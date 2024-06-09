import os
import sys
import ctypes
import winreg
import json
import subprocess
import time
import webbrowser
from colorama import init, Fore, Style

init()
RED = Fore.RED
GREEN = Fore.GREEN
BOLD = Style.BRIGHT
END = Style.RESET_ALL


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

run_as_admin()


def registry_path_exists(hive, path):
    try:
        winreg.OpenKey(getattr(winreg, hive), path)
        return True
    except FileNotFoundError:
        return False

def check_registry_key(key_path, value_name):
    try:
        result = subprocess.check_output(['reg', 'query', key_path, '/v', value_name], stderr=subprocess.STDOUT, universal_newlines=True)
        return value_name in result
    except subprocess.CalledProcessError:
        return False

def get_registry_value(key_path, value_name):
    try:
        result = subprocess.check_output(['reg', 'query', key_path, '/v', value_name], stderr=subprocess.STDOUT)
        result = result.decode('utf-8', errors='ignore')
        lines = result.split('\n')
        for line in lines:
            if value_name in line:
                return line.split()[-1]
    except subprocess.CalledProcessError:
        return None
    
def set_registry_value(key_path, value_name, value):
    subprocess.run(['reg', 'add', key_path, '/v', value_name, '/t', 'REG_DWORD', '/d', str(value), '/f'], check=True)

def is_chrome_installed():
    chrome_path = os.path.join(os.getenv('PROGRAMFILES'), 'Google', 'Chrome', 'Application', 'chrome.exe')
    return os.path.exists(chrome_path)

def registry_path_exists(hive, path):
    try:
        winreg.OpenKey(getattr(winreg, hive), path)
        return True
    except FileNotFoundError:
        return False

def is_steam_installed():
    steam_path_to_check = "Software\\Valve\\Steam"
    return registry_path_exists('HKEY_CURRENT_USER', steam_path_to_check)

def is_spotify_installed():
    spotify_path = os.path.join(os.getenv('APPDATA'), 'Spotify', 'Spotify.exe')
    return os.path.exists(spotify_path)

def is_edge_installed():
    global edge_user_data_dir
    edge_user_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data')
    return os.path.exists(edge_user_data_dir)

def is_gx_installed():
    global gx_user_data_dir
    gx_user_data_dir = os.path.join(os.getenv('APPDATA'), 'Opera Software', 'Opera GX Stable')
    return os.path.exists(gx_user_data_dir)

def is_brave_installed():
    brave_path = os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser')
    return os.path.exists(brave_path)

def is_firefox_installed():
    firefox_path = os.path.join(os.getenv('PROGRAMFILES'), 'Mozilla Firefox', 'firefox.exe')
    return os.path.exists(firefox_path)

def is_discord_installed():
    discord_path = os.path.join(os.getenv('APPDATA'), 'discord')
    return os.path.exists(discord_path)

def get_hardware_acceleration_status():
    status = {}
    if is_chrome_installed():
        chrome_status = get_registry_value('HKLM\\SOFTWARE\\Policies\\Google\\Chrome', 'HardwareAccelerationModeEnabled')
        status['Chrome'] = 'Enabled' if chrome_status == '0x1' else 'Disabled' if chrome_status == '0x0' else 'Unknown'

    if is_steam_installed():
        steam_status = get_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'GPUAccelWebViewsV3')
        status['Steam'] = 'Enabled' if steam_status == '0x1' else 'Disabled' if steam_status == '0x0' else 'Unknown'

    if is_spotify_installed():
        spotify_prefs_file = os.path.join(os.getenv('APPDATA'), 'Spotify', 'prefs')
        if os.path.exists(spotify_prefs_file):
            with open(spotify_prefs_file, 'r', encoding='utf-8') as file:
                content = file.read()
                status['Spotify'] = 'Disabled' if 'ui.hardware_acceleration=false' in content else 'Enabled'

    if is_edge_installed():
        edge_cfg_path = os.path.join(edge_user_data_dir, 'Local State')
        if os.path.exists(edge_cfg_path):
            with open(edge_cfg_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                status['Edge'] = 'Enabled' if data.get('hardware_acceleration_mode', {}).get('enabled') else 'Disabled'

    if is_gx_installed():
        gx_cfg_path = os.path.join(gx_user_data_dir, 'Local State')
        if os.path.exists(gx_cfg_path):
            with open(gx_cfg_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                status['Opera GX'] = 'Enabled' if data.get('hardware_acceleration_mode') else 'Disabled'

    if is_brave_installed():
        brave_file_path = os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Local State')
        if os.path.exists(brave_file_path):
            with open(brave_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                status['Brave'] = 'Enabled' if data.get("hardware_acceleration_mode", {}).get("enabled") else 'Disabled'

    if is_firefox_installed():
        firefox_pref_loc = os.path.join(os.getenv('APPDATA'),'Mozilla', 'Firefox', 'Profiles')
        for profile_name in os.listdir(firefox_pref_loc):
            if profile_name.endswith('default-release'):
                profile_path = os.path.join(firefox_pref_loc, profile_name)
                prefs_file = os.path.join(profile_path, 'prefs.js')
                if os.path.exists(prefs_file):
                    with open(prefs_file, 'r', encoding='utf-8') as file:
                        content = file.read()
                        status['Firefox'] = 'Disabled' if 'user_pref("layers.acceleration.disabled", true);' in content else 'Enabled'

    if is_discord_installed():
        discord_cfg_path = os.path.join(os.getenv('APPDATA'), 'discord', 'settings.json')
        if os.path.exists(discord_cfg_path):
            with open(discord_cfg_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                status['Discord'] = 'Enabled' if data.get('enableHardwareAcceleration') else 'Disabled'

    return status

def remove_hardware_acceleration_prefs(profile_path):
    prefs_file = os.path.join(profile_path, 'prefs.js')
    if os.path.exists(prefs_file):
        with open(prefs_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open(prefs_file, 'w', encoding='utf-8') as file:
            for line in lines:
                if not line.strip().startswith('user_pref("layers.acceleration.disabled"'):
                    file.write(line)

def print_hardware_acceleration_status(status):
    print(f"{BOLD}Hardware Acceleration Status:{END}")
    for program, acceleration_status in status.items():
        if acceleration_status == 'Enabled':
            print(f"{program}: {GREEN}{acceleration_status}{END}")
        elif acceleration_status == 'Disabled':
            print(f"{program}: {RED}{acceleration_status}{END}")
        else:
            print(f"{program}: {acceleration_status}")
banner = f"""
{Fore.MAGENTA}
██   ██  █████       ██████ ██   ██ ███████  ██████ ██   ██ ███████ ██████  
██   ██ ██   ██     ██      ██   ██ ██      ██      ██  ██  ██      ██   ██ 
███████ ███████     ██      ███████ █████   ██      █████   █████   ██████  
██   ██ ██   ██     ██      ██   ██ ██      ██      ██  ██  ██      ██   ██ 
██   ██ ██   ██      ██████ ██   ██ ███████  ██████ ██   ██ ███████ ██   ██
{Style.RESET_ALL}
"""
def reset_and_check_status():
    os.system('cls' if os.name == 'nt' else 'clear')  # Bildschirm löschen
    print(banner)
    hardware_acceleration_status = get_hardware_acceleration_status()  # Aktuellen Status abrufen
    print_hardware_acceleration_status(hardware_acceleration_status)  # Aktuellen Status ausgeben


print(banner)
hardware_acceleration_status = get_hardware_acceleration_status()
print_hardware_acceleration_status(hardware_acceleration_status)

def success_print():
        time.sleep(1)
        reset_and_check_status()
        print("")
        print(f"{GREEN}Everything has been configured, you may close this window now")
        print(f"{GREEN}Good Luck and Have fun :)")
        webbrowser.open('https://twitter.com/PxrmaFX')
        webbrowser.open('https://twitter.com/frequencycs')
        input("")




def disable_hardware_acceleration_for_all_programs(enable):
    action = 'Enabled' if enable else 'Disabled'
    try:
        if is_chrome_installed():
            set_registry_value('HKLM\\SOFTWARE\\Policies\\Google\\Chrome', 'HardwareAccelerationModeEnabled', 1 if enable else 0)
            print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Chrome.{END}")
        if is_steam_installed():
            set_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'H264HWAccel', 1 if enable else 0)
            set_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'GPUAccelWebViewsV3', 1 if enable else 0)
            print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Steam.{END}")

# Spotify
        if is_spotify_installed():
            spotify_prefs_file = os.path.join(os.getenv('APPDATA'), 'Spotify', 'prefs')
            try:
                with open(spotify_prefs_file, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                with open(spotify_prefs_file, 'w', encoding='utf-8') as file:
                    if enable:
                        lines = [line for line in lines if "ui.hardware_acceleration=false" not in line]
                    else:
                        if not any("ui.hardware_acceleration=false" in line for line in lines):
                            lines.append("ui.hardware_acceleration=false\n")
                    file.writelines(lines)
                print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Spotify.{END}")
            except FileNotFoundError:
                print(f"{RED}Spotify preferences file not found.{END}")

# Brave
        if is_brave_installed():
            brave_file_path = os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Local State')
            try:
                with open(brave_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                data["hardware_acceleration_mode"]["enabled"] = enable
                with open(brave_file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4)
                print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Brave.{END}")
            except (FileNotFoundError, json.JSONDecodeError):
                print(f"{RED}Brave preferences file not found or invalid.{END}")

# Firefox
        if is_firefox_installed():
            firefox_pref_loc = os.path.join(os.getenv('APPDATA'),'Mozilla', 'Firefox', 'Profiles')
            profile_found = False
            for profile_name in os.listdir(firefox_pref_loc):
                if profile_name.endswith('default-release'):
                    profile_path = os.path.join(firefox_pref_loc, profile_name)
                    profile_found = True
                    break
            if profile_found:
                prefs_file = os.path.join(profile_path, 'prefs.js')
                if os.path.exists(prefs_file):
                    with open(prefs_file, 'a', encoding='utf-8') as file:
                        remove_hardware_acceleration_prefs(profile_path)
                        file.write(f'user_pref("layers.acceleration.disabled", {"false" if enable else "true"});\n')
                    print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Firefox.{END}")
                else:
                    print(f"{RED}Firefox preference file not found.{END}")
            else:
                print(f"{RED}Firefox profile not found.{END}")

# Discord
        if is_discord_installed():
            discord_cfg_path = os.path.join(os.getenv('APPDATA'), 'discord', 'settings.json')
            if os.path.exists(discord_cfg_path):
                try:
                    with open(discord_cfg_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    data['enableHardwareAcceleration'] = enable
                    with open(discord_cfg_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4)
                    print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Discord.{END}")
                except (FileNotFoundError, json.JSONDecodeError):
                    print(f"{RED}Discord preferences file not found or invalid.{END}")

# Edge
        if is_edge_installed():
            edge_cfg_path = os.path.join(edge_user_data_dir, 'Local State')
            if os.path.exists(edge_cfg_path):
                try:
                    with open(edge_cfg_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    data['hardware_acceleration_mode'] = {'enabled': enable}
                    with open(edge_cfg_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4)
                    print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Edge.{END}")
                except (FileNotFoundError, json.JSONDecodeError):
                    print(f"{RED}Edge preferences file not found or invalid.{END}")

# Opera GX
        if is_gx_installed():
            gx_cfg_path = os.path.join(gx_user_data_dir, 'Local State')
            if os.path.exists(gx_cfg_path):
                try:
                    with open(gx_cfg_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    data['hardware_acceleration_mode'] = enable
                    with open(gx_cfg_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4)
                    print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Opera GX.{END}")
                    success_print()
                except (FileNotFoundError, json.JSONDecodeError):
                    print(f"{RED}Opera GX preferences file not found or invalid.{END}")
    except Exception as e:
        print(f"{RED}An error occurred: {e}{END}")


def ask_all_or_individual():
    while True:
        print("")
        print("Do you want to change hardware acceleration settings for all programs or individually?")
        print("1. All programs")
        print("2. Individually")
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == '1' or choice == '2':
            return choice
        else:
            reset_and_check_status()
            print("")
            print(f"{RED}Invalid choice. Please enter 1 or 2.{END}")

def main():
    choice = ask_all_or_individual()
    reset_and_check_status()
    last_query_success = False
    if choice == '1':
        print("")
        while True:
            enable_input = input(f"Do you want to enable or disable hardware acceleration? ({GREEN}1{END} for Enable, {RED}2{END} for Disable): ").strip()
            if enable_input == '1':
                enable = True
                break
            elif enable_input == '2':
                enable = False
                break
            else:
                print(f"{RED}Invalid input. Please enter 1 or 2.{END}")
        disable_hardware_acceleration_for_all_programs(enable)
        last_query_success = True  
        success_print()
    elif choice == '2':
        programs = [
            ("Chrome", is_chrome_installed),
            ("Steam", is_steam_installed),
            ("Spotify", is_spotify_installed),
            ("Brave", is_brave_installed),
            ("Firefox", is_firefox_installed),
            ("Discord", is_discord_installed),
            ("Edge", is_edge_installed),
            ("Opera GX", is_gx_installed)
        ]
        for program, is_installed_func in programs:
            if is_installed_func():
                reset_and_check_status()
                print("")
                while True:
                    enable_input = input(f"Do you want to disable Hardware Acceleration for {BOLD}{program}{Style.RESET_ALL}? ({GREEN}1{END} for Enable, {RED}2{END} for Disable): ").strip()
                    if enable_input == '1':
                        enable = True
                        break
                    elif enable_input == '2':
                        enable = False
                        break
                    else:
                        reset_and_check_status()
                        print("")
                        print(f"{RED}Invalid input. Please enter 1 or 2.{END}")
                disable_hardware_acceleration_for_program(program, enable)
                last_query_success = True  
        if last_query_success:
            reset_and_check_status()
            success_print()
    else:
        reset_and_check_status()
        print("")
        print(f"{RED}Invalid choice. Please enter 1 or 2.{END}")

# Chrome        
def disable_hardware_acceleration_for_program(program_name, enable):
    action = 'Enabled' if enable else 'Disabled'
    try:
        if program_name == "Chrome":
            set_registry_value('HKLM\\SOFTWARE\\Policies\\Google\\Chrome', 'HardwareAccelerationModeEnabled', 1 if enable else 0)
            print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Chrome.{END}")
        elif program_name == "Steam":
            set_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'H264HWAccel', 1 if enable else 0)
            set_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'GPUAccelWebViewsV3', 1 if enable else 0)
            print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Steam.{END}")


# Spotify            
        elif program_name == "Spotify":
            spotify_prefs_file = os.path.join(os.getenv('APPDATA'), 'Spotify', 'prefs')
            try:
                with open(spotify_prefs_file, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                with open(spotify_prefs_file, 'w', encoding='utf-8') as file:
                    if enable:
                        lines = [line for line in lines if "ui.hardware_acceleration=false" not in line]
                    else:
                        if not any("ui.hardware_acceleration=false" in line for line in lines):
                            lines.append("ui.hardware_acceleration=false\n")
                    file.writelines(lines)
                print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Spotify.{END}")
            except FileNotFoundError:
                print(f"{RED}Spotify preferences file not found.{END}")



# Brave
        elif program_name == "Brave":
            brave_file_path = os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Local State')
            try:
                with open(brave_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                data["hardware_acceleration_mode"]["enabled"] = enable
                with open(brave_file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4)
                print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Brave.{END}")
            except (FileNotFoundError, json.JSONDecodeError):
                print(f"{RED}Brave preferences file not found or invalid.{END}")



# Firefox
        elif program_name == "Firefox":
            firefox_pref_loc = os.path.join(os.getenv('APPDATA'),'Mozilla', 'Firefox', 'Profiles')
            profile_found = False
            for profile_name in os.listdir(firefox_pref_loc):
                if profile_name.endswith('default-release'):
                    profile_path = os.path.join(firefox_pref_loc, profile_name)
                    profile_found = True
                    break
            if profile_found:
                prefs_file = os.path.join(profile_path, 'prefs.js')
                if os.path.exists(prefs_file):
                    with open(prefs_file, 'a', encoding='utf-8') as file:
                        remove_hardware_acceleration_prefs(profile_path)
                        file.write(f'user_pref("layers.acceleration.disabled", {"false" if enable else "true"});\n')
                    print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Firefox.{END}")
                else:
                    print(f"{RED}Firefox preference file not found.{END}")
            else:
                print(f"{RED}Firefox profile not found.{END}")


# Discord                
        elif program_name == "Discord":
            discord_cfg_path = os.path.join(os.getenv('APPDATA'), 'discord', 'settings.json')
            if os.path.exists(discord_cfg_path):
                try:
                    with open(discord_cfg_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    data['enableHardwareAcceleration'] = enable
                    with open(discord_cfg_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4)
                    print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Discord.{END}")
                except (FileNotFoundError, json.JSONDecodeError):
                    print(f"{RED}Discord preferences file not found or invalid.{END}")


# Edge                    
        elif program_name == "Edge":
            edge_cfg_path = os.path.join(edge_user_data_dir, 'Local State')
            if os.path.exists(edge_cfg_path):
                try:
                    with open(edge_cfg_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    data['hardware_acceleration_mode'] = {'enabled': enable}
                    with open(edge_cfg_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4)
                    print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Edge.{END}")
                except (FileNotFoundError, json.JSONDecodeError):
                    print(f"{RED}Edge preferences file not found or invalid.{END}")


# Opera GX                    
        elif program_name == "Opera GX":
            gx_cfg_path = os.path.join(gx_user_data_dir, 'Local State')
            if os.path.exists(gx_cfg_path):
                try:
                    with open(gx_cfg_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    data['hardware_acceleration_mode'] = enable
                    with open(gx_cfg_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4)
                    print(f"{GREEN if enable else RED}{action} Hardware Acceleration for Opera GX.{END}")   
                except (FileNotFoundError, json.JSONDecodeError):
                    print(f"{RED}Opera GX preferences file not found or invalid.{END}")
        else:
            print(f"{RED}Program '{program_name}' is not supported for hardware acceleration configuration.{END}")
            
        
    except Exception as e:
        print(f"{RED}An error occurred: {e}{END}")
        time.sleep(10)
        
if __name__ == "__main__":
    main()
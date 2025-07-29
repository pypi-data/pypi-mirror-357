import sys
import os
import json
import shutil

def get_windows_terminal_settings_path():
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        settings_path = os.path.join(local_app_data, "Packages", 
                                     "Microsoft.WindowsTerminal_8wekyb3d8bbwe", 
                                     "LocalState", "settings.json")
        return settings_path
    else:
        return None

def add_git_bash_to_terminal(settings_path):
    if os.path.exists(settings_path):
        # Read the current settings.json file
        with open(settings_path, 'r', encoding='utf-8') as file:
            settings = json.load(file)
        
        # Define the Git Bash profile to add
        git_bash_profile = {
            "guid": "{d99be700-e39f-5380-bbbd-4a7b6ef76e9e}",
            "name": "Git Bash",
            "commandline": "C:\\Program Files\\Git\\bin\\bash.exe -i -l",
            "icon": "C:\\Program Files\\Git\\mingw64\\share\\git\\git-for-windows.ico",
            "hidden": False,
            "startingDirectory": "%USERPROFILE%"
        }
        
        # Check if the Git Bash profile already exists by its name
        profile_exists = False
        if 'profiles' in settings and 'list' in settings['profiles']:
            for profile in settings['profiles']['list']:
                if profile.get("name") == "Git Bash":
                    profile_exists = True
                    break

        # If the profile doesn't exist, add it
        if not profile_exists:
            settings['profiles']['list'].append(git_bash_profile)
            
            # Write the updated settings back to settings.json
            with open(settings_path, 'w', encoding='utf-8') as file:
                json.dump(settings, file, indent=4)
            
            settings['defaultProfile'] = git_bash_profile["guid"]

            print("Git Bash profile has been added to Windows Terminal settings.")
        else:
            print("Git Bash profile already exists.")
    else:
        print(f"settings.json not found at {settings_path}.")

def add_git_bash_vs2022_to_terminal(settings_path):
    if os.path.exists(settings_path):
        # Read the current settings.json file
        with open(settings_path, 'r', encoding='utf-8') as file:
            settings = json.load(file)
        
        # Define the Git Bash profile to add
        git_bash_profile = {
            "guid": "{4e86fa87-bee2-4f95-b161-3366ab2fbde3}",
            "name": "Git Bash VS 2022",
            "commandline": "C:\\Program Files\\Git\\bin\\git-bash_vs2022.cmd",
            "icon": "C:\\Program Files\\Git\\mingw64\\share\\git\\git-for-windows.ico",
            "hidden": False,
            "startingDirectory": "%USERPROFILE%"
        }
        
        # Check if the Git Bash profile already exists by its name
        profile_exists = False
        if 'profiles' in settings and 'list' in settings['profiles']:
            for profile in settings['profiles']['list']:
                if profile.get("name") == "Git Bash VS 2022":
                    profile_exists = True
                    break

        # If the profile doesn't exist, add it
        if not profile_exists:
            settings['profiles']['list'].append(git_bash_profile)
            
            # Write the updated settings back to settings.json
            with open(settings_path, 'w', encoding='utf-8') as file:
                json.dump(settings, file, indent=4)
            
            # settings['defaultProfile'] = git_bash_profile["guid"]

            print("Git Bash VS 2022 profile has been added to Windows Terminal settings.")
        else:
            print("Git Bash VS 2022 profile already exists.")
    else:
        print(f"settings.json not found at {settings_path}.")

def add_elevate_default(settings_path):
    if os.path.exists(settings_path):
        # Read the current settings.json file
        with open(settings_path, 'r', encoding='utf-8') as file:
            settings = json.load(file)
        
        # Check if "defaults" exists in the profiles section
        if 'profiles' in settings:
            if 'defaults' not in settings['profiles']:
                # Add the "defaults": { "elevate": true } block if it does not exist
                settings['profiles']['defaults'] = {
                    "elevate": True
                }
                print('Added "defaults": { "elevate": true } to settings.json.')
            else:
                # Check if the "elevate" field exists and is set to True
                if settings['profiles']['defaults'].get('elevate', False) is not True:
                    settings['profiles']['defaults']['elevate'] = True
                    print('Updated "elevate" to true in the defaults section.')
                else:
                    print('"elevate" is already set to true.')
            
            # Write the updated settings back to settings.json
            with open(settings_path, 'w', encoding='utf-8') as file:
                json.dump(settings, file, indent=4)

        else:
            print('"profiles" section not found in settings.json.')
    else:
        print(f"settings.json not found at {settings_path}.")

def add_git_bash_vs2022_to_terminal_start(settings_path):
    base_path = os.path.dirname(__file__)
    bashcmd_path = os.path.join(base_path, 'git-bash_vs2022.cmd')

    if not os.path.exists(bashcmd_path):
        print(f"git-bash_vs2022.cmd not found at {bashcmd_path}")
        sys.exit(6)

    shutil.copyfile(bashcmd_path, "C:\\Program Files\\Git\\bin\\git-bash_vs2022.cmd")
    add_git_bash_vs2022_to_terminal(settings_path)
    pass

def setup_wt_git_bash():
    settings_path = get_windows_terminal_settings_path()
    if settings_path and os.path.exists(settings_path):
        print(f"Windows Terminal settings.json is located at: {settings_path}")
        add_git_bash_to_terminal(settings_path)
    else:
        print("Windows Terminal settings.json not found.")

def setup_wt_git_bash_vs():
    settings_path = get_windows_terminal_settings_path()
    if settings_path and os.path.exists(settings_path):
        print(f"Windows Terminal settings.json is located at: {settings_path}")
        add_git_bash_vs2022_to_terminal_start(settings_path)
    else:
        print("Windows Terminal settings.json not found.")
    
def setup_wt_admin():
    settings_path = get_windows_terminal_settings_path()
    if settings_path and os.path.exists(settings_path):
        print(f"Windows Terminal settings.json is located at: {settings_path}")
        add_elevate_default(settings_path)
    else:
        print("Windows Terminal settings.json not found.")
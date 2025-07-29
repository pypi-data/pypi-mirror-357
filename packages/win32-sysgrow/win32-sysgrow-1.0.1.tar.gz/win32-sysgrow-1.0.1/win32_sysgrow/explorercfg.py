import os
import winreg as reg

def disable_hide_extensions():
    # The registry key for "Hide extensions for known file types"
    registry_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced"
    
    try:
        # Open the registry key
        reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, registry_key, 0, reg.KEY_SET_VALUE)
        
        # Set the "HideFileExt" value to 0 (disable hiding extensions)
        reg.SetValueEx(reg_key, "HideFileExt", 0, reg.REG_DWORD, 0)
        
        # Close the registry key
        reg.CloseKey(reg_key)
        
        print("Successfully disabled 'Hide extensions for known file types'.")
        
    except Exception as e:
        print(f"Failed to modify registry: {e}")


def enable_show_hidden_files():
    # The registry key for showing hidden files, folders, and drives
    registry_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced"
    
    try:
        # Open the registry key with permission to modify it
        reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, registry_key, 0, reg.KEY_SET_VALUE)
        
        # Set the "Hidden" value to 1 (enable showing hidden files)
        reg.SetValueEx(reg_key, "Hidden", 0, reg.REG_DWORD, 1)
        
        # Close the registry key
        reg.CloseKey(reg_key)
        
        print("Successfully enabled 'Show hidden files, folders, and drives'.")
        
    except Exception as e:
        print(f"Failed to modify registry: {e}")

def restart_explorer():
    os.system("taskkill /f /im explorer.exe")
    os.system("start explorer.exe")
    
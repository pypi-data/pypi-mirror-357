import os
import sys
import shutil
import subprocess

from win32_sysgrow.sysenv import *

def check_choco_installed():
    try:
        subprocess.run(["choco", "--version"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_choco():
    folder_path = r"C:\ProgramData\chocolatey" 
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except Exception as e:
            print(f"Folder deletion error: {e}")

    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        "iex (New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')"
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        os.system("taskkill /f /im explorer.exe && start explorer.exe")
        return True
    except subprocess.CalledProcessError as e:
        print("Error while installing Chocolatey")
        print("Error code:", e.returncode)
        print("Error:\n", e.stderr)
        return False
    except Exception as ex:
        print("Unexpected error:", ex)
        return False
    
def ensure_choco():
    if not check_choco_installed():
        if find_executable_in_registry_path('choco') != None:
            print('Console restart required to run choco')
            sys.exit(2)

        if not install_choco():
            print('Failed to install choco')
            sys.exit(3)

        print('Console restart required to run choco')
        sys.exit(2)
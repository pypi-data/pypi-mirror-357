import sys
import subprocess

from win32_sysgrow.sysenv import *

def check_winget_installed():
    try:
        subprocess.run(["winget", "--version"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def ensure_winget():

    if not check_winget_installed():
        if find_executable_in_registry_path('winget') != None:
            print('Console restart required to run winget')
            sys.exit(2)

        print('winget installation is required. Try to install from "https://github.com/microsoft/winget-cli/releases/download/v1.9.25180/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"')
        sys.exit(2)

    
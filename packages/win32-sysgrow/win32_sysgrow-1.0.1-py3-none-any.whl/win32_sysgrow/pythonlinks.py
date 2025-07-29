import os
import subprocess

def make_python3_links():
    local_appdata = os.getenv('LOCALAPPDATA')
    if not local_appdata:
        print("Error: LOCALAPPDATA environment variable is not set.")
        return

    python_root = os.path.join(local_appdata, "Programs", "Python")
    if not os.path.exists(python_root):
        print(f"Python root folder does not exist: {python_root}")
        return

    python_versions = [d for d in os.listdir(python_root) if os.path.isdir(os.path.join(python_root, d))]
    if not python_versions:
        print("No Python versions found in", python_root)
        return

    for version in python_versions:
        python_exe = os.path.join(python_root, version, "python.exe")
        python3_exe = os.path.join(python_root, version, "python3.exe")

        if os.path.exists(python_exe) and not os.path.exists(python3_exe):
            try:
                subprocess.run(
                    ["cmd", "/c", "mklink", python3_exe, python_exe],
                    check=True,
                    shell=True
                )
                print(f"Created symlink: {python3_exe} -> {python_exe}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to create symlink for {version}: {e}")
        else:
            if not os.path.exists(python_exe):
                print(f"Missing python.exe for {version}, skipping")
            else:
                print(f"Symlink already exists for {version}, skipping")

def remove_windowsapps_python_redirects():
    os.system('powershell Remove-Item $env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe >nul')
    os.system('powershell Remove-Item $env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe >nul')


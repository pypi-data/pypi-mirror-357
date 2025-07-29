import sys
import os
import argparse

from win32_sysgrow.nvidia import *
from win32_sysgrow.sysenv import *
from win32_sysgrow.choco import *
from win32_sysgrow.winget import *
from win32_sysgrow.explorercfg import *
from win32_sysgrow.powercfg import *
from win32_sysgrow.vsinstall import *
from win32_sysgrow.pythonlinks import *
from win32_sysgrow.windowsterminal import *

def load_vscode_extensions():
    vscode_path = find_executable_in_registry_path("code")
    if not vscode_path:
        print("Something was wrong while vscode installation")
        sys.exit(5)

    vscode_path = '"' + vscode_path + '"'

    os.system(f"{vscode_path} --install-extension ms-python.python")
    os.system(f"{vscode_path} --install-extension ms-vscode.cpptools-extension-pack")
    os.system(f"{vscode_path} --install-extension llvm-vs-code-extensions.vscode-clangd")

def setup_coding_tools():
    ensure_choco()

    os.system('choco install llvm -y')
    os.system('choco install cmake -y')
    os.system('choco install nodejs -y')
    os.system('choco install git -y')
    os.system('choco install vscode -y')

    load_vscode_extensions()

def setup_mullvad():
    ensure_winget()
    os.system('winget install --id=MullvadVPN.MullvadVPN --version=2025.5 -e')

def setup_wireguard():
    ensure_winget()
    os.system('winget install "WireGuard.WireGuard"')

def setup_winrar():
    ensure_winget()
    os.system('winget install "WinRAR"')

def setup_windowsterminal():
    ensure_winget()
    os.system('winget install "Microsoft.WindowsTerminal"')

def setup_tools():
    ensure_winget()

    os.system('winget install "WinRAR"')
    os.system('winget install "Microsoft.WindowsTerminal"')

TASKS_INFO = {
    'wireguard': 'Install WireGuard VPN',
    'mullvad': 'Install Mullvad VPN',
    'nvidia': 'Setup Nvidia drivers',
    'tools': 'Install WinRAR and Windows Terminal',
    'codetools': 'Install LLVM, CMake, Node.js, Git, VSCode',
    'powercfg': 'Disable sleep, screen turning off, and hibernation',
    'explorercfg': 'Configure Explorer (show hidden files, extensions)',
    'visualstudio': 'Install Visual Studio',
    'pythonlinks': 'Fix Python links, ensure python3 link exists, remove MS Store redirection',
    'firefox': 'Install Firefox browser',
    'wtprofile': 'Set Windows Terminal to start as administrator, add Git Bash and VS2022 Git Bash profiles',
    'wtadmin': 'Set Windows Terminal to start as administrator',
    'wtgitbash': 'Add Git Bash profile to Windows Terminal',
    'wtgitbash_vs': 'Add VS2022 Git Bash profile',
}

def print_tasks_help():
    print("\nAvailable tasks:")
    for task, desc in TASKS_INFO.items():
        print(f"  {task:<12} - {desc}")

    print(f"\nExample: sysgrow tools codetools powercfg explorercfg")
    sys.exit(0)

def parse_args():
    parser = argparse.ArgumentParser(description="Run selected setup tasks")
    parser.add_argument('tasks', nargs='*',
                        help="Tasks to run. Use --list-tasks to see descriptions.")
    # parser.add_argument('--list-tasks', action='store_true', help="Show list of tasks with descriptions and exit")
    args = parser.parse_args()

    if not args.tasks:
        parser.print_help()
        print_tasks_help()
        sys.exit(0)

    # Проверка на валидность задач
    invalid = [task for task in args.tasks if task not in TASKS_INFO]
    if invalid:
        print(f"Error: invalid task(s): {', '.join(invalid)}")
        print("Available tasks:")
        for task in TASKS_INFO:
            print(f"  {task}")
        sys.exit(1)

    return args

def main():
    if sys.version_info < (3, 0):
        print("Python 3 or higher is required.")
        sys.exit(1)

    args = parse_args()

    if 'wireguard' in args.tasks:
        setup_wireguard()

    if 'mullvad' in args.tasks:
        setup_mullvad()

    if 'nvidia' in args.tasks:
        setup_nvidia()

    if 'tools' in args.tasks:
        setup_tools()

    if 'codetools' in args.tasks:
        setup_coding_tools()

    if 'powercfg' in args.tasks:
        disable_sleep_and_screen_turn_off()

    if 'explorercfg' in args.tasks:
        disable_hide_extensions()
        enable_show_hidden_files()
        restart_explorer()

    if 'visualstudio' in args.tasks:
        setup_visualstudio()

    if 'pythonlinks' in args.tasks:
        remove_windowsapps_python_redirects()
        make_python3_links()

    if 'firefox' in args.tasks:
        os.system('choco install firefox -y')

    if 'wtprofile' in args.tasks:
        setup_wt_git_bash()
        setup_wt_git_bash_vs()
        setup_wt_admin()

    if 'wtadmin' in args.tasks:
        setup_wt_admin()

    if 'wtgitbash' in args.tasks:
        setup_wt_git_bash()

    if 'wtgitbash_vs' in args.tasks:
        setup_wt_git_bash_vs()

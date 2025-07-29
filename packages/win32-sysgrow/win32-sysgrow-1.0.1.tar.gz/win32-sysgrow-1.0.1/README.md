# win32-sysgrow

**win32-sysgrow** is a Python toolkit for automating the installation and configuration of various useful software and system settings on Windows.  
It helps quickly provision a Windows environment by installing drivers, VPN clients, utilities, development tools, and tweaking system parameters.

---

## Features

- Install and configure VPN clients (WireGuard, Mullvad)
- Setup Nvidia drivers
- Install essential tools (WinRAR, Windows Terminal)
- Install development tools (LLVM, CMake, Node.js, Git, VSCode)
- Disable sleep, hibernation, and screen turning off
- Configure File Explorer (show hidden files and file extensions)
- Install and configure Visual Studio
- Fix Python links and remove Microsoft Store redirections
- Install Firefox browser via Chocolatey
- Configure Windows Terminal:
  - Start as administrator
  - Add Git Bash profile
  - Add VS2022 Git Bash profile

---

## Requirements

- Python 3.x
- Windows with package managers [Chocolatey](https://chocolatey.org/) and/or [Winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)
- Administrator privileges for software installation and system changes

**Note:** If Chocolatey is missing, the script will attempt to install it automatically.

---

## Installation and Usage

1. Install package with following command:

```bash
python -m pip install win32-sysgrow
```

2. Run the script from the command line, specifying one or more tasks to execute:

```bash
sysgrow [tasks ...]
```

| Task          | Description                                                                               |
| ------------- | ----------------------------------------------------------------------------------------- |
| wireguard     | Install WireGuard VPN                                                                     |
| mullvad       | Install Mullvad VPN                                                                       |
| nvidia        | Setup Nvidia drivers                                                                      |
| tools         | Install WinRAR and Windows Terminal                                                       |
| codetools     | Install LLVM, CMake, Node.js, Git, and VSCode                                             |
| powercfg      | Disable sleep, screen turning off, and hibernation                                        |
| explorercfg   | Configure Explorer (show hidden files and file extensions)                                |
| visualstudio  | Install Visual Studio                                                                     |
| pythonlinks   | Fix Python links, ensure python3 link exists, remove Microsoft Store redirection          |
| firefox       | Install Firefox browser                                                                   |
| wtprofile     | Set Windows Terminal to start as administrator, add Git Bash and VS2022 Git Bash profiles |
| wtadmin       | Set Windows Terminal to start as administrator                                            |
| wtgitbash     | Add Git Bash profile to Windows Terminal                                                  |
| wtgitbash\_vs | Add VS2022 Git Bash profile                                                               |


## Help Output Example

When running the script without arguments or with -h, you'll see the following help message:

```
usage: sysgrow [-h] [tasks ...]

Run selected setup tasks

positional arguments:
  tasks       Tasks to run.

options:
  -h, --help  show this help message and exit

Available tasks:
  wireguard    - Install WireGuard VPN
  mullvad      - Install Mullvad VPN
  nvidia       - Setup Nvidia drivers
  tools        - Install WinRAR and Windows Terminal
  codetools    - Install LLVM, CMake, Node.js, Git, VSCode
  powercfg     - Disable sleep, screen turning off, and hibernation
  explorercfg  - Configure Explorer (show hidden files, extensions)
  visualstudio - Install Visual Studio
  pythonlinks  - Fix Python links, ensure python3 link exists, remove MS Store redirection
  firefox      - Install Firefox browser
  wtprofile    - Set Windows Terminal to start as administrator, add Git Bash and VS2022 Git Bash profiles
  wtadmin      - Set Windows Terminal to start as administrator
  wtgitbash    - Add Git Bash profile to Windows Terminal
  wtgitbash_vs - Add VS2022 Git Bash profile

Example: sysgrow tools codetools powercfg explorercfg
```

## Notes

- Run the script with administrator privileges to allow installation and system configuration.
- Review the tasks you run to understand the changes applied to your system.
- The script supports both Chocolatey and Winget package managers.
- If Chocolatey is not installed, the script will try to install it automatically.


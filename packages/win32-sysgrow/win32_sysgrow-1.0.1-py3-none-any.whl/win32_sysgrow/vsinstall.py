import os
import subprocess

from win32_sysgrow.sysenv import *
from win32_sysgrow.winget import *

def get_vs_using_vswhere():
    try:
        base_path = os.path.dirname(__file__)
        vswhere_path = os.path.join(base_path, 'vswhere.exe')

        if not os.path.exists(vswhere_path):
            print(f"vswhere.exe not found at {vswhere_path}")
            return None

        # Run 'vswhere' to find Visual Studio installation paths
        result = subprocess.run([vswhere_path, "-latest", "-property", "installationPath"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def after_vs_install():
    vs_path = get_vs_using_vswhere()
    if not vs_path:
        print("Visual Studio installation not found using vswhere.")
        return

    need_restart = add_env_path(vs_path + "\\Common7\\Tools")
    if need_restart:
        os.system("taskkill /f /im explorer.exe && start explorer.exe")


def setup_visualstudio():
    ensure_winget()

    os.system('winget install "Microsoft.VisualStudio.2022.Community"')

    cmd = [
        r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vs_installer.exe",
        "install",
        "--productId", "Microsoft.VisualStudio.Product.Community",
        "--add", "Microsoft.Component.MSBuild",
        "--add", "Microsoft.VisualStudio.Component.VC.CoreIde",
        "--add", "Microsoft.VisualStudio.Component.VC.Redist.14.Latest",
        "--add", "Microsoft.VisualStudio.ComponentGroup.NativeDesktop.Core",
        "--add", "Microsoft.VisualStudio.Component.CppBuildInsights",
        "--add", "Microsoft.VisualStudio.Component.Debugger.JustInTime",
        "--add", "Microsoft.VisualStudio.Component.Graphics.Tools",
        "--add", "Microsoft.VisualStudio.Component.IntelliCode",
        "--add", "Microsoft.VisualStudio.Component.NuGet",
        "--add", "Microsoft.VisualStudio.Component.Roslyn.LanguageServices",
        "--add", "Microsoft.VisualStudio.Component.VC.ATL",
        "--add", "Microsoft.VisualStudio.Component.WindowsAppSdkSupport.Cpp",
        "--add", "Microsoft.VisualStudio.Component.VC.DiagnosticTools",
        "--add", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
        "--add", "Microsoft.VisualStudio.Component.Windows11SDK.22621",
        "--add", "Microsoft.VisualStudio.Component.Windows11Sdk.WindowsPerformanceToolkit",
        "--add", "Microsoft.VisualStudio.Component.VC.Modules.x86.x64",
        "--add", "Microsoft.VisualStudio.Component.Windows10SDK.20348",
        "--add", "Microsoft.VisualStudio.Component.Windows10SDK.19041",
        "--add", "Microsoft.VisualStudio.ComponentGroup.VC.Tools.142.x86.x64",
        "--add", "Microsoft.VisualStudio.Component.Windows10SDK",
        "--channelId", "VisualStudio.17.Release",
        "--norestart",
        "--passive"
    ]

    result = subprocess.run(cmd
                            # , capture_output=True, text=True
                            )

    # print("stdout:")
    # print(result.stdout)
    # print("stderr:")
    # print(result.stderr)

    if result.returncode == 0:
        after_vs_install()
        print("Successfully Visual Studio installed")
        return True
    else:
        print(f"Error while vsinstaller: {result.returncode}")
        return False



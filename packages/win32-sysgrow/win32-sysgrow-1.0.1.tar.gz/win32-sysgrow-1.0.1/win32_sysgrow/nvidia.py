import subprocess
import os
import shutil

from win32_sysgrow.choco import *

def is_process_in_path(process_name):
    # Check if the executable is in the system's PATH
    return shutil.which(process_name) is not None

def check_nvidia_gpu():
    try:
        result = subprocess.run(["wmic", "path", "win32_videocontroller", "get", "caption"], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            gpus = result.stdout.splitlines()
            gpus = [gpu.strip() for gpu in gpus if gpu.strip()]
            
            for gpu in gpus:
                if "NVIDIA" in gpu:
                    print(f"NVIDIA GPU detected: {gpu}")
                    return True

            print("No NVIDIA GPU detected.")
            return False
        else:
            print("Failed to query video controllers.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def setup_nvidia():
    if is_process_in_path("nvidia-smi"):
        print("nvidia-display-driver already installed")
        return

    if check_nvidia_gpu():
        ensure_choco()
        os.system('choco install "nvidia-display-driver" -y')
import subprocess

def disable_sleep_and_screen_turn_off():
    try:
        # Disable sleep (standby) when plugged in and on battery
        subprocess.run("powercfg -change standby-timeout-ac 0", check=True, shell=True)
        subprocess.run("powercfg -change standby-timeout-dc 0", check=True, shell=True)
        
        # Disable screen turn off (display timeout) when plugged in and on battery
        subprocess.run("powercfg -change monitor-timeout-ac 0", check=True, shell=True)
        subprocess.run("powercfg -change monitor-timeout-dc 0", check=True, shell=True)
        
        # Disable hibernation (optional)
        subprocess.run("powercfg -h off", check=True, shell=True)
        
        print("Sleep, screen turn off, and hibernation have been disabled.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
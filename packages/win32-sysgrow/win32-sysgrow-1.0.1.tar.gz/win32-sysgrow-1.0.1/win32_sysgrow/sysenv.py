import os
import winreg as reg

def test_path_exists_in(path: str, path_list: list[str]):
    prepared_path_list = []
    for existing_path in path_list:
        prepared_path_list.append(existing_path.lower().rstrip('\\/ '))
        pass

    prepared_path = path.lower().rstrip('\\/ ')
    return prepared_path in prepared_path_list

def add_env_path(path: str):
    key = reg.HKEY_CURRENT_USER  # For the current user (use HKEY_LOCAL_MACHINE for system-wide)
    reg_path = "Environment"   # Location where PATH is stored
    value_name = "Path"         # The name of the PATH variable in the registry

    path = path.replace('/', "\\")

    try:
        # Open the registry key where the PATH variable is stored
        reg_key = reg.OpenKey(key, reg_path, 0, reg.KEY_READ | reg.KEY_WRITE)

        # Get the current PATH variable value (it could be a string or a list of strings)
        current_path, reg_type = reg.QueryValueEx(reg_key, value_name)
        # print(f"Prev PATH is: {current_path}")

        # If it's a string, convert it to a list for easier modification
        if isinstance(current_path, str):
            current_path = current_path.split(os.pathsep)
            if current_path[-1] == '':
                current_path.pop()

        # print(f"current PATH is: {current_path}")

        # Avoid adding the new path if it's already present
        if not test_path_exists_in(path, current_path):
            current_path.append(path)
        else:
            return False
        
        # Join the paths back into a single string separated by os.pathsep (e.g., ";" for Windows)
        updated_path = os.pathsep.join(current_path)

        # Write the updated PATH back to the registry
        reg.SetValueEx(reg_key, value_name, 0, reg_type, updated_path)

        # Close the registry key
        reg.CloseKey(reg_key)

        # os.system('start C:\\ProgramData\\chocolatey\\bin\\RefreshEnv.cmd')

        print(f"Successfully added '{path}' to the PATH variable.")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def get_registry_path_list() -> list[str]:
    """Извлекает PATH из реестра (user + system)."""
    paths = []

    # Чтение системного PATH
    try:
        with reg.OpenKey(
            reg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        ) as key:
            sys_path, _ = reg.QueryValueEx(key, "Path")
            paths.extend(sys_path.split(os.pathsep))
    except (FileNotFoundError, OSError):
        pass

    # Чтение пользовательского PATH
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, "Environment") as key:
            user_path, _ = reg.QueryValueEx(key, "Path")
            paths.extend(user_path.split(os.pathsep))
    except (FileNotFoundError, OSError):
        pass

    # Удаляем пустые строки и пробелы, нормализуем
    clean_paths = [p.strip().strip('"') for p in paths if p.strip()]
    return clean_paths


def find_executable_in_registry_path(exe_name: str) -> str | None:
    path_entries = get_registry_path_list()
    
    pathext = os.environ.get("PATHEXT", ".EXE;.CMD;.BAT;.COM").lower().split(os.pathsep)
    pathext.insert(0, '')

    exe_name = exe_name.lower()

    for dir_path in path_entries:
        for ext in pathext:
            candidate = os.path.join(dir_path, exe_name + ext)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return os.path.abspath(candidate)

    return None
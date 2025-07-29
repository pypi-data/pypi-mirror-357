from pathlib import Path
import platform

def get_system_folder(folder_name: str) -> Path:
    """Get the path to a system folder (e.g., Pictures) based on the OS."""
    home = Path.home()
    if platform.system() == "Windows":
        return home / folder_name  # e.g., C:\Users\Kelly\Pictures
    else:
        return home / folder_name  # e.g., /home/kelly/Pictures
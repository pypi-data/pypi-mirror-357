from pathlib import Path
import shutil
from .utils import get_system_folder

# Map extensions to folders (system or custom)
SYSTEM_FOLDERS = {
    "Pictures": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".docx", ".txt"],
    "Videos": [".mp4", ".mov", ".avi"],
}
CUSTOM_FOLDERS = {
    "Archives": [".zip", ".rar", ".7z"],
}

def preview_moves(path: Path) -> list:
    """Generate a list of planned file moves without executing them."""
    path = Path(path)
    if not path.is_dir():
        print(f"Error: {path} is not a directory")
        return []

    moves = []
    for file in path.iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            moved = False

            # Check system folders
            for folder, extensions in SYSTEM_FOLDERS.items():
                if ext in extensions:
                    target_folder = get_system_folder(folder)
                    moves.append((file, target_folder / file.name))
                    moved = True
                    break

            # Check custom folders
            if not moved:
                for folder, extensions in CUSTOM_FOLDERS.items():
                    if ext in extensions:
                        target_folder = path / folder
                        moves.append((file, target_folder / file.name))
                        break

    return moves

def organize_files(path: Path):
    """Organize files in the given path into system or custom folders."""
    path = Path(path)
    if not path.is_dir():
        print(f"Error: {path} is not a directory")
        return

    file_count = 0
    for file in path.iterdir():
        if file.is_file():
            file_count += 1
            ext = file.suffix.lower()
            moved = False

            # Check system folders
            for folder, extensions in SYSTEM_FOLDERS.items():
                if ext in extensions:
                    target_folder = get_system_folder(folder)
                    move_file(file, target_folder)
                    moved = True
                    break

            # Check custom folders
            if not moved:
                for folder, extensions in CUSTOM_FOLDERS.items():
                    if ext in extensions:
                        target_folder = path / folder
                        move_file(file, target_folder)
                        break

    if file_count == 0:
        print(f"No files to organize in {path}")

def move_file(file: Path, target_folder: Path):
    """Move a file to the target folder, creating it if needed."""
    target_folder.mkdir(parents=True, exist_ok=True)
    new_path = target_folder / file.name
    try:
        shutil.move(str(file), str(new_path))
        print(f"Moved {file} -> {new_path}")
    except (shutil.Error, OSError) as e:
        print(f"Error moving {file}: {e}")
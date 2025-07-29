from pathlib import Path
import questionary

def select_folder() -> Path:
    """Let the user interactively select a folder using questionary."""
    current_path = Path.cwd()

    while True:
        # Get list of directories in the current path
        dirs = [d for d in current_path.iterdir() if d.is_dir()]
        dir_names = [d.name for d in dirs]
        choices = dir_names + ["..", "Cancel"]

        # Prompt user to select a folder
        selected = questionary.select(
            f"Select a folder to organize (current: {current_path}):",
            choices=choices,
            use_arrow_keys=True,
        ).ask()

        if selected == "Cancel":
            return None
        elif selected == "..":
            current_path = current_path.parent
        else:
            current_path = current_path / selected
            return current_path.resolve()

def confirm_moves(path: Path, moves: list) -> bool:
    """Show preview of file moves and ask for confirmation."""
    if not moves:
        print(f"No files to organize in {path}")
        return False

    print("Preview of file moves:")
    for src, dst in moves:
        print(f"Would move {src} -> {dst}")

    return questionary.confirm("Proceed with these file moves?").ask()
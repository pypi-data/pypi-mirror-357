from questionary import prompt
from .engine import organize_files, preview_moves
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init()

def get_folder_choice():
    """Prompt user to select a folder interactively."""
    answer = prompt({
        "type": "input",
        "name": "folder",
        "message": "Enter the folder path to organize (or press Enter for current directory):"
    })
    return answer["folder"] or "."

def display_preview(moves):
    """Display the preview of file moves with numbered, color-coded output."""
    if not moves:
        print("No files to move!")
        return
    print("\nPreview of file moves:")
    for i, (source, dest) in enumerate(moves.items(), 1):
        print(f"{i}. {Fore.GREEN}{source}{Style.RESET_ALL} -> {Fore.BLUE}{dest}{Style.RESET_ALL}")

def main():
    """Main function to run the organizer."""
    folder = get_folder_choice()
    moves = preview_moves(folder)
    display_preview(moves)
    if moves:
        confirm = prompt({
            "type": "confirm",
            "name": "proceed",
            "message": "Proceed with these moves?",
            "default": False
        })
        if confirm["proceed"]:
            organize_files(folder)
            print("Files organized successfully!")
        else:
            print("Operation cancelled.")

if __name__ == "__main__":
    main()
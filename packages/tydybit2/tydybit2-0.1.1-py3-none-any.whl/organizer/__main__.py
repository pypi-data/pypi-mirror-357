import argparse
from pathlib import Path
from .engine import preview_moves, organize_directory
from .interface import select_folder, confirm_moves

def main():
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="Organize files into system or custom folders")
    parser.add_argument("path", nargs="?", help="Directory to organize (default: interactive selection)")
    parser.add_argument("--interactive", action="store_true", help="Force interactive folder selection")
    args = parser.parse_args()

    # Determine target path
    if args.path and not args.interactive:
        target_path = Path(args.path).resolve()
    else:
        target_path = select_folder()

    # Run the organizer if a path was selected
    if target_path:
        # Get preview of moves
        moves = preview_moves(target_path)
        # Confirm moves with user
        if confirm_moves(target_path, moves):
            organize_directory(target_path)
    else:
        print("No folder selected. Exiting.")

if __name__ == "__main__":
    main()
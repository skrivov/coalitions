"""
script.py

Utility to recursively read and print all .py files in the specified directory.
"""

from __future__ import annotations
import os



def read_and_print_files(directory: str) -> None:
    """
    Recursively reads and prints the content of all .py files in the given directory.

    Args:
        directory (str): The path to the directory to scan.
    """
    for root, dirs, files in os.walk(directory):
        # Exclude hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"\n{'='*10} {file_path} {'='*10}\n")
                with open(file_path, 'r', encoding='utf-8') as f:
                    print(f.read())


def main() -> None:
    """
    Main entry point for the script, reading .py files in the current directory.
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    read_and_print_files(current_directory)


if __name__ == "__main__":
    main()

import os

def read_and_print_files(directory):
    for root, dirs, files in os.walk(directory):
        # Exclude hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"\n{'='*10} {file_path} {'='*10}\n")
                with open(file_path, 'r', encoding='utf-8') as f:
                    print(f.read())

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    read_and_print_files(current_directory)

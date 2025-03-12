import os
from pathlib import Path

def get_directory_tree(directory_path):
    tree = []
    for root, dirs, files in os.walk(directory_path):
        level = root.replace(directory_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree.append('{}{}/'.format(indent, os.path.basename(root)))
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            tree.append('{}{}'.format(sub_indent, file))
    return '\n'.join(tree)

def export_python_files_contents(directory_path):
    # Create a Path object for the directory path
    dir_path = Path(directory_path)
    
    # Check if the directory exists
    if not dir_path.is_dir():
        print(f"The provided path '{directory_path}' is not a valid directory.")
        return
    
    # Define the output file name based on the directory name
    output_file = f"{dir_path.name}_contents.txt"
    
    try:
        with open(output_file, 'w') as outfile:
            # Write the directory tree to the output file
            outfile.write("Directory Tree:\n")
            outfile.write(get_directory_tree(directory_path) + "\n\n")
            
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        relative_path = file_path.relative_to(dir_path)
                    
                        # Write the file path to the output file
                        outfile.write(f"File: {relative_path}\n")
                        
                        # Read and write the contents of the file to the output file
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            outfile.write(f.read())
                        
                        # Add a divider between file contents
                        outfile.write("\n" + '-' * 80 + "\n")
        
        print(f"The directory tree and contents have been saved to {output_file}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
directory_path = input("Enter the path of the directory: ")
export_python_files_contents(directory_path)
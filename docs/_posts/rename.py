import os

def remove_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    lines_to_remove = [
        'layout:', 
        'title:', 
        'date:',
        'category:'
    ]

    lines = [line for line in lines if not any(line.startswith(prefix) for prefix in lines_to_remove)]

    with open(file_path, 'w') as file:
        file.writelines(lines)

# specify directory
directory = '.'

for dirpath, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        if filename.endswith('.md'):
            file_path = os.path.join(dirpath, filename)
            remove_lines(file_path)
            print(f'Removed specific lines from file {file_path}')

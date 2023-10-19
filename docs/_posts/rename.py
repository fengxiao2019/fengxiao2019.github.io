import os

def sanitize_filename(filename):
    return filename.replace("'", "").replace(" ", "")

def remove_first_line_dashes(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    if lines[0].strip() == '---':
        lines = lines[1:]
    with open(file_path, 'w') as file:
        file.writelines(lines)

# specify directory
directory = '.'

for dirpath, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        if filename.endswith('.md'):
            sanitized_filename = sanitize_filename(filename)
            source = os.path.join(dirpath, filename)
            if sanitized_filename != filename:
                destination = os.path.join(dirpath, sanitized_filename)
                os.rename(source, destination)
                print(f'Renamed file {source} to {destination}')
                
            remove_first_line_dashes(destination if sanitized_filename != filename else source)

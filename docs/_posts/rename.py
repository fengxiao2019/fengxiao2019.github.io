import os

def sanitize_filename(filename):
    return filename.replace("'", "").replace(" ", "")

# specify directory
directory = '.'

for dirpath, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        if filename.endswith('.md'):
            sanitized_filename = sanitize_filename(filename)
            if sanitized_filename != filename:
                source = os.path.join(dirpath, filename)
                destination = os.path.join(dirpath, sanitized_filename)
                os.rename(source, destination)
                print(f'Renamed file {source} to {destination}')

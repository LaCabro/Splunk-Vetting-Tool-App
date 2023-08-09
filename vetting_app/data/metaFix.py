import os
import re

def perform_file_substitution(file):
    with open(file, 'r') as f:
        content = f.read()
    substituted_content1 = re.sub(r'\[ admin, ', r'[ admin, sc_admin, ', content)
    substituted_content2 = re.sub(r'\[ admin \]', r'[ admin, sc_admin ]', substituted_content1)
    substituted_content3 = re.sub(r'owner = admin', r'owner = sc_admin', substituted_content2)

    with open(file, 'w') as f:
        f.write(substituted_content3)

def search_files_with_extension(directory, extension):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                file = os.path.join(root, file)
                perform_file_substitution(file)

# Root directory for search
root_directory = "."  # You can adjust the root directory according to your needs

# Extension of files to search
file_extension = ".meta"  # You can adjust the extension according to your needs

# Perform search and substitution
search_files_with_extension(root_directory, file_extension)

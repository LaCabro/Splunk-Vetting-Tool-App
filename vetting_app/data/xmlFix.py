import os
import re

def formversionfix(file):
    with open(file, 'r') as f:
        content = f.read()
    if not re.search(r'<form[^>]*version="1.1"', content):
        subs = re.sub(r'(<form\b)', r'\1 version="1.1"', content)
        with open(file, 'w') as f:
            f.write(subs)

def dashboardversionfix(file):
    with open(file, 'r') as f:
        content = f.read()
    if not re.search(r'<dashboard[^>]*version="1.1"', content):
        subs = re.sub(r'(<dashboard\b)', r'\1 version="1.1"', content)
        with open(file, 'w') as f:
            f.write(subs)

def earliestFix(file):
    with open(file, 'r') as f:
        content = f.read()
    subs = re.sub(r'<earliestTime>(.*?)</earliestTime>', r'<earliest>\1</earliest>', content)
    with open(file, 'w') as f:
        f.write(subs)

def latestFix(file):
    with open(file, 'r') as f:
        content = f.read()
    subs = re.sub(r'<latestTime>(.*?)</latestTime>', r'<latest>\1</latest>', content)
    with open(file, 'w') as f:
        f.write(subs)

def search_files_with_pattern(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                formversionfix(file_path)
                dashboardversionfix(file_path)
                earliestFix(file_path)
                latestFix(file_path)

# Root directory to perform the search
root_directory = "."  # You can adjust the root directory according to your needs

# Perform the search and substitution
search_files_with_pattern(root_directory)

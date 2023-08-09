#Line
import os
import subprocess
#Get AppNames
process = subprocess.Popen('ls -d */', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, _ = process.communicate()
output = output.decode().strip()
directories = [line.rstrip('/') for line in output.splitlines()]
path = [folder for folder in directories]
def analyzer(file):
    try:
        with open(file, 'r') as f:
            contenido = f.read()

        # Verificar si hay Failures
        if "Failures: 0" not in contenido:
            return "Fail"

        # Verificar si hay Warnings
        if "Error: 0" not in contenido:
            return "Fail"

        # Verificar si PASSED está presente
        if "PASSED" not in contenido:
            return "Fail"

        if "Manual Checks: 0" not in contenido:
            return "Fail"

        return "Passed"
    except FileNotFoundError:
        return "Ignore"

def write_on_file(result):
    os.system(f"touch {AppName}.txt")
    with open(f"{AppName}.txt", 'w') as f:
        f.write(result)
    directory = "./Vetted/Apps_with_issues"
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        print(" ")
for folder in path:
    AppName = folder
    file = f"{AppName}.log"
    if os.path.exists(file):
        result = f"{AppName}: {analyzer(file)}"
        write_on_file(result)
        
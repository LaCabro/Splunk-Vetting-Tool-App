#Line
import os
import subprocess
import time
import shutil
#Get AppNames
process = subprocess.Popen('ls -d */', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, _ = process.communicate()
output = output.decode().strip()
directories = [line.rstrip('/') for line in output.splitlines()]
path = [folder for folder in directories]

for folder in path:
    AppName = folder
    status = f"{AppName}.txt"
    fileHTML = f"AppInspect_Report_{AppName}.html"
    SPLFile = f"{AppName}.spl"
    LOGFile = f"{AppName}.log"
    TEMP=f"{AppName}_temp"
    if os.path.exists(fileHTML):
        with open(status, 'r') as f:
            contenido = f.read()
        if "Passed" in contenido:
            folder_path = "./Vetted/VettedFolderApps"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                os.remove(fileHTML)

            if os.path.exists(f"./Vetted/{SPLFile}"):
                print(f"App {AppName} already Vetted")
                os.remove(SPLFile)
            else:    
                shutil.move(f"./{SPLFile}", "./Vetted/")
            if os.path.exists(f"./Vetted/{LOGFile}"):
                os.remove(LOGFile)
            else:    
                shutil.move(f"./{LOGFile}", "./Vetted/")

            os.remove(status)
            shutil.rmtree(TEMP)
            shutil.move(f"./{AppName}", "./Vetted/VettedFolderApps")
        else:
            issue_folder = "./Vetted/Apps_with_issues"
            if not os.path.exists(issue_folder):
                os.makedirs(issue_folder)
            if os.path.exists(fileHTML):
                print(f"Report for {AppName} already exists, please check and analyze the report")
            else:
                shutil.move(fileHTML, "./Vetted/Apps_with_issues/")
            os.remove(SPLFile)
            os.remove(LOGFile)
            os.remove(status)
            shutil.rmtree(TEMP)
# vetting_app/VetAssist.py
import os
import subprocess
import time
import argparse
import configparser
import sys
import re

def get_script_directory():
    if getattr(sys, 'frozen', False):  # Si el script se ejecuta como archivo ejecutable o instalado con PyInstaller
        script_directory = os.path.dirname(sys.executable)
    else:  # Si el script se ejecuta directamente con Python
        script_directory = os.path.dirname(os.path.abspath(__file__))
    return script_directory


def main():
    script_directory = get_script_directory()
    PythonFilePath = os.path.join(script_directory, "data", "cps-appVet.py")
    config_file = os.path.join(script_directory, "data", "setup.conf")

    def checkfile():
        filename = os.path.join(script_directory, "data", "check.crg")
        defaultContent = "is_configured = false"
        try:
            # Try to open file
            with open(filename, 'r') as archivo:
                content = archivo.read()
            if "is_configure = true" in content:
                pass
            else:
                file = os.path.join(script_directory, "data", "check.crg")
                subs = ("is_configure = false")
                with open(file, 'w') as f:
                    f.write(subs)

        except FileNotFoundError:
            # If if does not exist, then create file
            with open(filename, 'w') as archivo:
                archivo.write(defaultContent)

    def run_configure():
        configure_script = os.path.join(script_directory, "data", "configure.py")
        python_executable = sys.executable
        subprocess.call([python_executable, configure_script])

    # Check if the check.crg file is present in the current directory
    def vfy():
        checkfile()
        file = os.path.join(script_directory, "data", "check.crg")
        with open(file, 'r') as f:
            content = f.read()
        if "is_configure = false" in content:
            print("Configuring SVTA App for the first time...")
            run_configure()
            subs = re.sub(r'is_configure = false', r'is_configure = true', content)
            with open(file, 'w') as f:
                f.write(subs)
        else:
            pass

    config = configparser.ConfigParser()
    config.read(config_file)
    SplunkPythonPath = config.get('ScriptSetup', 'splunkpythonpath')
    cmd = os.path.join(f"{SplunkPythonPath} cmd python")

    def quickFixes():
        fixXML = os.path.join(script_directory, "data", "xmlFix.py")
        fixMETA = os.path.join(script_directory, "data", "metaFix.py")
        python_executable = sys.executable
        print("Running Quick Fixes, plese wait...")
        subprocess.call([python_executable, fixXML])
        time.sleep(3)
        subprocess.call([python_executable, fixMETA])
        print("Quick Fixes Completed")

    def run_vetting(app, use_local_only, use_private_app, ignore_local, bin_delete):
        comando = f'{cmd} {PythonFilePath} --app="{app}"'
        if use_local_only:
            comando += " -l"
        if use_private_app:
            comando += " -p"
        if ignore_local:
            comando += " -d"
        if bin_delete:
            comando += " -b"
        subprocess.call(comando, shell=True)
        time.sleep(1)

    def run_bulk_vetting():
        process = subprocess.Popen('ls -d */', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()
        output = output.decode().strip()
        directories = [line.rstrip('/') for line in output.splitlines()]
        excluded_directories = ["Vetted", "VettingApps", "Apps_with_issues"]
        for folder in directories:
            if folder in excluded_directories:
                continue
            run_vetting(folder, False, False, False, False)
            print(f"Done for {folder}")

    def verify():
        VettingVerify = os.path.join(script_directory, "data", "VettingVerificator.py")
        VetVerify = f'{cmd} {VettingVerify}'
        subprocess.call(VetVerify, shell=True)

        ActionVerify = os.path.join(script_directory, "data", "ActionVerificator.py")
        ActVerify = f'{cmd} {ActionVerify}'
        subprocess.call(ActVerify, shell=True)

        print("Finished")

    parser = argparse.ArgumentParser()
    parser.add_argument("--bulk", action="store_true", help="Run vettings in bulk mode")
    parser.add_argument("--app", help="Run vetting for a specific app")
    parser.add_argument("-l", "--use_local_only", action="store_true", help="Vetting for Local Only")
    parser.add_argument("-p", "--use_private_app", action="store_true", help="Vetting Private Apps")
    parser.add_argument("-d", "--ignore_local", action="store_true", help="Vetting and Ignoring Local")
    parser.add_argument("-b", "--bin_delete", action="store_true", help="Vetting and bin Delete")
    parser.add_argument("--configure", action="store_true", help="Configure the SVTA App")
    parser.add_argument("--fix", action="store_true", help="Run QuickFix on the apps you want to run Vetting")
    args = parser.parse_args()

    if not args.fix and not args.bulk and not args.app and not args.configure:
        vfy()
        text = """
SSSSSSSSSSS   VV      VV   TTTTTTTTT     AA
SS             VV    VV    TTTTTTTTT    AAAA
SSSSSSSSSSS     VV  VV        TTT      AA  AA
         SS      VVVV         TTT     AAAAAAAA
SSSSSSSSSSS       VV          TTT    AAA    AAA"""
        print(text)
        print(" ")
        print("Thanks for using VettingApp, please check the available options by running 'svta --help'")
        print(" ")
    
    if args.fix and args.bulk:
        parser.error("Fixes can not be run along with bulk command, execute first the --fix and then --bulk")

    if args.configure and args.bulk:
        parser.error("Configuration Mode can not be run along with bulk command, execute first the --configure and then --bulk")

    if args.fix and args.app:
        parser.error("Fixes can not be run along with single Vetting App mode, execute first the --fix and then --app")

    if args.configure and args.app:
        parser.error("Configuration Mode can not be run along with single Vetting App mode, execute first the --configure and then --app")

    if args.app and args.bulk:
        parser.error("Single Vetting App mode can not be run along with bulk mode, please choose just one vetting mode")

    if args.fix and args.configure:
        parser.error("Fixes and Configure can not be executed at the same time")

    if args.configure:
        run_configure()

    elif args.fix:
        quickFixes()

    elif args.bulk:
        vfy()
        run_bulk_vetting()
        verify()

    elif args.app:
        vfy()
        run_vetting(args.app, args.use_local_only, args.use_private_app, args.ignore_local, args.bin_delete)
        verify()

if __name__ == "__main__":
    main()

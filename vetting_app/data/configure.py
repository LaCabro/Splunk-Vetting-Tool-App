import os
import configparser
import getpass
import platform
import sys

def get_script_directory():
    if getattr(sys, 'frozen', False):  # Si el script se ejecuta como archivo ejecutable o instalado con PyInstaller
        script_directory = os.path.dirname(sys.executable)
    else:  # Si el script se ejecuta directamente con Python
        script_directory = os.path.dirname(os.path.abspath(__file__))
    return script_directory

path = get_script_directory()

def get_credentials():
    username = input("Splunk Username = ")
    password = getpass.getpass("Splunk Password = ")
    return username, password

def update_config(username, password, splunk_path):
    config = configparser.ConfigParser()
    config.read(f"{path}/setup.conf")

    if "credential" not in config:
        config.add_section("credential")

    config.set("credential", "username", username)
    config.set("credential", "password", password)

    if "ScriptSetup" not in config:
        config.add_section("ScriptSetup")

    if "SplunkPythonPath" in config["ScriptSetup"]:
        choice = input("The Splunk Path is already configured. Do you want to update it? (y/n): ").lower()
        if choice == "y":
            config.set("ScriptSetup", "SplunkPythonPath", splunk_path)
    else:
        config.set("ScriptSetup", "SplunkPythonPath", splunk_path)

    try:
        with open(f"{path}/setup.conf", "w") as config_file:
            config.write(config_file)
    except Exception as e:
        print("Error writing to setup.conf:", e)

def main():
    print("Configuring SVTA App, please provide the required information:")
    print("==============================================================")
    
    if os.path.exists(f"{path}/setup.conf"):
        config = configparser.ConfigParser()
        try:
            config.read(f"{path}/setup.conf")
        except Exception as e:
            print("Error reading setup.conf:", e)
            return

        if "credential" in config:
            choice = input("Configuring Credentials, do you want to proceed ? (y/n): ").lower()
            if choice == "y":
                username, password = get_credentials()

                # Check the operating system
                os_name = platform.system()
                if os_name == "Windows":
                    splunk_path = r'C:\"Program Files"\Splunk\bin\splunk'
                elif os_name == "Linux":
                    splunk_path = "/opt/splunk/bin/splunk"
                elif os_name == "Darwin":  # macOS
                    splunk_path = "/Applications/Splunk/bin/splunk"
                else:
                    print(f"Unsupported operating system: {os_name}")
                    return

                default_splunk_path = input("Is Splunk installed in the default path? (y/n): ").lower()
                if default_splunk_path == "n":
                    custom_splunk_path = input("Please enter the full path to /bin/splunk: ")
                    splunk_path = custom_splunk_path.strip()

                update_config(username, password, splunk_path)
                print("SVTA configuration has been updated successfully.")
                print("==============================================================")
            else:
                print("Configuration remains unchanged.")
                print("==============================================================")
        else:
            print("No 'credential' section found in setup.conf.")
            print("==============================================================")
    else:
        print("Warning: Missing Files, please reinstall the SVTA app")
        print("==============================================================")

if __name__ == "__main__":
    main()

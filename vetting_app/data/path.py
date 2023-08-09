import os
import subprocess
import time
import argparse
import configparser

script_directory = os.path.dirname(os.path.abspath(__file__))
PythonFilePath = os.path.join(script_directory, "data", "cps-appVet.py")
config = configparser.ConfigParser()
config.read(f'{script_directory}/data/setup.conf')
SplunkPythonPath = config.get('ScriptSetup', 'SplunkPythonPath')

print(SplunkPythonPath)
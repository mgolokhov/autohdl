import os
import subprocess

os.chdir('autohdl')
subprocess.call(['python', 'deploy.py'])


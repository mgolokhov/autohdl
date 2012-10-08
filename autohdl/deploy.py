import subprocess
import os

os.chdir('..')
subprocess.call(['python', 'setup.py', 'clean', '-a'])
subprocess.call(['python', 'setup.py', 'install'])


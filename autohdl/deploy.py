import subprocess
import os

os.chdir(os.path.join(os.path.dirname(__file__),'..'))
subprocess.call(['python', 'setup.py', 'clean', '-a'])
subprocess.call(['python', 'setup.py', 'install'])


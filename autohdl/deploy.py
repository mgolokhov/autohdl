import subprocess
import os
import sys

sys.path.insert(0, '.')
import pkg_info

print(pkg_info.inc_version())
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
subprocess.call(['python', 'setup.py', 'clean', '-a'])
subprocess.call(['python', 'setup.py', 'install'])


import subprocess

subprocess.call(['python', 'setup.py', 'bdist_wininst'])
subprocess.call(['python', 'setup.py', 'clean'])
subprocess.call(['python', 'setup.py', 'install'])

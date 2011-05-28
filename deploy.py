import subprocess

subprocess.call(['python', 'setup.py', 'clean', '-a'])
subprocess.call(['python', 'setup.py', 'bdist_wininst', '--pre-install-script', 'preinstall.py'])
subprocess.call(['python', 'setup.py', 'uninstall'])
subprocess.call(['python', 'setup.py', 'install'])




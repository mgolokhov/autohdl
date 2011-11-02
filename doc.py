import os
import subprocess


def handler(page):
  if page == 'index':
    subprocess.Popen(os.path.dirname(__file__)+'/doc/index.html', shell = True)

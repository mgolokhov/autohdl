import subprocess
import os

def compile(i_file_list):
  path_modelsim = 'c:/modeltech_6.6a/win32/'
  os.mkdir(os.getcwd()+'/../simulate')
  os.chdir(os.getcwd()+'/../simulate')
  subprocess.call([path_modelsim+'vlib', 'mylib'])
  subprocess.call([path_modelsim+'vmap', 'work mylib'])
  subprocess.call([path_modelsim+'vlog', ' ', join(i_file_list)])


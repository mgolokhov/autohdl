import sys
import os
import shutil



sys.path.insert(0, '..')
sys.path.insert(0, '.')
from instance import *




if os.path.exists('tmp_test_dir'):
  shutil.rmtree('tmp_test_dir')      
if not os.path.exists('tmp_test_dir'):
  os.mkdir('tmp_test_dir')
shutil.copytree('data/prj4test', 'tmp_test_dir/prj4test/')
os.chdir('tmp_test_dir/prj4test/script')


   
res = ParseFile('../src/top1.v')
print res.content
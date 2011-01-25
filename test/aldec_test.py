import sys
import os
import shutil
import unittest


sys.path.insert(0, '..')
import utils
from aldec import *
from hdlLogger import *
#logging.disable(logging.ERROR)

class Tests(unittest.TestCase):
  
  def setUp(self):
    if not os.path.exists('tmp_test_dir'):
      os.mkdir('tmp_test_dir')

  def tearDown(self):
    if os.path.exists('tmp_test_dir'):
       shutil.rmtree('tmp_test_dir')
      
      
  def test_gen(self):
    dsnName = 'noName'
    dsnPath = os.getcwd().replace('\\','/')+'tmp_test_dir/dir1/dir2/dsn1'
    utils.mkFakeRepo(iPath = 'tmp_test_dir')
    os.chdir('tmp_test_dir/dir1/dir2/dsn1/script')
#    gen(iTopModule = '', iDsnName = dsnName)
    tb(iTopModule = 'dsn1_m1', iPrjName = dsnName, iClean = True)
    
    
    
if __name__ == '__main__':
  unittest.main()
import copy
import sys
import os
import shutil
import unittest

sys.path.insert(0, '..')
from structure import *
from hdlLogger import *



def _mk_tree(paths):
  for i in paths:
    if os.path.splitext(i)[1]:
      path = os.path.dirname(i)
      if not os.path.exists(path):
        os.makedirs(path)
      open(i, 'w').close()
    else:
      if not os.path.exists(i):
        os.makedirs(i)


class Tests(unittest.TestCase):
 
  def setUp(self):
    self.tree = {
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v1'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v3'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v1'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v3'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v1'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v2'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v1'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v2'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v1'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v2'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v1'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v2'),
                 os.path.join(os.getcwd(), 'tmp_test_dir', 'empty'),
                 }
    _mk_tree(self.tree)

  def tearDown(self):
    if os.path.exists('tmp_test_dir'):
       shutil.rmtree('tmp_test_dir')

  def test_search(self):
    res = search(directory='tmp_test_dir')
    expected = copy.copy(self.tree)
    expected.remove(os.path.join(os.getcwd(), 'tmp_test_dir', 'empty'))
    self.assertSetEqual(expected, set(res))

  def test_search1(self):
    res = search(directory='tmp_test_dir', onlyExt='.v')
    expected = {
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v'),
      }

    self.assertSetEqual(expected, set(res))


  def test_search2(self):
    res = search(directory='tmp_test_dir', onlyExt=['.v', '.v1'])
    expected = {
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v1'),
    }
    self.assertSetEqual(expected, set(res))

  def test_search3(self):
    res = search(directory='tmp_test_dir', ignoreExt=['.v2'])
    expected = {
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v3'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v3'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v1'),
      }
    self.assertSetEqual(expected, set(res))

  def test_search4(self):
    res = search(directory='tmp_test_dir', ignoreExt=['.v2', '.v3'])
    expected = {
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'tmp', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v1'),
      }
    self.assertSetEqual(expected, set(res))

  def test_search5(self):
    res = search(directory='tmp_test_dir', ignoreDir='tmp')
    expected = {
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v2'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v2'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v2'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v2'),
      }
    self.assertSetEqual(expected, set(res))

  def test_search6(self):
    res = search(directory='tmp_test_dir', ignoreDir=['tmp', 'dir2'])
    expected = {
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v2'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v2'),
      }
    self.assertSetEqual(expected, set(res))

  def test_search7(self):
    res = search(directory='tmp_test_dir', ignoreDir='tmp', onlyExt='.v')
    expected = {
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v'),
      }
    self.assertSetEqual(expected, set(res))

  def test_search8(self):
    res = search(directory='tmp_test_dir', ignoreDir='tmp', ignoreExt='.v')
    expected = {
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f.v2'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'dir1', 'dir2', 'f1.v2'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f.v2'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v1'),
      os.path.join(os.getcwd(), 'tmp_test_dir', 'f1.v2'),
      }
    self.assertSetEqual(expected, set(res))


def runTests():
  logging.disable(logging.ERROR)
  tests = [
           'test_search',
           'test_search1',
           'test_search2',
          ]

  suite = unittest.TestSuite(map(Tests, tests))
  unittest.TextTestRunner(verbosity=3).run(suite)  

if __name__ == '__main__':
  unittest.main()
#  runTests()

  
  
  
  
  
  
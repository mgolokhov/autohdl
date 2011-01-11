import shutil
import os
import sys
import subprocess
import unittest


class Test(unittest.TestCase):
  def test_main(self):
    path = os.path.dirname(__file__)
    curDir = os.getcwd().replace('\\', '/')
    if os.path.exists('prj4test'):
      shutil.rmtree('prj4test')
    shutil.copytree(path+'/prj4test', 'prj4test')
    os.chdir('prj4test/ctrl_v2_shagovik')
    f = open('test_results', 'w')
    subprocess.call(['python', sys.exec_prefix+'/hdl.py', '-l'], stdout=f, stderr=f)
    f.close()
    f = open('test_results', 'r')
    actual = f.read()
    f.close()
    actualAsList = actual.split('\n')
    res = [i for i in actualAsList if os.path.splitext(i)[1] != '.pyo']
    actual = '\n'.join(res)
    f = open(path+'/prj4test/gold_results', 'r')
    expected = f.read()
    f.close()
    expected = expected.format(local_cwd = curDir)
#    print expected
    self.maxDiff = None
    self.assertMultiLineEqual(expected, actual)
    print 'pyk'

def runTest():
  tests = ['test_main'
           ]

  suite = unittest.TestSuite(map(Test, tests))
  unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == '__main__':
  unittest.main()
import unittest
import sys, os, shutil
sys.path.insert(0, '..')
from build import *

class Test(unittest.TestCase):
  def test_getDeps(self):
    t = '''
    <wsp>
    <dsn id = "some">
    <dep>.</dep>
    <dep>..</dep>
    <dep>shit</dep>
    </dsn>
    <dsn id = "myDesign">
    <dep>../..</dep>
    </dsn>
    <dsn id = "dsn666">
     <dep>shit</dep>
    </dsn>
    </wsp>
    '''
    buildFile = os.getcwd()+'/wsp/dsn/resource/build.xml'
    if not os.path.exists('wsp/dsn/resource/'):
      os.makedirs('wsp/dsn/resource/')
    
    f = open(buildFile, 'w')
    f.write(t)
    f.close()
    
    dsnName = 'myDesign'
    expected = {u'myDesign': [u'G:/repo/git/autohdl/test/wsp/../..'],
                u'some': [u'G:/repo/git/autohdl/test/wsp/.',
                          u'G:/repo/git/autohdl/test/wsp/..']}
    
    self.assertDictEqual(expected, getDeps(iDsnName = dsnName, iBuildFile = buildFile))

    if os.path.exists(buildFile): shutil.rmtree('wsp')
    
if __name__ == '__main__':
  unittest.main()
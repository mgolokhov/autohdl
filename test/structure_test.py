import sys
import os
import shutil
import unittest

try:
  sys.path.insert(0, '..')
  from structure import *
  from hdlLogger import *
except ImportError:
  from autohdl.structure import *
  from autohdl.hdlLogger import *


class Tests(unittest.TestCase):
 
  def setUp(self):
    if not os.path.exists('tmp_test_dir'):
      os.mkdir('tmp_test_dir')

  def tearDown(self):
    if os.path.exists('tmp_test_dir'):
       shutil.rmtree('tmp_test_dir')

    
  def test_genDsn(self):
    dsn = Design(iPath = './tmp_test_dir', iName = 'mega_dsn')
    path = os.getcwd().replace('\\', '/')
    self.assertEqual('mega_dsn', dsn.name)
    self.assertEqual(path+'/tmp_test_dir/mega_dsn', dsn.pathRoot)
    expectedStructure = set([dsn.pathRoot+'/resource/implement_default',
                             dsn.pathRoot+'/resource/synthesis_default',
                             dsn.pathRoot+'/resource/build.xml',
                             dsn.pathRoot+'/script/kungfu.py'])
    actualStructure = (set(search(iPath = dsn.pathRoot)))
    self.assertSetEqual(expectedStructure, actualStructure)
    
  
  def test_genDsn2(self):
    dsn = Design(iPath = '..', iInit = False, iGen = False)
    self.assertEqual('autohdl', dsn.name)
    expectedPath = (os.path.abspath(os.getcwd()+'/..')).replace('\\', '/')
    self.assertEqual(expectedPath, dsn.pathRoot)
  
  
  def test_initDsn(self):
    dsn1 = Design(iPath = './tmp_test_dir', iName = 'dsn1', iInit = False)
    dsn2 = Design(iPath = './tmp_test_dir', iName = 'dsn2', iInit = False)
    
    f = open(dsn1.pathRoot+'/src/f1.v', 'w')
    t = '''
    module f1(input a, output b);
    f2 name1(a, b);
    f3 name2(a, b);
    endmodule
    '''
    f.write(t)
    f.close()
    
    f = open(dsn1.pathRoot+'/resource/build.xml', 'w')
    t = '''
    <wsp>
    <dsn id="dsn1">
    <dep>dsn2</dep>
    </dsn>
    </wsp>
    '''
    f.write(t)
    f.close()
    
    f = open(dsn2.pathRoot+'/src/f2.v', 'w')
    t = '''
    module f2(input a, output b);
    f4 name1(a, b);
    endmodule
    '''
    f.write(t)
    f.close()
    
    dsn1.init()
    actual = str(dsn1) 
    expected = '''\
DsnName: dsn1
pathRoot:
\t{0}/tmp_test_dir/dsn1
fileMain:
\t{0}/tmp_test_dir/dsn1/src/f1.v
fileDep:
\t{0}/tmp_test_dir/dsn2/src/f2.v'''.format(os.getcwd().replace('\\','/'))
    self.assertMultiLineEqual(expected, actual)

    
  def test_filter(self):
    t = ['']
    expected = ['']
    self.assertItemsEqual(filter(t), expected)

    t = ['just_one_file']
    expected = ['just_one_file']
    self.assertItemsEqual(filter(t), expected)
    
    t = ['f1', 'f2', 'f3']
    expected = ['f1', 'f2', 'f3']
    self.assertItemsEqual(filter(t), expected)
   
    t = ['f1', 'f2', 'f3']
    expected = ['f1', 'f3']
    self.assertItemsEqual(filter(iFiles = t, iIgnore = ['f2']), expected)
    
    t = ['f1', 'f2', 'f3']
    expected = ['f2', 'f3']
    self.assertItemsEqual(filter(iFiles = t, iOnly = ['f2', 'f3']), expected)

    t = ['f1', 'f2', 'f3']
    expected = ['f3']
    self.assertItemsEqual(filter(iFiles = t, iOnly = ['f2', 'f3'], iIgnore = ['f2']),
                          expected)

    t = ['dir1/f1', 'dir2/f2', 'dir3/f3', 'd4/f4']
    expected = ['dir1/f1', 'dir3/f3']
    self.assertItemsEqual(filter(iFiles = t, iOnly = ['dir',], iIgnore = ['f2']),
                          expected)
    
    
  def test_getLocToBuildXml(self):
    self.assertEqual(None, getLocToBuildXml('asd'))
    if not os.path.exists('tmp_test_dir/src'): os.makedirs('tmp_test_dir/src')
    if not os.path.exists('tmp_test_dir/resource'): os.makedirs('tmp_test_dir/resource')
    open('tmp_test_dir/src/f1', 'w').close()
    open('tmp_test_dir/resource/build.xml', 'w').close()
    path, dsnName = getLocToBuildXml(os.getcwd()+'/tmp_test_dir/src/f1')
    expectedPath = os.getcwd().replace('\\','/')+'/tmp_test_dir/resource/build.xml'
    expectedDsnName = 'tmp_test_dir'
    self.assertEqual(expectedPath, path)
    self.assertEqual(expectedDsnName, dsnName)
    
    
  def test_getDepSrc(self):
    dsn1 = Design(iName = 'tmp_test_dir/dsn1', iInit = False)
    f = open('tmp_test_dir/dsn1/src/f1.v', 'w')
    t = '''
    module f1(input a, output b);
    f2 name1(a, b);
    f3 name2(a, b);
    endmodule
    '''
    f.write(t)
    f.close()
    
    f = open('tmp_test_dir/dsn1/resource/build.xml', 'w')
    t = '''
    <wsp>
    <dsn id="dsn1">
    <dep>dsn2</dep>
    </dsn>
    </wsp>
    '''
    f.write(t)
    f.close()
    
    dsn2 = Design(iName = 'tmp_test_dir/dsn2', iInit = False)
    f = open('tmp_test_dir/dsn2/src/f2.v', 'w')
    t = '''
    module f2(input a, output b);
    f4 name1(a, b);
    f1 name2(a,b);
    endmodule
    '''
    f.write(t)
    f.close()
    
    f = open('tmp_test_dir/dsn2/resource/build.xml', 'w')
    t = '''
    <wsp>
    <dsn id="dsn2">
    <dep>dsn1</dep>
    </dsn>
    </wsp>
    '''
    f.write(t)
    f.close()

    src = [os.getcwd().replace('\\','/')+'/tmp_test_dir/dsn1/src/f1.v']
    expected = set([os.getcwd().replace('\\','/')+'/tmp_test_dir/dsn2/src/f2.v'])
    self.assertSetEqual(expected, getDepSrc(iSrc = src))

    
  @unittest.skip("BUGAGA: unfinished")  
  def test_search(self):
    res = search(iOnly = ['.v'], iIgnore = ['prj4test'])
    print '\n'.join(res)

def runTests():
  logging.disable(logging.ERROR)
  tests = [
           'test_getDepSrc',
           'test_getLocToBuildXml',
           'test_genDsn',
           'test_genDsn2',
           'test_initDsn',
           'test_filter',
           'test_search'
          ]

  suite = unittest.TestSuite(map(Tests, tests))
  unittest.TextTestRunner(verbosity=3).run(suite)  

if __name__ == '__main__':
#  unittest.main()
  runTests()

  
  
  
  
  
  
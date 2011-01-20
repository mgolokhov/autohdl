import sys
import os
import shutil
import unittest


sys.path.insert(0, '..')
from structure import *
from hdlLogger import *
logging.disable(logging.ERROR)

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
#    print dsn1    
    

  
    
    
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
    
  
  def test_initMain(self):
#    log.setLevel(logging.DEBUG)
    prjStruct = ['/project/dsn1/f1.v',
                 '/project/dsn1/f2.v',
                 '/project/dsn2/f1.v',
                 '/project/dsn2/f2.v',
                 '/project/dsn3/'
                ]
    expected = ['./project/dsn1/f1.v',
                './project/dsn1/f2.v'
                ]
    self.genTree(prjStruct)
    os.chdir('project/dsn1')
    dsn = Design()
    fileMain, dirMain = self.initMain()
    actual = fileMain + fileMain
    self.assertItemsEqual(expected, actual)
    shutil.rmtree('./project')
    #
    #
    #
    expected = ['./project/dsn1/f1.v',
                './project/dsn1/f2.v',
                './project/dsn2/f1.v',
                './project/dsn2/f2.v', 
                './project/dsn3']
    self.genTree(prjStruct)
    dsn = Design(iDsnName = 'dsn', iPathRoot = './project')
    dsn.initMain()
    actual = dsn.getFileMain() + dsn.getDirMain()
    self.assertItemsEqual(expected, actual)
    shutil.rmtree('./project')
    #
    #
    #
    expected = ['./project/dsn2/f1.v',
                './project/dsn2/f2.v',
                './project/dsn3'
                ]
    self.genTree(prjStruct)
    dsn = Design(iDsnName = 'dsn', iPathRoot = './project')
    dsn.initMain(iIgnore = ['dsn1'])
    actual = dsn.getFileMain() + dsn.getDirMain()
    self.assertItemsEqual(expected, actual)
    shutil.rmtree('./project')
    #
    #
    #
    prjStruct = ['/project/dsn1/',
                 '/project/dsn2/',
                 '/project/dsn3/',
                 '/project/ignore/'
                ]
    expected = ['./project/dsn1',
                './project/dsn3'
                ]
    self.genTree(prjStruct)
    dsn = Design(iDsnName = 'dsn', iPathRoot = './project')
    dsn.initMain(iOnly = ['dsn'], iIgnore = ['dsn2'])
    actual = dsn.getFileMain() + dsn.getDirMain()
    self.assertItemsEqual(expected, actual)
    shutil.rmtree('./project')
    
    
  def test_getLocToBuildXml(self):
#    pathSrcFile = 'fake'
#    dsn.getLocToBuildXml(pathSrcFile)
#    pathSrcFile = os.path.abspath( __file__ )
#    dsn.getLocToBuildXml(pathSrcFile)
    if not os.path.exists('src'): os.mkdir('src')
    if not os.path.exists('resource'): os.mkdir('resource')
    f = open('src/f1', 'w')
    f.close()
    f = open('resource/build.xml', 'w')
    f.close()
    path, dsnName = self.getLocToBuildXml(os.getcwd()+'/src/f1')
    expectedPath = 'G:/repo/git/autohdl/test/resource'
    expectedDsnName = 'test'
    self.assertEqual(expectedPath, path)
    self.assertEqual(expectedDsnName, dsnName)
    shutil.rmtree('resource')
    shutil.rmtree('src')
    
    
  def test_getDeps(self):
    os.mkdir('myWsp')
    os.chdir('myWsp')
    dsn = Design(iDsnName = 'myDsn1')
    Design(iDsnName = 'myDsn2')
    f = open('myWsp/myDsn1/src/f1.v', 'w')
    t = '''
    module f1(input a, output b);
    f2 name1(a, b);
    f3 name2(a, b);
    endmodule
    '''
    f.write(t)
    f.close()
    
    f = open('myWsp/myDsn1/resource/build.xml', 'w')
    t = '''
    <wsp>
    <dsn id="myDsn1">
    <dep>myDsn2</dep>
    </dsn>
    </wsp>
    '''
    f.write(t)
    f.close()
    
    f = open('myWsp/myDsn2/src/f2.v', 'w')
    t = '''
    module f2(input a, output b);
    f4 name1(a, b);
    endmodule
    '''
    f.write(t)
    f.close()
    
    expected = set(['G:/repo/git/autohdl/test/myWsp/myDsn2/src/f2.v'])
    self.assertSetEqual(expected, dsn.getDeps())
    os.chdir('..')
    shutil.rmtree('myWsp')
    
    
    
  def test_search(self):
    res = s.search(iOnly = ['.v'], iIgnore = ['prj4test'])
    print '\n'.join(res)

def runTests():
  tests = [

           'test_genDsn',
           'test_genDsn2',
           'test_initDsn',
           'test_filter'
          ]

  suite = unittest.TestSuite(map(Tests, tests))
  unittest.TextTestRunner(verbosity=3).run(suite)  

if __name__ == '__main__':
#  unittest.main()
  runTests()

  
  
  
  
  
  
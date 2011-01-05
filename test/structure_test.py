import sys
import os
import shutil
import unittest


sys.path.insert(0, '..')
import structure as s
from hdlLogger import *
#consoleHandler.setLevel(logging.DEBUG)



class Tests(unittest.TestCase):
  pathCur = os.getcwd()
  
  def setUp(self):
#    self.dsn = Design(iDsnName = 'dsn')
    pass

  def tearDown(self):
#    log.setLevel(logging.INFO)
    if os.path.exists('dsn'): shutil.rmtree('dsn')
    os.chdir(Tests.pathCur)
    if sys.path[0] == '../..':
      sys.path.pop(0)
      reload(s)
    
  def test_init1(self):
    if not os.path.exists('dsn4test1'): os.mkdir('dsn4test1')
    os.chdir('dsn4test1')
    sys.path.insert(0, '../..')
    reload(s)
    dsn = s.Design()
    expected = '''\
name: dsn4test1
dirMain: {0}/src
\t{0}/TestBench
fileMain: {0}/resource/implement_default
\t{0}/resource/synthesis_default
\t{0}/script/kungfu.py
fileDep: 
pathRoot: {0}'''.format(os.getcwd().replace('\\', '/'))
    self.assertMultiLineEqual(expected, str(dsn))
    os.chdir('..')
    if os.path.exists('dsn4test1'): shutil.rmtree('dsn4test1')
  
  def test_init2(self):  
    dsn = s.Design('dsn4test2')
    expected = '''\
name: dsn4test2
dirMain: {0}/src
\t{0}/TestBench
fileMain: {0}/resource/implement_default
\t{0}/resource/synthesis_default
\t{0}/script/kungfu.py
fileDep: 
pathRoot: {0}'''.format(os.getcwd().replace('\\', '/')+'/dsn4test2')
    self.assertMultiLineEqual(expected, str(dsn))
    if os.path.exists('dsn4test2'): shutil.rmtree('dsn4test2')
    
  def test_init3(self):
    s.Design('dsn4test3')
    s.Design('dsn4test4')
    
    f = open('dsn4test3/src/f1.v', 'w')
    t = '''
    module f1(input a, output b);
    f2 name1(a, b);
    f3 name2(a, b);
    endmodule
    '''
    f.write(t)
    f.close()
    
    f = open('dsn4test3/resource/build.xml', 'w')
    t = '''
    <wsp>
    <dsn id="dsn4test3">
    <dep>dsn4test4</dep>
    </dsn>
    </wsp>
    '''
    f.write(t)
    f.close()
    
    f = open('dsn4test4/src/f2.v', 'w')
    t = '''
    module f2(input a, output b);
    f4 name1(a, b);
    endmodule
    '''
    f.write(t)
    f.close()    
    
    dsn = s.Design('dsn4test3')
    
    expected = '''\
name: dsn4test3
dirMain: {0}/dsn4test3/TestBench
fileMain: {0}/dsn4test3/resource/build.xml
\t{0}/dsn4test3/resource/implement_default
\t{0}/dsn4test3/resource/synthesis_default
\t{0}/dsn4test3/script/kungfu.py
\t{0}/dsn4test3/src/f1.v
fileDep: {0}/dsn4test4/src/f2.v
pathRoot: {0}/dsn4test3'''.format(os.getcwd().replace('\\','/'))
    self.assertMultiLineEqual(expected, str(dsn))
    if os.path.exists('dsn4test3'): shutil.rmtree('dsn4test3')
    if os.path.exists('dsn4test4'): shutil.rmtree('dsn4test4')
  
  def test_init4(self):
    s.Design('dsn4test3')
    s.Design('dsn4test4')
    
    f = open('dsn4test3/src/f1.v', 'w')
    t = '''
    module f1(input a, output b);
    f2 name1(a, b);
    f3 name2(a, b);
    endmodule
    '''
    f.write(t)
    f.close()
    
    f = open('dsn4test3/resource/build.xml', 'w')
    t = '''
    <wsp>
    <dsn id="dsn4test3">
    <dep>dsn4test4</dep>
    </dsn>
    </wsp>
    '''
    f.write(t)
    f.close()
    
    f = open('dsn4test4/src/f2.v', 'w')
    t = '''
    module f2(input a, output b);
    f4 name1(a, b);
    endmodule
    '''
    f.write(t)
    f.close()    
    
    dsn = s.Design('dsn4test3', iOnly = ['src'])
    
    expected = '''\
name: dsn4test3
dirMain: 
fileMain: {0}/dsn4test3/src/f1.v
fileDep: {0}/dsn4test4/src/f2.v
pathRoot: {0}/dsn4test3'''.format(os.getcwd().replace('\\','/'))
    self.assertMultiLineEqual(expected, str(dsn))
    if os.path.exists('dsn4test3'): shutil.rmtree('dsn4test3')
    if os.path.exists('dsn4test4'): shutil.rmtree('dsn4test4')
    
    
  def test_filter(self):
    t = ['']
    expected = ['']
    self.assertItemsEqual(self.dsn.filter(t), expected)

    t = ['just_one_file']
    expected = ['just_one_file']
    self.assertItemsEqual(self.dsn.filter(t), expected)
    
    t = ['f1', 'f2', 'f3']
    expected = ['f1', 'f2', 'f3']
    self.assertItemsEqual(self.dsn.filter(t), expected)
   
    t = ['f1', 'f2', 'f3']
    expected = ['f1', 'f3']
    self.assertItemsEqual(self.dsn.filter(iFiles = t, iIgnore = ['f2']), expected)
    
    t = ['f1', 'f2', 'f3']
    expected = ['f2', 'f3']
    self.assertItemsEqual(self.dsn.filter(iFiles = t, iOnly = ['f2', 'f3']), expected)

    t = ['f1', 'f2', 'f3']
    expected = ['f3']
    self.assertItemsEqual(self.dsn.filter(iFiles = t, iOnly = ['f2', 'f3'], iIgnore = ['f2']),
                          expected)

    t = ['dir1/f1', 'dir2/f2', 'dir3/f3', 'd4/f4']
    expected = ['dir1/f1', 'dir3/f3']
    self.assertItemsEqual(self.dsn.filter(iFiles = t, iOnly = ['dir',], iIgnore = ['f2']),
                          expected)
    
  def genTree(self, iTreeStruct):
    for i in iTreeStruct:
      head, tail = os.path.split(i)
      
      if not os.path.exists(os.getcwd() + head):
        os.makedirs(os.getcwd() + head)
        
      if tail:
        open(os.getcwd()+i, 'w').close()
    
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
    fileMain, dirMain = self.dsn.initMain()
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
    path, dsnName = self.dsn.getLocToBuildXml(os.getcwd()+'/src/f1')
    expectedPath = 'G:/repo/git/autohdl/test/resource'
    expectedDsnName = 'test'
    self.assertEqual(expectedPath, path)
    self.assertEqual(expectedDsnName, dsnName)
    shutil.rmtree('resource')
    shutil.rmtree('src')
    
  def test_getTree(self):
    tree = ['/project/dsn1/f1.v',
            '/project/dsn1/f2.v',
            '/project/dsn2/f1.v',
            '/project/dsn2/f2.v',
            '/project/dsn2/f2.fake',
            '/project/dsn3/',
            '/project/dsn4/f666',
            ]
    self.genTree(tree)
    pathDeps = [os.getcwd()+'/project']
    expected = ['G:/repo/git/autohdl/test/project/dsn1/f1.v',
                'G:/repo/git/autohdl/test/project/dsn1/f2.v',
                'G:/repo/git/autohdl/test/project/dsn2/f1.v',
                'G:/repo/git/autohdl/test/project/dsn2/f2.v']
    self.assertEqual(expected,
                     self.dsn.getTree(pathDeps,
                                      iIgnore = ['dsn4'],
                                      iOnly = ['\.v', '\.vhdl', '\.vm', '\.hdl']))
    shutil.rmtree('project')
    
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
#           'test_init1',
#           'test_init2',
#           'test_init3',
#           'test_init4',
           'test_search'
          ]

  suite = unittest.TestSuite(map(Tests, tests))
  unittest.TextTestRunner(verbosity=3).run(suite)  

if __name__ == '__main__':
#  unittest.main()
#  suite = unittest.TestSuite()
#  suite.addTest(Tests('test_init1'))
#  suite.addTest(Tests('test_init2'))
#  suite.addTest(Tests('test_init3'))
#  suite.addTest(Tests('test_init4'))
#  unittest.TextTestRunner().run(suite)
  runTests()

  
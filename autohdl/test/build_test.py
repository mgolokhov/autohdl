import unittest
import sys
import os
import shutil

try:
  sys.path.insert(0, '..')
  from autohdl.build import *
except ImportError:
  from autohdl.build import *


class Tests(unittest.TestCase):
  
  def setUp(self):
    if not os.path.exists('tmp_test_dir'):
      os.mkdir('tmp_test_dir')

  def tearDown(self):
    if os.path.exists('tmp_test_dir'):
       shutil.rmtree('tmp_test_dir')  
       
  def test_genPredef(self):
    genPredef(iPath = 'tmp_test_dir', iDsnName = 'MegaDsn')
    f = open('tmp_test_dir/build.xml', 'r')
    contentActual = f.read()
    f.close()
    contentExpected = '''\
  <!--default build-->
  <wsp>
    <dsn id="MegaDsn">
      <dep></dep>
      <synthesis_ext>v; vm; vhd; vhdl</synthesis_ext>
      <implement_ext>ucf; edf; ndf; ngc</implement_ext>
    </dsn>
  </wsp>
  '''
    self.assertMultiLineEqual(contentExpected, contentActual)
       
  def test_getDeps(self):
    t = '''
    <wsp>
    <dsn id = "some">
    <dep>.</dep>
    <dep>..</dep>
    <dep>shit</dep>
    </dsn>
    <dsn id = "myDesign">
    <dep>..</dep>
    </dsn>
    <dsn id = "dsn666">
     <dep>shit</dep>
    </dsn>
    </wsp>
    '''
    buildFile = os.getcwd()+'/tmp_test_dir/resource/build.xml'
    if not os.path.exists('tmp_test_dir/resource/'):
      os.makedirs('tmp_test_dir/resource/')
    
    f = open(buildFile, 'w')
    f.write(t)
    f.close()
    
    dsnName = 'myDesign'
    expected = {u'myDesign': [os.path.abspath(os.getcwd()+'/..').replace('\\','/')],
                u'some': [os.path.abspath(os.getcwd()+'/.').replace('\\','/'),
                          os.path.abspath(os.getcwd()+'/..').replace('\\','/')]}
    
    self.assertDictEqual(expected, getDeps(iDsnName = dsnName, iBuildFile = buildFile))

  def test_getDeps2(self):
    t = '''
  <!--default build-->
  <wsp>
    <dsn id="masker">
      <dep>../../hdl_dev/cores</dep>
      <dep>curtain</dep>
      <synthesis_ext>v; vm; vhd; vhdl</synthesis_ext>
      <implement_ext>ucf; edf; ndf; ngc</implement_ext>
    </dsn>
  </wsp>
      '''
    buildFile = os.getcwd()+'/tmp_test_dir/masker/resource/build.xml'
    if not os.path.exists('tmp_test_dir/masker/resource'):
      os.makedirs('tmp_test_dir/masker/resource')
    if not os.path.exists('tmp_test_dir/curtain'):
      os.makedirs('tmp_test_dir/curtain')

    f = open(buildFile, 'w')
    f.write(t)
    f.close()
    
    dsnName = 'masker'
    expected = {'masker':[os.getcwd().replace('\\','/')+'/tmp_test_dir/curtain']}
    self.assertDictEqual(expected, getDeps(iDsnName = dsnName, iBuildFile = buildFile))  
    
    
  def test_getDeps3(self):
    t = '''
  <!--default build-->
  <wsp>
    <dsn id="curtain">
      <dep></dep>
      <synthesis_ext>v; vm; vhd; vhdl</synthesis_ext>
      <implement_ext>ucf; edf; ndf; ngc</implement_ext>
    </dsn>
  </wsp>
  '''
    buildFile = os.getcwd()+'/tmp_test_dir/resource/build.xml'
    if not os.path.exists('tmp_test_dir/resource/'):
      os.makedirs('tmp_test_dir/resource/')  
    f = open(buildFile, 'w')
    f.write(t)
    f.close()
    
    dsnName = 'curtain'
    expected = {'curtain':[]}
    self.assertDictEqual(expected, getDeps(iDsnName = dsnName, iBuildFile = buildFile))  
    
    
  def test_getSrcExtensions(self):
    t = '''
    <wsp>
      <synthesis_ext>v;vm;</synthesis_ext>
      <dsn id = "some">
        <dep></dep>
      </dsn>
    </wsp>
    '''
    f = open('tmp_test_dir/build.xml', 'w')
    f.write(t)
    f.close()
    expected = ['v', 'vm']
    actual = getSrcExtensions(iTag='synthesis_ext', iBuildFile='tmp_test_dir/build.xml')
    self.assertEqual(expected, actual)
    
  def test_getSrcExtensions2(self):
    t = '''
    <wsp>
      <dsn id = "some">
        <synthesis_ext>v;vm;</synthesis_ext>
        <dep></dep>
      </dsn>
    </wsp>
    '''
    f = open('tmp_test_dir/build.xml', 'w')
    f.write(t)
    f.close()
    expected = ['v', 'vm']
    actual = getSrcExtensions(iTag='synthesis_ext', iBuildFile='tmp_test_dir/build.xml')
    self.assertEqual(expected, actual)
    
  def test_getSrcExtensions3(self):
    t = '''
    <wsp>
      <dsn id = "some">
        <implement_ext>ngc </implement_ext>
        <dep></dep>
      </dsn>
    </wsp>
    '''
    f = open('tmp_test_dir/build.xml', 'w')
    f.write(t)
    f.close()
    expected = [i.strip() for i in gSYN_EXT.split(';')]
    actual = getSrcExtensions(iTag='synthesis_ext', iBuildFile='tmp_test_dir/build.xml')
    self.assertEqual(expected, actual)
    
  def test_getSrcExtensions4(self):
    t = '''
    <wsp>
      <dsn id = "some">
        <implement_ext>ngc ; edf</implement_ext>
        <dep></dep>
      </dsn>
    </wsp>
    '''
    f = open('tmp_test_dir/build.xml', 'w')
    f.write(t)
    f.close()
    expected = ['ngc', 'edf']
    actual = getSrcExtensions(iTag='implement_ext', iBuildFile='tmp_test_dir/build.xml')
    self.assertEqual(expected, actual)
     
  def test_getSrcExtensions5(self):
    expected = ''
    actual = getSrcExtensions(iTag='fake_ext', iBuildFile='tmp_test_dir/build.xml')
    self.assertEqual(expected, actual)
    
        
def runTests():
  logging.disable(logging.ERROR)
  tests = [
           'test_genPredef',
           'test_getDeps',
           'test_getDeps2',
           'test_getDeps3',
           'test_getSrcExtensions',
           'test_getSrcExtensions2',
           'test_getSrcExtensions3',
           'test_getSrcExtensions4',
           'test_getSrcExtensions5'
          ]

  suite = unittest.TestSuite(map(Tests, tests))
  unittest.TextTestRunner(verbosity=3).run(suite)  
      
if __name__ == '__main__':
#  unittest.main()
  runTests()
  
  
import sys
import os
import shutil
import unittest

try:
  sys.path.insert(0, '..')
  from synthesis import *
  from hdlLogger import *
except ImportError:
  from autohdl.synthesis import *
  from autohdl.hdlLogger import *

class Tests(unittest.TestCase):
  if not os.path.exists('tmp_test_dir'):
    os.mkdir('tmp_test_dir')
  
  def tearDown(self):
    if os.path.exists('tmp_test_dir'):
      shutil.rmtree('tmp_test_dir')
        
  def test_mergeSrc1(self):
    src = ['d1/f1', 'd1/f2', 'd2/f1', 'd2/f2']
    script = ['#lets party begin',
              'add_file "d1/f2"',
              '# add_file  "d2/f2"',
              'add_file "d3/f1"',
              '# comment'
              ]
    
    expectedSrc = ['d1/f1', 'd2/f1']
    expectedScript = [
                      '#lets party begin',
                      'add_file "d1/f2"',
                      '# add_file  "d2/f2"',
                      '# add_file "d3/f1" WAS DELETED',
                      'add_file "d1/f1"',
                      'add_file "d2/f1"',
                      '# comment'
                      ]
    merge(src, script, 'TopModule')
    self.assertListEqual(expectedSrc, src)
    self.assertListEqual(expectedScript, script)
  
  def test_synchTopModule(self):
    script = ['really no matter']
    num = 0;
    line = 'does not match'
    self.assertEqual(None, synchTopModule(script, 'topModule', num, line))
    expectedScript = ['really no matter']
    self.assertListEqual(expectedScript, script)

    script = ['really no matter', 'should be replaced']
    num = 1;
    line = ' set_option  -top_module  "zaebis"'
    self.assertTrue(synchTopModule(script, 'topModule', num, line))
    expectedScript = ['really no matter', 'set_option -top_module "topModule"']
    self.assertListEqual(expectedScript, script)
      
  def test_synchResultFile(self):
    script = ['really no matter']
    num = 0;
    line = 'does not match'
    self.assertFalse(synchResultFile(script, 'topModule', num, line))
    expectedScript = ['really no matter']
    self.assertListEqual(expectedScript, script)

    script = ['really no matter', 'should be replaced']
    num = 1;
    line = ' project  -result_file  "zaebis"'
    self.assertEqual(True, synchResultFile(script, 'topModule', num, line))
#    resultFile = '%s/%s' % (os.getcwd(), '../synthesis/topModule.edf')
#    resultFile = os.path.abspath(resultFile).replace('\\','/')
    resultFile = '../synthesis/topModule.edf'
    expectedScript = ['really no matter', 'project -result_file "{0}"'.format(resultFile)]
    self.assertListEqual(expectedScript, script)

  def test_synchSrcFile(self):
    src = []
    script = []
    num = 0
    line = 'no match'
    self.assertFalse(synchSrcFile(src, script, num, line))

    src = ['no files']
    script = ['no care', 'replace me']
    num = 1
    line = 'add_file "d1/f1"'
    self.assertTrue(synchSrcFile(src, script, num, line))
    expectedScript = ['no care', '# add_file "d1/f1" WAS DELETED']
    self.assertListEqual(expectedScript, script)

    src = ['d1/f1']
    script = ['no care', 'same']
    num = 1
    line = 'add_file "d1/f1"'
    self.assertTrue(synchSrcFile(src, script, num, line))
    expectedScript =  ['no care', 'same']
    self.assertListEqual(expectedScript, script)
  
  
  @unittest.skip("BUGAGA: unfinished")
  def test_genScript(self):
    if not os.path.exists('tmp_test_dir/script'):
      os.makedirs('tmp_test_dir/script')
    os.chdir('tmp_test_dir/script')
    content = '''\

  #device options
  set_option -technology SPARTAN3E
  set_option -part XC3S1200E
  set_option -package FG320
  set_option -speed_grade -5
  
  #compilation/mapping options
  set_option -default_enum_encoding default
  set_option -symbolic_fsm_compiler true
  set_option -resource_sharing true
  
  #map options
  set_option -top_module "mega_top"
  set_option -disable_io_insertion false
  set_option -frequency auto
  set_option -pipe 1
  set_option -retiming 0
  set_option -fixgatedclocks 3
  set_option -fixgeneratedclocks 3
  set_option -par_use_xflow 0
  set_option -fanout_limit 10000
  set_option -update_models_cp false
  set_option -verification_mode false
  set_option -vlog_std sysv
  set_option -hier_report 1
  set_option -island_num_paths 10
  set_option -island_group_range 0.5
  set_option -island_global_range 0.5
  set_option -enable_nfilter 0
  set_option -feedthrough 0
  set_option -constant_prop 0
  set_option -level_hierarchy 0
  set_option -auto_constrain_io 0
  set_option -dup 0
  set_option -run_prop_extract 1
  set_option -write_vif 1
  set_option -write_apr_constraint 1
  set_option -synthesis_onoff_pragma 0
  set_option -no_sequential_opt 0
  set_option -use_fsm_explorer 0
  
  #simulation options
  set_option -write_vhdl false
  set_option -write_verilog true
  project -result_format "edif"
  project -result_file "../synthesis/mega_top.edf"    
    '''
    
    genScript(iTopModule = 'mega_top')
    
    f = open('synthesis.prj', 'r')
    res = f.read()
    f.close()
    self.assertMultiLineEqual(content, res)
    
    os.chdir('../..')
    
    
  def test_getSrcFromFileSys(self):
    if not os.path.exists('tmp_test_dir/src'): os.makedirs('tmp_test_dir/src')
    if not os.path.exists('tmp_test_dir/.svn'): os.makedirs('tmp_test_dir/.svn')
    if not os.path.exists('tmp_test_dir/src/.svn'): os.makedirs('tmp_test_dir/src/.svn')
    if not os.path.exists('tmp_test_dir/script'): os.makedirs('tmp_test_dir/script')
    open('tmp_test_dir/src/should1.v', 'w').close()
    open('tmp_test_dir/src/should1.vm', 'w').close()
    open('tmp_test_dir/src/should1.vhdl', 'w').close()
    open('tmp_test_dir/src/nope.txt', 'w').close()
    open('tmp_test_dir/src/v', 'w').close()
    open('tmp_test_dir/src/.svn/nope.v', 'w').close()
    open('tmp_test_dir/.svn/nope.v', 'w').close()
    open('tmp_test_dir/nope.v', 'w').close()
    open('tmp_test_dir/src.v', 'w').close()
    os.chdir('tmp_test_dir/script')
    import structure
    dsn = structure.Design(iPath = '..', iInit = False, iGen = False)
    filesPath = os.path.abspath(os.getcwd()+'/../src').replace('\\','/')
    expected = [filesPath+'/should1.v',
                filesPath+'/should1.vm',
                filesPath+'/should1.vhdl']
    os.chdir('../..')
    self.assertEqual(set(expected), set(getSrcFromFileSys(iDsn = dsn)))


def runTests():
  consoleHandler.setLevel(logging.ERROR)
  tests = [
           'test_mergeSrc1', 
           'test_synchTopModule',
           'test_synchResultFile',
           'test_synchSrcFile',
           'test_genScript',
           'test_getSrcFromFileSys'
          ]

  suite = unittest.TestSuite(map(Tests, tests))
  unittest.TextTestRunner(verbosity=3).run(suite)  

if __name__ == '__main__':
#  unittest.main()
  runTests()
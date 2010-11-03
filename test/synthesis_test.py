import sys
import os
import shutil
import unittest


sys.path.insert(0, '..')
import synthesis as s
from hdlLogger import *
#consoleHandler.setLevel(logging.DEBUG)

class Tests(unittest.TestCase):
  def test_mergeSrc1(self):
    '''
    tests synchSrcFile
    '''
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
    s.mergeSrc(src, script, 'TopModule')
    self.assertListEqual(expectedSrc, src)
    self.assertListEqual(expectedScript, script)
  
  def test_synchTopModule(self):
    script = ['really no matter']
    num = 0;
    line = 'does not match'
    self.assertFalse(s.synchTopModule(script, 'topModule', num, line))
    expectedScript = ['really no matter']
    self.assertListEqual(expectedScript, script)

    script = ['really no matter', 'should be replaced']
    num = 1;
    line = ' set_option  -top_module  "zaebis"'
    self.assertTrue(s.synchTopModule(script, 'topModule', num, line))
    expectedScript = ['really no matter', 'set_option -top_module "topModule"']
    self.assertListEqual(expectedScript, script)
      
  def test_synchResultFile(self):
    script = ['really no matter']
    num = 0;
    line = 'does not match'
    self.assertFalse(s.synchResultFile(script, 'topModule', num, line))
    expectedScript = ['really no matter']
    self.assertListEqual(expectedScript, script)

    script = ['really no matter', 'should be replaced']
    num = 1;
    line = ' set_option  -result_file  "zaebis"'
    self.assertTrue(s.synchResultFile(script, 'topModule', num, line))
    resultFile = '%s/%s' % (os.getcwd(), '../synthesis/topModule.edf')
    resultFile = os.path.abspath(resultFile).replace('\\','/')
    expectedScript = ['really no matter', 'set_option -result_file "{0}"'.format(resultFile)]
    self.assertListEqual(expectedScript, script)

  def test_synchSrcFile(self):
    src = []
    script = []
    num = 0
    line = 'no match'
    self.assertFalse(s.synchSrcFile(src, script, num, line))

    src = ['no files']
    script = ['no care', 'replace me']
    num = 1
    line = 'add_file "d1/f1"'
    self.assertTrue(s.synchSrcFile(src, script, num, line))
    expectedScript = ['no care', '# add_file "d1/f1" WAS DELETED']
    self.assertListEqual(expectedScript, script)

    src = ['d1/f1']
    script = ['no care', 'same']
    num = 1
    line = 'add_file "d1/f1"'
    self.assertTrue(s.synchSrcFile(src, script, num, line))
    expectedScript =  ['no care', 'same']
    self.assertListEqual(expectedScript, script)
    
  def test_genScript(self):
    
    self.assertRaises(s.SynthesisException, s.genScript)
    
    if not os.path.exists('resource'):
      os.mkdir('resource')
    f = open('./resource/synthesis_default', 'w')
    f.write('''\

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
  set_option -top_module "{top_module}"
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
  project -result_file "{result}"    
    ''')
    f.close()
    
    if not os.path.exists('script'):
      os.mkdir('script')
    os.chdir('script')

    self.assertRaises(s.SynthesisException, s.genScript)
    



      
if __name__ == '__main__':
  unittest.main()
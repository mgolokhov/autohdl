import sys
import unittest

try:
  sys.path.append('..')
  from implement import *
except ImportError:
  from autohdl.implement import *


class Tests(unittest.TestCase):
  @unittest.skip("BUGAGA: unfinished")
  def test_mergeSrc(self):
    srcFileSys = ['fileSame1',
                  'fileSame2',
                  'fileNew'
                  ]
    srcScript = ['xfile add "fileSame1"',
                 '  xfile add "fileSame2"',
                 'xfile add "fileDeleted"',
                 '  # xfile add "fileNone"'        
                 ]
    expected = [['xfile add "fileSame1"', 'same'],
                ['  xfile add "fileSame2"', 'same'],
                ['# xfile add "fileDeleted" DELETED', 'del'],
                ['  # xfile add "fileNone"', 'comment'],
                ['xfile add "fileNew"', 'new']
                ]
    actual = mergeSrc(srcFileSys, srcScript) 
    
    self.assertItemsEqual(expected, actual)
    
    
    srcFileSys=['G:/hdl/cheapCtrl/script/../resource/top.ucf',
                'G:/hdl/cheapCtrl/script/../synthesis/top.edf']
    srcScript=['# xfile add "{synthesis_result_top}" DELETED',
               '# xfile add "{ucf}" DELETED',
               'xfile add "G:/hdl/cheapCtrl/script/../synthesis/top.edf"',
               'xfile add "G:/hdl/cheapCtrl/script/../resource/cheapCtrl.ucf"']
    expected = [['# xfile add "{synthesis_result_top}" DELETED', 'comment'],
                ['# xfile add "{ucf}" DELETED', 'comment'],
                ['xfile add "G:/hdl/cheapCtrl/script/../synthesis/top.edf"', 'same'],
                ['# xfile add "G:/hdl/cheapCtrl/script/../resource/cheapCtrl.ucf" DELETED', 'del'],
                ['xfile add "G:/hdl/cheapCtrl/script/../resource/top.ucf"', 'new'],
                ]
    self.maxDiff = None
    actual = mergeSrc(srcFileSys, srcScript) 
    self.assertItemsEqual(expected, actual)
    
  @unittest.skip("BUGAGA: unfinished")
  def test_getPureFile(self):
    t = r'xfile add "asss_/asd/dasds\dasds/sads343"   # wassup'
    expected = 'asss_/asd/dasds\dasds/sads343'
    actual = getPureFile(t)
    self.assertEqual(actual, expected)
    
    t = r'xfile add "asss_/asd/dasds\dasds/sads343"#wassup'
    expected = 'asss_/asd/dasds\dasds/sads343'
    actual = getPureFile(t)
    self.assertEqual(actual, expected)

    t = r'xfile add "asss_/asd/dasds sfd\dasds/sads343"#wassup'
    expected = 'asss_/asd/dasds sfd\dasds/sads343'
    actual = getPureFile(t)
    self.assertEqual(actual, expected)
    
    t = r'xfile add "G:/hdl/cheapCtrl/script/../synthesis/top.edf"'
    expected = 'G:/hdl/cheapCtrl/script/../synthesis/top.edf'
    actual = getPureFile(t)
    self.assertEqual(actual, expected)
  
  @unittest.skip("BUGAGA: unfinished")  
  def test_refreshParams(self):
    impl = '''
    project new ../implement/{prj_name}.ise
    
    xfile add "synthesis_result_top"
    xfile add "ucf"
    
    project set family "{family}"
    project set device "device"
    project set package "package"
    project set speed "-5"
    project set top_level_module_type  "EDIF"
    project set generated_simulation_language "Other Mixed"
    project set "Preferred Language" Verilog
    project set "FPGA Start-Up Clock" "JTAG Clock"
    process run "Generate Programming File"
    project close
    '''
    
    syn = '''
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
    project -result_file "result_filizeee"
    '''
    
    #BUGAGA: not yet
    refreshParams(syn, impl, gSynToImpl) 
    

def runTests():
  tests = [
           'test_refreshParams',
           'test_getPureFile',
           'test_mergeSrc'
          ]

  suite = unittest.TestSuite(map(Tests, tests))
  unittest.TextTestRunner(verbosity=2).run(suite)    
    

if __name__ == '__main__':
#  unittest.main()
  runTests()


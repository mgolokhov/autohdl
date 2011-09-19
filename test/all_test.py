import sys
import unittest
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/verilog')
import func_test
import vparser_test
import vpreprocessor_test

if __name__ == '__main__':


  loader = unittest.TestLoader()
  suite = loader.loadTestsFromModule(vpreprocessor_test)
  suite.addTests(loader.loadTestsFromModule(vparser_test))
  suite.addTests(loader.loadTestsFromModule(func_test))

  runner = unittest.TextTestRunner(verbosity=2)
  result = runner.run(suite)
  print result.wasSuccessful()
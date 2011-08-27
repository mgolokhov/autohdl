import sys
import unittest

sys.path.insert(0, '../..')
from verilog.preprocessor import *

class ATest(unittest.TestCase):
  def test(self):
    actual = Preprocessor('nested_ifdef').result
    expacted = '''
    $display("1A");

        $display("2A");

            $display("3AELSE");

'''
    self.assertMultiLineEqual(expacted, actual)


if __name__ == '__main__':
  unittest.main()

  
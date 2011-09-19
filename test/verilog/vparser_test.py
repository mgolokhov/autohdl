import os
import unittest
import sys

sys.path.append('../..')
from verilog.vparser import Parser


class ParserTest(unittest.TestCase):
  @classmethod
  def setUpClass(self):
    self.cwd_was = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

  @classmethod
  def tearDown(self):
    os.chdir(self.cwd_was)

  def test_parser(self):
    with open('in/parser/serial_neuron_core.v') as f:
      actual = Parser({'file_path': 'fake_path',
                       'preprocessed': f.read()}).parsed
    expected = {'serial_neuron_core': {'path': 'fake_path',
                                       'instances': {'serial_subs',
                                                     'serial_mult',
                                                     'serial_summ',
                                                     'serial_summ_n'}},
                'second_in_one_file': {'instances': {'as'},
                                       'path': 'fake_path'}}
    self.assertEqual(actual, expected)



if __name__ == '__main__':
  unittest.main()
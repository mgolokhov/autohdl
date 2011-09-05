import os
import shutil
import unittest
import sys
sys.path.insert(0, '../..')

from verilog import get_instances, cache

cache.CACHE_PATH = 'tmp/'


class FuncTest(unittest.TestCase):
  def setUp(self):
    if not os.path.exists('tmp'):
      os.mkdir('tmp')

#  def tearDown(self):
#    while True:
#      try:
#        shutil.rmtree('tmp')
#        return
#      except WindowsError:
#        pass

  def test_get_instances(self):
    get_instances(r'in/parser/serial_neuron_core.v')
    with open('tmp/in_parser_serial_neuron_core_v') as f:
      actual = f.read()
    with open('gold/func/in_parser_serial_neuron_core_v') as f:
      expected = f.read()
    self.assertMultiLineEqual(actual, expected)

    
if __name__ == '__main__':
  unittest.main()

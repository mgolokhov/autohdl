import os
import unittest
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../..')
from verilog import get_instances, cache
import lib.yaml as yaml


class FuncTest(unittest.TestCase):

  @classmethod
  def setUpClass(self):
    self.was = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cache.CACHE_LOAD = False
    cache.CACHE_PATH = os.path.dirname(os.path.abspath(__file__))+'/in/tmp'
    if not os.path.exists(cache.CACHE_PATH):
      os.mkdir(cache.CACHE_PATH)
    self.maxDiff = None

  @classmethod
  def tearDownClass(self):
    os.chdir(self.was)

  def test_get_instances(self):
    for f in os.listdir(os.path.dirname(os.path.abspath(__file__))+'/in/func'):
      get_instances(os.path.dirname(os.path.abspath(__file__))+'/in/func/'+f)
      with open(os.path.dirname(os.path.abspath(__file__))+'/gold/func/'+f+'cache') as af:
        expected = yaml.load(af)
      with open(os.path.dirname(os.path.abspath(__file__))+'/in/tmp/'+f+'cache') as af:
        actual = yaml.load(af)
      self.assertEqual(actual, expected)

      
#  def test(self):
#    self.assertFalse(True)

    
if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(FuncTest)
  res = unittest.TextTestRunner(verbosity=2).run(suite)
  print res.wasSuccessful()
  
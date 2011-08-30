import unittest

from hdlLogger import *



sys.path.insert(0, '../..')
from verilog.preprocessor import *

class Atest(unittest.TestCase):
  def setUp(self):
    self.maxDiff = None

  def compare(self, expected, actual):
    actual = [i.strip() for i in actual.splitlines() if i]
    expected = [i.strip() for i in expected.splitlines() if i]
    self.assertSequenceEqual(expected, actual)


  def test_nested_ifdef(self):
    actual   = Preprocessor('in/nested_ifdef.v').preprocessed
    with open('gold/nested_ifdef.v') as f:
      expected = f.read()
    self.compare(expected, actual)

  def test_nested_ifdef2(self):
    actual   = Preprocessor('in/nested_ifdef2.v').preprocessed
    with open('gold/nested_ifdef2.v') as f:
      expected = f.read()
    self.compare(expected, actual)

  def test_nested_ifdef3(self):
    actual   = Preprocessor('in/nested_ifdef3.v').preprocessed
    with open('gold/nested_ifdef3.v') as f:
      expected = f.read()
    self.compare(expected, actual)

  def test_nested_ifdef4(self):
    actual   = Preprocessor('in/nested_ifdef4.v').preprocessed
    with open('gold/nested_ifdef4.v') as f:
      expected = f.read()
    self.compare(expected, actual)

  def test_nested_ifdef5(self):
    actual   = Preprocessor('in/nested_ifdef5.v').preprocessed
    with open('gold/nested_ifdef5.v') as f:
      expected = f.read()
    self.compare(expected, actual)

  def test_nested_ifdef6(self):
    actual   = Preprocessor('in/nested_ifdef6.v').preprocessed
    with open('gold/nested_ifdef6.v') as f:
      expected = f.read()
    self.compare(expected, actual)

  def test_nested_ifdef7(self):
    actual   = Preprocessor('in/nested_ifdef7.v').preprocessed
    with open('gold/nested_ifdef7.v') as f:
      expected = f.read()
    self.compare(expected, actual)

  def test_macro_resolve(self):
    actual = Preprocessor('in/macro_resolve.v').preprocessed
    with open('gold/macro_resolve.v') as f:
      expected = f.read()
    self.compare(expected, actual)

  def test_include(self):
    actual = Preprocessor('in/incl_top.v').preprocessed
    with open('gold/incl.v') as f:
      expected = f.read()
    self.compare(expected, actual)

  def test_removeComments(self):
    actual = Preprocessor('in/comments.v').preprocessed
    with open('gold/comments.v') as f:
      expected = f.read()
    self.compare(expected, actual)


if __name__ == '__main__':
  logging.disable(logging.CRITICAL)
#  tests = [
#           'test_nested_ifdef',
#           'test_nested_ifdef2',
#           'test_nested_ifdef3',
#           'test_nested_ifdef4',
#           'test_nested_ifdef5',
#           'test_macro_resolve',
#           'test_include',
#           'test_removeComments',
#           ]
#  suite = unittest.TestSuite(map(Atest, tests))
#  unittest.TextTestRunner(verbosity=2).run(suite)
  unittest.main()

import unittest

from autohdl.hdlLogger import *

logging.disable(logging.CRITICAL)

import sys

sys.path.insert(0, '../..')
from autohdl.verilog.vpreprocessor import *

class PreprocessorTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.cwd_was = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    @classmethod
    def tearDownClass(self):
        os.chdir(self.cwd_was)

    def compare(self, expected, actual):
        actual = [i.strip() for i in actual.splitlines() if i]
        expected = [i.strip() for i in expected.splitlines() if i]
        self.assertSequenceEqual(expected, actual)


    def test_nested_ifdef(self):
        actual = Preprocessor('in/nested_ifdef.v').preprocessed
        with open('gold/nested_ifdef.v') as f:
            expected = f.read()
        self.compare(expected, actual)

    def test_nested_ifdef2(self):
        actual = Preprocessor('in/nested_ifdef2.v').preprocessed
        with open('gold/nested_ifdef2.v') as f:
            expected = f.read()
        self.compare(expected, actual)

    def test_nested_ifdef3(self):
        actual = Preprocessor('in/nested_ifdef3.v').preprocessed
        with open('gold/nested_ifdef3.v') as f:
            expected = f.read()
        self.compare(expected, actual)

    def test_nested_ifdef4(self):
        actual = Preprocessor('in/nested_ifdef4.v').preprocessed
        with open('gold/nested_ifdef4.v') as f:
            expected = f.read()
        self.compare(expected, actual)

    def test_nested_ifdef5(self):
        actual = Preprocessor('in/nested_ifdef5.v').preprocessed
        with open('gold/nested_ifdef5.v') as f:
            expected = f.read()
        self.compare(expected, actual)

    def test_nested_ifdef6(self):
        actual = Preprocessor('in/nested_ifdef6.v').preprocessed
        with open('gold/nested_ifdef6.v') as f:
            expected = f.read()
        self.compare(expected, actual)

    def test_nested_ifdef7(self):
        actual = Preprocessor('in/nested_ifdef7.v').preprocessed
        with open('gold/nested_ifdef7.v') as f:
            expected = f.read()
        self.compare(expected, actual)

    def test_ifdef(self):
        actual = Preprocessor('in/ifdef.v').preprocessed
        with open('gold/ifdef.v') as f:
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

    def test_include1(self):
        actual = Preprocessor('in/incl0').preprocessed
        with open('gold/incl0') as f:
            expected = f.read()
        self.compare(expected, actual)

    def test_removeComments(self):
        actual = Preprocessor('in/comments.v').preprocessed
        with open('gold/comments.v') as f:
            expected = f.read()
        self.compare(expected, actual)

    def test_preprocessor(self):
        actual = Preprocessor('in/preprocessor/dspuva16.v').preprocessed
        with open('gold/preprocessor/dspuva16.v') as f:
            expected = f.read()
        self.compare(expected, actual)


if __name__ == '__main__':
    unittest.main()

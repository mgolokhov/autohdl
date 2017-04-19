import unittest
import sys
import os

sys.path.insert(1, '../../verilog')
from vpreprocessor import Preprocessor

class PreprocessorTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.cwd_was = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    @classmethod
    def tearDownClass(self):
        os.chdir(self.cwd_was)

    def show_repr(self, actual, expected):
        return "\n\n" \
               "RESULT:\n{raw_actual}\n" \
               "EXPECTED:\n{raw_expected}\n\n" \
               "RESULT REPR:\n{repr_actual}\n" \
               "EXPECTED REPR:\n{repr_expected}" \
               "\n".format(raw_actual=actual,
                           raw_expected=expected,
                           repr_actual=repr(actual),
                           repr_expected=repr(expected))

    def run_test(self, fname_in, fname_exp, cfg=None):
        if cfg:
            p = Preprocessor(includes=cfg.includes, defines=cfg.defines)
        else:
            p = Preprocessor()
        with open(fname_in) as f:
            txt = f.read()
        with open(fname_exp) as f:
            expected = f.read()
        actual = p.prepr_txt(txt)
        self.assertEqual(actual, expected, msg=self.show_repr(actual, expected))

    def test_nested_ifdef(self):
        self.run_test('in/nested_ifdef.v', 'gold/nested_ifdef.v')

    def test_nested_ifdef2(self):
        self.run_test('in/nested_ifdef2.v', 'gold/nested_ifdef2.v')

    def test_nested_ifdef3(self):
        self.run_test('in/nested_ifdef3.v', 'gold/nested_ifdef3.v')

    def test_nested_ifdef4(self):
        self.run_test('in/nested_ifdef4.v', 'gold/nested_ifdef4.v')

    def test_nested_ifdef5(self):
        self.run_test('in/nested_ifdef5.v', 'gold/nested_ifdef5.v')

    def test_nested_ifdef6(self):
        self.run_test('in/nested_ifdef6.v', 'gold/nested_ifdef6.v')

    def test_nested_ifdef7(self):
        self.run_test('in/nested_ifdef7.v', 'gold/nested_ifdef7.v')

    def test_ifdef(self):
        self.run_test('in/nested_ifdef.v', 'gold/nested_ifdef.v')

    def test_macro_resolve(self):
        self.run_test('in/macro_resolve.v', 'gold/macro_resolve.v')

    def test_include(self):
        cfg = Preprocessor(includes=['in'])
        self.run_test('in/incl_top.v', 'gold/incl.v', cfg)

    def test_include1(self):
        cfg = Preprocessor(includes=['in'])
        self.run_test('in/incl0', 'gold/incl0', cfg)

    def test_removeComments(self):
        self.run_test('in/comments.v', 'gold/comments.v')

    def test_preprocessor(self):
        self.run_test('in/preprocessor/dspuva16.v', 'gold/preprocessor/dspuva16.v')



if __name__ == '__main__':
    unittest.main()

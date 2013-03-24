import unittest
import os
import sys
import logging

from autohdl.hdlManager import kungfu


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # logging.disable(logging.ERROR)
        cls.was_dir = os.getcwd().replace('\\', '/')

    def setUp(self):
        sys.argv = ['']
        os.chdir(self.was_dir)

    # priority in searching top module name:
    #   1 name set by command line (-top <top_name>)
    #   2 name of python script (top_name.py)
    #   3 name set in python script (top="<top_name>")
    #   4 name in build.yaml (top:<top_name>)
    # priority in searching ucf file:
    #   1 same name as top module
    #   2 name in python script <ucf_filename>[.ucf]
    #   3 path in build.yaml (absolute or relative path)
    #   4 any single ucf file in "src" folder
    def test_valid_top_from_cl_and_same_ucf(self):
        os.chdir('test_data_hdlManager/dsn1/script')
        sys.modules['__main__'].__file__ = 'top_py_script_filename.py'
        sys.argv += '-debug -top top_command_line'.split()
        res = kungfu(top='top_py_script_content',
                     ucf='top_py_script_content')
        self.assertEqual(res['top'], 'top_command_line')
        self.assertEqual(res['ucf'],
                         self.was_dir + '/test_data_hdlManager/dsn1/src/top_command_line.ucf')

    def test_valid_top_from_py_script_filename_and_same_ucf(self):
        os.chdir('test_data_hdlManager/dsn1/script')
        sys.modules['__main__'].__file__ = 'top_py_script_filename.py'
        sys.argv += '-debug -top no_match_top_command_line'.split()
        res = kungfu(top='top_py_script_content',
                     ucf='top_py_script_content')
        self.assertEqual(res['top'], 'top_py_script_filename')
        self.assertEqual(res['ucf'],
                         self.was_dir + '/test_data_hdlManager/dsn1/src/top_py_script_filename.ucf')

    def test_valid_top_in_py_script_content_and_same_ucf(self):
        os.chdir('test_data_hdlManager/dsn1/script')
        sys.modules['__main__'].__file__ = 'no_match_top_py_script_filename.py'
        sys.argv += '-debug -top no_match_top_command_line'.split()
        res = kungfu(top='top_py_script_content',
                     ucf='top_py_script_content')
        self.assertEqual(res['top'], 'top_py_script_content')
        self.assertEqual(res['ucf'],
                         self.was_dir + '/test_data_hdlManager/dsn1/src/top_py_script_content.ucf')

    def test_valid_top_in_build_yaml_and_same_ucf(self):
        os.chdir('test_data_hdlManager/dsn1/script')
        sys.modules['__main__'].__file__ = 'no_match_top_py_script_filename.py'
        sys.argv += '-debug -top no_match_top_command_line'.split()
        res = kungfu(top='no_match_top_py_script_content',
                     ucf='top_py_script_content')
        self.assertEqual(res['top'], 'top_build_yaml')
        print res['ucf']

    def test_undefined_top_and_ucf_from_py_script_content(self):
        os.chdir('test_data_hdlManager/dsn2/script')
        sys.modules['__main__'].__file__ = 'no_match_top_py_script_filename.py'
        sys.argv += '-debug -top no_match_top_command_line'.split()
        res = kungfu(top='no_match_top_py_script_content',
                     ucf='top_py_script_content')
        self.assertEqual(res['top'], '')
        self.assertEqual(res['ucf'],
                         self.was_dir + '/test_data_hdlManager/dsn2/src/top_py_script_content.ucf')

    def test_undefined_top_and_ucf_form_build_yaml(self):
        os.chdir('test_data_hdlManager/dsn2/script')
        sys.modules['__main__'].__file__ = 'no_match_top_py_script_filename.py'
        sys.argv += '-debug -top no_match_top_command_line'.split()
        res = kungfu(top='no_match_top_py_script_content')
        self.assertEqual(res['top'], '')
        self.assertEqual(res['ucf'],
                         self.was_dir + '/test_data_hdlManager/dsn2/src/top_build_yaml.ucf')

    def test_undefined_top_and_undefined_ucf_but_only_one_ucf(self):
        os.chdir('test_data_hdlManager/dsn3/script')
        sys.modules['__main__'].__file__ = 'no_match_top_py_script_filename.py'
        sys.argv += ['-debug']
        res = kungfu()
        self.assertEqual(res['top'], '')
        self.assertEqual(res['ucf'],
                         self.was_dir + '/test_data_hdlManager/dsn3/src/ucf_any_single_in_src.ucf')

    def test_undefined_top_and_undefined_ucf(self):
        os.chdir('test_data_hdlManager/dsn4/script')
        sys.modules['__main__'].__file__ = 'no_match_top_py_script_filename.py'
        sys.argv += ['-debug']
        res = kungfu()
        self.assertEqual(res['top'], '')
        self.assertEqual(res['ucf'], '')

if __name__ == '__main__':
    unittest.main()
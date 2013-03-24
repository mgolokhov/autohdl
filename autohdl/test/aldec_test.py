import re
import os
import shutil
import unittest

from autohdl.aldec import *


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.dir_was = os.path.abspath(os.getcwd())
        self.test_tmp = 'test_tmp'
        self.maxDiff = None

    def setUp(self):
        os.chdir(self.dir_was)
        if os.path.exists(self.test_tmp):
            shutil.rmtree(self.test_tmp)
        # precondition:
        # form some structure with src, constraints, netlists
        self.config = dict()
        self.config['hdlManager'] = dict()
        self.config['hdlManager']['debug'] = 'hardcore_test'
        self.config['hdlManager']['family'] = 'Spartan3E'
        self.config['hdlManager']['device'] = 'xc3s1200e'
        self.config['hdlManager']['package'] = 'fg320'
        self.config['hdlManager']['speed'] = '-5'

        self.config['structure'] = dict()
        self.config['structure']['mainSrc'] = []
        self.config['structure']['depSrc'] = []

    def test_2(self):
        shutil.copytree('test_data_aldec/test_2/input', self.test_tmp)
        os.chdir(os.path.join(self.test_tmp, 'dsn1', 'script'))
        aldec_root = (os.path.join(self.dir_was,
                                   self.test_tmp,
                                   'dsn1',
                                   'autohdl',
                                   'aldec'))
        self.config['structure']['depSrc'] = [os.path.join(self.dir_was, self.test_tmp, 'dsn2/src/f1_dsn2.v')]

        export(self.config)
        #
        # check existence of generated files
        #
        workspace_file = os.path.join(aldec_root, 'wsp.aws')
        self.assertTrue(os.path.exists(workspace_file),
                        'Cant find workspace file: ' + workspace_file)
        compile_file = (os.path.join(aldec_root, 'compile.cfg'))
        self.assertTrue(os.path.exists(compile_file),
                        'Cant find compite file: ' + compile_file)
        design_file = os.path.join(aldec_root, 'dsn1.adf')
        self.assertTrue(os.path.exists(design_file),
                        'Cant find design file: ' + design_file)
        # run python abs_path_to/aldec_run.py abs_path_to/current_directory abs_path_to/avhdl.exe
        # current_directory in script
        self.assertTrue(len(self.config['execution_fifo']) == 1,
                        "Expected one execution in fifo, got: " + str(len(self.config['execution_fifo'])))
        self.assertTrue(re.match('python\s+.*?aldec_run.py\s+.*?script\s+.*?avhdl.exe',
                                 self.config['execution_fifo'][0]),
                        'Expected format '
                        '"python abs_path_to/aldec_run.py abs_path_to/current_directory abs_path_to/avhdl.exe"\n'
                        'Got: ' + self.config['execution_fifo'][0])
        #
        # compare content of generated files
        #
        f = open(compile_file)
        content_compile_file = f.read()
        f = open(self.dir_was + '/test_data_aldec/test_2/result/autohdl/aldec/compile.cfg')
        expected_content_compile_file = f.read()
        self.assertMultiLineEqual(content_compile_file, expected_content_compile_file)

        f = open(workspace_file)
        content_workspace_file = f.read()
        f = open(self.dir_was + '/test_data_aldec/test_2/result/autohdl/aldec/wsp.aws')
        expected_content_workspace_file = f.read()
        self.assertMultiLineEqual(content_workspace_file, expected_content_workspace_file)

        f = open(design_file)
        content_design_file = f.read()
        content_design_file = re.sub('FAMILY=<function family at 0x\w+>',
                                     '',
                                     content_design_file)
        f = open(self.dir_was + '/test_data_aldec/test_2/result/autohdl/aldec/dsn1.adf')
        expected_content_design_file = f.read().format(abs_path_to_tmp_dir=self.dir_was + '\\' + self.test_tmp)
        expected_content_design_file = re.sub('FAMILY=<function family at 0x\w+>',
                                              '',
                                              expected_content_design_file)
        self.assertMultiLineEqual(content_design_file, expected_content_design_file)

    def test_3(self):
        shutil.copytree('test_data_aldec/test_3/input', self.test_tmp)
        os.chdir(os.path.join(self.test_tmp, 'cores/core1/script'))
        aldec_root = (os.path.join(self.dir_was,
                                   self.test_tmp,
                                   'cores',
                                   'core1',
                                   'autohdl',
                                   'aldec'))

        export(self.config)
        #
        # check existence of generated files
        #
        workspace_file = os.path.join(aldec_root, 'wsp.aws')
        self.assertTrue(os.path.exists(workspace_file),
                        'Cant find workspace file: ' + workspace_file)
        compile_file = (os.path.join(aldec_root, 'compile.cfg'))
        self.assertTrue(os.path.exists(compile_file),
                        'Cant find compite file: ' + compile_file)
        design_file = os.path.join(aldec_root, 'core1.adf')
        self.assertTrue(os.path.exists(design_file),
                        'Cant find design file: ' + design_file)
        # run python abs_path_to/aldec_run.py abs_path_to/current_directory abs_path_to/avhdl.exe
        # current_directory in script
        self.assertTrue(len(self.config['execution_fifo']) == 1,
                        "Expected one execution in fifo, got: " + str(len(self.config['execution_fifo'])))
        self.assertTrue(re.match('python\s+.*?aldec_run.py\s+.*?script\s+.*?avhdl.exe',
                                 self.config['execution_fifo'][0]),
                        'Expected format '
                        '"python abs_path_to/aldec_run.py abs_path_to/current_directory abs_path_to/avhdl.exe"\n'
                        'Got: ' + self.config['execution_fifo'][0])
        #
        # compare content of generated files
        #
        f = open(compile_file)
        content_compile_file = f.read()
        f = open(self.dir_was + '/test_data_aldec/test_3/result/autohdl/aldec/compile.cfg')
        expected_content_compile_file = f.read()
        self.assertMultiLineEqual(content_compile_file, expected_content_compile_file)

        f = open(workspace_file)
        content_workspace_file = f.read()
        f = open(self.dir_was + '/test_data_aldec/test_3/result/autohdl/aldec/wsp.aws')
        expected_content_workspace_file = f.read()
        self.assertMultiLineEqual(content_workspace_file, expected_content_workspace_file)

        f = open(design_file)
        content_design_file = f.read()
        content_design_file = re.sub('FAMILY=<function family at 0x\w+>',
                                     '',
                                     content_design_file)
        f = open(self.dir_was + '/test_data_aldec/test_3/result/autohdl/aldec/core1.adf')
        expected_content_design_file = f.read().format(abs_path_to_tmp_dir=self.dir_was + '\\' + self.test_tmp)
        expected_content_design_file = re.sub('FAMILY=<function family at 0x\w+>',
                                              '',
                                              expected_content_design_file)
        self.assertMultiLineEqual(content_design_file, expected_content_design_file)
        # self.debug(path=workspace_file)

    def adebug(self, path):
        import pprint
        pprint.pprint(self.config)
        import autohdl.toolchain as t
        aldec = t.Tool().get('avhdl_gui')
        subprocess.Popen(aldec + ' ' + path)

    # def tearDown(self):
    #     os.chdir(self.dir_was)
    #     if os.path.exists(self.test_tmp):
    #         shutil.rmtree(self.test_tmp)



if __name__ == '__main__':
    unittest.main()
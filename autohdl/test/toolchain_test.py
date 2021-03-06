import shutil
import unittest
import os
import logging
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from toolchain import *


class Test(unittest.TestCase):
    def setUp(self):
        self.t = Tool()
        if not os.path.exists('tmp_test_dir'):
            os.mkdir('tmp_test_dir')

    def tearDown(self):
        if os.path.exists('tmp_test_dir'):
            shutil.rmtree('tmp_test_dir')

    def test_check_tag_wrong(self):
        self.assertRaises(KeyError, self.t.get, 'wrong_id')

    def test_check_tag_wrong2(self):
        self.assertRaises(KeyError, self.t.get, 'gitbatch')

    def test_check_tag_wrong3(self):
        self.assertRaises(KeyError, self.t.get, 'batch_git')
    #
    # def test_getPath2(self):
    #     try:
    #         getPath('wrongTool_batch')
    #     except ToolchainException as e:
    #         self.assertEqual(str(e), "Can't find key in database: 'wrongTool' tag: wrongTool_batch")
    #
    # def test_getPath2(self):
    #     try:
    #         getPath('avhdl_wrongBatch')
    #     except ToolchainException as e:
    #         self.assertEqual(str(e), "Can't find key in database: 'wrongBatch' tag: avhdl_wrongBatch")
    #
    # def test_getPath3(self):
    #     """
    #     1. No toolchain.xml, generation new.
    #     2. Get path from existing one.
    #     """
    #     #    logging.disable(logging.DEBUG)
    #     pathGlobalXml = sys.prefix + '/Lib/site-packages/autohdl_cfg/toolchain.xml'
    #     if os.path.exists(pathGlobalXml):
    #         os.remove(pathGlobalXml)
    #     tc.gTools = {'tool': {'mode': 'exe_test',
    #                           'path': ['repo/github/autohdl/test/']
    #     }}
    #     open('tmp_test_dir/exe_test', 'w').close()
    #     path = tc.getPath('tool_mode')
    #     self.assertEqual(os.getcwd().replace('\\', '/') + '/tmp_test_dir/exe_test', path)
    #     # toolchain.xml exists
    #     path = tc.getPath('tool_mode')
    #     self.assertEqual(os.getcwd().replace('\\', '/') + '/tmp_test_dir/exe_test', path)


if __name__ == '__main__':
    logging.disable(logging.ERROR)
    unittest.main()

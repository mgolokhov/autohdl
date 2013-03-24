import sys
import os
import unittest
import shutil

sys.path.append('..')
from implement import *
# from autohdl.implement import *


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.dir_was = os.path.abspath(os.getcwd())
        self.maxDiff = None

    def setUp(self):
        os.chdir(self.dir_was)
        self.test_tmp = 'test_tmp'
        if not os.path.exists(self.test_tmp):
            os.makedirs(self.test_tmp)
            # precondition:
        # form some structure with src, constraints, netlists
        self.config = dict()
        self.config['hardcore_test'] = True
        self.top = 'top'
        self.config['top'] = self.top
        self.constraint_file = os.path.abspath(os.path.join(self.test_tmp,
                                                            'src',
                                                            self.config['top'] + '.ucf'))
        self.config['ucf'] = self.constraint_file
        # after coregen??
        netlists = ['blk_mem_gen_v7_3.ngc']
        self.netlists = [os.path.abspath(os.path.join(self.test_tmp, 'src', i)) for i in netlists]
        self.config['netlists'] = self.netlists

        self.synthesis_result_constraint = os.path.abspath(os.path.join(self.test_tmp,
                                                                        'autohdl',
                                                                        'synthesis',
                                                                        self.top,
                                                                        'synplicity.ucf'))
        self.synthesis_result_netlist = os.path.abspath(os.path.join(self.test_tmp,
                                                                     'autohdl',
                                                                     'synthesis',
                                                                     self.top,
                                                                     self.top + '.edf'))
        self.config['family'] = 'Spartan3E'
        self.config['device'] = 'xc3s1200e'
        self.config['package'] = 'fg320'
        self.config['speed'] = '-5'
        self.impl_script_path = os.path.abspath(os.path.join(
            self.test_tmp,
            'autohdl',
            'implement',
            self.top,
            self.top + '.tcl'
        ))
        # for afile in [self.config['ucf'],
        #               os.path.join(self.test_tmp, 'script'),
        #               self.synthesis_result_constraint,
        #               self.synthesis_result_netlist] + self.config['netlists']:
        #     self._mk_path(afile)
        if os.path.exists(self.test_tmp):
            shutil.rmtree(self.test_tmp)
        shutil.copytree('fake_repo/dsn_test_impl', self.test_tmp)
        os.chdir(os.path.join(self.test_tmp, 'script'))


    def tearDown(self):
        os.chdir(self.dir_was)
        # shutil.rmtree('test_tmp')

    def _mk_path(self, afile):
        if not os.path.exists(afile) and not os.path.splitext(afile)[1]:
            os.makedirs(afile)
            return
        d = os.path.dirname(afile)
        if not os.path.exists(d):
            os.makedirs(d)
        if not os.path.exists(afile):
            open(afile, 'w').close()

    def test_form_project_src(self):
        form_project_src(self.config)
        impl_src_expected = set()
        for i in self.netlists:
            impl_src_expected.add(i)
        impl_src_expected.add(self.synthesis_result_netlist)
        impl_src_expected.add(self.synthesis_result_constraint)
        self.maxDiff = None
        self.assertEqual(impl_src_expected, self.config['impl_src'])

    # def test_form_project_script(self):
    #     self.config['-impl'] = True
    #     mk_project_script(self.config)
    #     self.assertTrue(os.path.exists(self.impl_script_path),
    #                     "Project script for Xilinx (xtclsh) wasn't generated")

    def test_run_project_impl_new(self):
        if os.path.exists('../autohdl/implement'):
            shutil.rmtree('../autohdl/implement')
        self.config['impl'] = True
        run_project(self.config)
        self.assertTrue(os.path.exists(self.config['impl_stage']['script_path']))
        project_script_content = None
        with open(self.config['impl_stage']['script_path']) as f:
            project_script_content = f.read()
            project_script_content = project_script_content.replace(self.dir_was.replace('\\', '/'), '')
        project_script_content_expected = '''
        project new /test_tmp/autohdl/implement/top/top.xise

        project set family "Spartan3E"
        project set device "xc3s1200e"
        project set package "fg320"
        project set speed "-5"

        project set top_level_module_type "EDIF"
        project set "Preferred Language" "Verilog"

        #project set "FPGA Start-Up Clock" "JTAG Clock"

        xfile add "/test_tmp/src/blk_mem_gen_v7_3.ngc"
        xfile add "/test_tmp/autohdl/synthesis/top/synplicity.ucf"
        xfile add "/test_tmp/autohdl/synthesis/top/top.edf"

        project set top "top"

        process run "Generate Programming File"

        project close
        '''.replace(' ' * 4, '')
        self.assertMultiLineEqual(project_script_content_expected, project_script_content)
        # compare subprocesses to run
        # abs_path_to/xtclsh.exe abs_path_to/top/top.tcl
        self.assertTrue(len(self.config['impl_stage']['run']) == 1)
        self.assertTrue('xtclsh' in self.config['impl_stage']['run'][0],
                        'First should be run xtclsh.\n'
                        'Got ' + self.config['impl_stage']['run'][0])
        self.assertTrue(os.path.join('autohdl', 'implement', 'top', 'top.tcl') in self.config['impl_stage']['run'][0],
                        'xtclsh expected abs_path_to/autohdl/implement/top/top.tcl script.\n'
                        'Got ' + self.config['impl_stage']['run'][0])

    def test_run_project_impl_existed(self):
        self.config['impl'] = True
        #self.config['hardcore_test'] = False
        if not os.path.exists('../autohdl/implement/top/top.tcl'):
            run_project(self.config)
        run_project(self.config)

    def test_run_project_impl_gui_clean_new(self):
        pass

    def test_run_project_impl_gui_clean_existed(self):
        pass

    def test_run_project_impl_gui_new(self):
        if os.path.exists('../autohdl/implement'):
            shutil.rmtree('../autohdl/implement')
        self.config['impl-gui'] = True
        run_project(self.config)
        self.assertTrue(os.path.exists(self.config['impl_stage']['script_path']))
        project_script_content = None
        with open(self.config['impl_stage']['script_path']) as f:
            project_script_content = f.read()
            project_script_content = project_script_content.replace(self.dir_was.replace('\\', '/'), '')
        project_script_content_expected = '''
        project new /test_tmp/autohdl/implement/top/top.xise

        project set family "Spartan3E"
        project set device "xc3s1200e"
        project set package "fg320"
        project set speed "-5"

        project set top_level_module_type "EDIF"
        project set "Preferred Language" "Verilog"

        #project set "FPGA Start-Up Clock" "JTAG Clock"

        xfile add "/test_tmp/src/blk_mem_gen_v7_3.ngc"
        xfile add "/test_tmp/autohdl/synthesis/top/synplicity.ucf"
        xfile add "/test_tmp/autohdl/synthesis/top/top.edf"

        project set top "top"



        project close
        '''.replace(' ' * 4, '')
        self.assertMultiLineEqual(project_script_content_expected, project_script_content)
        # compare subprocesses to run
        # abs_path_to/xtclsh.exe abs_path_to/top/top.tcl
        self.assertTrue(len(self.config['impl_stage']['run']) == 2)
        self.assertTrue('xtclsh' in self.config['impl_stage']['run'][0],
                        'First should be run xtclsh.\n'
                        'Got ' + self.config['impl_stage']['run'][0])
        self.assertTrue(os.path.join('autohdl', 'implement', 'top', 'top.tcl') in self.config['impl_stage']['run'][0],
                        'xtclsh expected abs_path_to/autohdl/implement/top/top.tcl script.\n'
                        'Got ' + self.config['impl_stage']['run'][0])
        self.assertTrue('ise' in self.config['impl_stage']['run'][1],
                        'Second should be run ise.\n'
                        'Got ' + self.config['impl_stage']['run'][0])
        #self.assertTrue(os.path.exists(os.path.join('autohdl', 'implement', 'top', 'top.xise')))
        self.assertTrue(os.path.join('autohdl', 'implement', 'top', 'top.xise') in self.config['impl_stage']['run'][1],
                        'ise expected abs_path_to/autohdl/implement/top/top.xise.\n'
                        'Got ' + self.config['impl_stage']['run'][1])

    def test_run_project_impl_gui_existed(self):
        pass


def runTests():
    tests = [
        'test_form_project_src',
        'test_run_project_impl_new',
        # 'test_form_tcl_script_batch_mode',
    ]

    suite = unittest.TestSuite(map(Tests, tests))
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
#  unittest.main()
    runTests()


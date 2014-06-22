import unittest

from autohdl.synplify import *


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.test_tmp = 'test_tmp'
        self.was_dir = os.path.abspath(os.getcwd()).replace('\\', '/')
        self.config = dict()
        self.config['debug'] = 'hardcore_test'
        self.config['technology'] = 'Spartan3E'
        self.config['part'] = 'xc3s1200e'
        self.config['package'] = 'fg320'
        self.config['speed_grade'] = '-5'

    def setUp(self):
        os.chdir(self.was_dir)
        if os.path.exists(self.test_tmp):
            shutil.rmtree(self.test_tmp)

    def test1(self):
        shutil.copytree('test_data_synthesis_synplify/dsn1', self.test_tmp + '/dsn1')
        os.chdir(self.test_tmp + '/dsn1/script')
        self.config['top'] = 'f1'
        self.config['cl'] = {'syn': 'synplify_batch'}
        self.config['structure'] = dict()
        self.config['structure']['mainSrc'] = [self.test_tmp + '/dsn1/src/f1.v']
        self.config['structure']['depSrc'] = []
        self.config['ucf'] = self.test_tmp + '/dsn1/src/f1.ucf'
        run(self.config)
        generated_project_file = os.path.join(self.was_dir,
                                              self.test_tmp,
                                              'dsn1/autohdl/synthesis/f1/synthesis.prj')
        self.assertTrue(os.path.exists(generated_project_file),
                        'Cant find project file:\n' + generated_project_file)
        self.assertTrue(len(self.config['execution_fifo']) == 1,
                        'Expected only one program to run')
        self.assertTrue('synplify_premier.exe" '
                        '-product synplify_premier '
                        '-licensetype synplifypremier '
                        '-batch synthesis.prj' in self.config['execution_fifo'][0])


if __name__ == '__main__':
    unittest.main()

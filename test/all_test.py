import unittest

import build_test
import instance_test
import structure_test
import synthesis_test
import toolchain_test
import implement_test


loader = unittest.TestLoader()

suite = loader.loadTestsFromModule(build_test)
suite.addTests(loader.loadTestsFromModule(instance_test))
suite.addTests(loader.loadTestsFromModule(structure_test))
suite.addTests(loader.loadTestsFromModule(synthesis_test))
suite.addTests(loader.loadTestsFromModule(toolchain_test))
suite.addTests(loader.loadTestsFromModule(implement_test))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

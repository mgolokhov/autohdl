import unittest

import implement_test

loader = unittest.TestLoader()

suite = loader.loadTestsFromModule(implement_test)
#suite.addTests(loader.loadTestsFromModule(test_something2))
#suite.addTests(loader.loadTestsFromModule(test_something3))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

from pathlib import Path
import sys
import unittest

# Tự động thêm thư mục gốc của dự án vào PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_app import TestChatApp
from tests.test_simple_server import TestSimpleServer

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestChatApp))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSimpleServer))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

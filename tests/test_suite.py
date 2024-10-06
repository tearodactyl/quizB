# tests/test_suite.py

import unittest

# Import test modules
from test_quiz_data import TestQuizData
from test_environment_handler import TestEnvironmentHandler
from test_command_processor import TestCommandProcessor
from test_quiz import TestQuiz
from test_configuration import TestConfiguration
from test_integration import TestIntegration

# Create a test suite combining all test cases
def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestQuizData))
    test_suite.addTest(unittest.makeSuite(TestEnvironmentHandler))
    test_suite.addTest(unittest.makeSuite(TestCommandProcessor))
    test_suite.addTest(unittest.makeSuite(TestQuiz))
    test_suite.addTest(unittest.makeSuite(TestConfiguration))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

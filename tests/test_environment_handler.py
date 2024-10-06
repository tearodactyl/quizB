# tests/test_environment_handler.py

import unittest
from quiz_core import EnvironmentHandler
import os

class TestEnvironmentHandler(unittest.TestCase):
    """Unit tests for the EnvironmentHandler class."""

    def setUp(self):
        """Set up test environment."""
        self.input_file = 'temp_input.txt'
        self.output_file = 'temp_output.txt'
        self.test_inputs = ['First input', 'Second input']

        # Write test inputs to the input file
        with open(self.input_file, 'w', encoding='utf-8') as f:
            for line in self.test_inputs:
                f.write(f"{line}\n")

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_local_mode(self):
        """Test input/output in local mode."""
        env_handler = EnvironmentHandler(mode='local')
        # Since input() in local mode requires user interaction,
        # we can test output() method
        with self.assertLogs(level='INFO') as log:
            env_handler.output("Test output")
        # Can't capture print output directly here without redirecting stdout

    def test_file_mode(self):
        """Test input/output in file mode."""
        env_handler = EnvironmentHandler(
            mode='file',
            input_file=self.input_file,
            output_file=self.output_file
        )
        # Test input()
        input1 = env_handler.input("Prompt 1: ")
        input2 = env_handler.input("Prompt 2: ")
        self.assertEqual(input1, 'First input')
        self.assertEqual(input2, 'Second input')

        # Test output()
        env_handler.output("Test output line 1")
        env_handler.output("Test output line 2")
        env_handler.close()

        # Check that outputs were written to the output file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            outputs = f.read().splitlines()
        expected_outputs = [
            'Prompt 1: First input',
            'Prompt 2: Second input',
            'Test output line 1',
            'Test output line 2'
        ]
        self.assertEqual(outputs, expected_outputs)

    def test_no_more_input(self):
        """Test behavior when input data is exhausted."""
        env_handler = EnvironmentHandler(
            mode='file',
            input_file=self.input_file,
            output_file=self.output_file
        )
        # Read all inputs
        env_handler.input()
        env_handler.input()
        # Next input should raise an error
        with self.assertRaises(SystemExit):
            env_handler.input()

if __name__ == '__main__':
    unittest.main()

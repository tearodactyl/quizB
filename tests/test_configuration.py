# tests/test_configuration.py

import unittest
from unittest.mock import patch, mock_open
from io import StringIO
import os
import sys
import json
import tempfile

# Import the necessary functions and classes from your application
# Adjust the import paths as needed based on your project structure
from quiz_application import load_config, setup_logging, main

class TestConfiguration(unittest.TestCase):
    """Unit tests for configuration loading and overriding."""

    def setUp(self):
        """Set up test environment."""
        # Store original environment variables and sys.argv
        self.original_environ = os.environ.copy()
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        """Clean up after tests."""
        # Restore environment variables and sys.argv
        os.environ.clear()
        os.environ.update(self.original_environ)
        sys.argv = self.original_argv.copy()

    def test_load_config_file(self):
        """Test loading configuration from the config file."""
        # Create a temporary config file
        config_data = {
            "quiz_length": 5,
            "input_file": "config_quiz.json",
            "output_file": "config_results.txt",
            "environment": "local",
            "sanitization_policy": "replace",
            "logging_enabled": False
        }
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_config:
            json.dump(config_data, temp_config)
            temp_config_path = temp_config.name

        # Mock the environment to use the temporary config file
        with patch.dict(os.environ, {'QUIZ_CONFIG_FILE': temp_config_path}):
            config = load_config()
            self.assertEqual(config['quiz_length'], 5)
            self.assertEqual(config['input_file'], "config_quiz.json")
            self.assertEqual(config['sanitization_policy'], "replace")
            self.assertFalse(config['logging_enabled'])

        # Clean up temporary file
        os.remove(temp_config_path)

    def test_override_with_command_line_arguments(self):
        """Test overriding configuration with command-line arguments."""
        # Create a temporary config file
        config_data = {
            "quiz_length": 5,
            "input_file": "config_quiz.json",
            "output_file": "config_results.txt",
            "environment": "local",
            "sanitization_policy": "reject",
            "logging_enabled": False
        }
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_config:
            json.dump(config_data, temp_config)
            temp_config_path = temp_config.name

        # Mock the environment to use the temporary config file
        with patch.dict(os.environ, {'QUIZ_CONFIG_FILE': temp_config_path}):
            # Mock sys.argv to simulate command-line arguments
            test_args = [
                'quiz_application.py',
                '--quiz-length', '10',
                '--sanitization-policy', 'remove',
                '--logging-enabled'
            ]
            with patch.object(sys, 'argv', test_args):
                config = load_config()
                # Now parse command-line arguments using argparse
                from quiz_application import argparse
                parser = argparse.ArgumentParser(description='Multiple-choice quiz application.')
                parser.add_argument('--mode', choices=['local', 'file', 'test', 'action'],
                                    default=os.environ.get('QUIZ_ENVIRONMENT', config.get('environment', 'local')),
                                    help='Mode in which to run the quiz.')
                parser.add_argument('--quiz-file',
                                    default=os.environ.get('QUIZ_INPUT_FILE', config.get('input_file', 'quiz.json')),
                                    help='Path to the quiz JSON file.')
                parser.add_argument('--input-file',
                                    default=os.environ.get('QUIZ_INPUT_FILE', config.get('input_file')),
                                    help='Input file for file-based mode.')
                parser.add_argument('--output-file',
                                    default=os.environ.get('QUIZ_OUTPUT_FILE', config.get('output_file')),
                                    help='Output file for file-based mode.')
                parser.add_argument('--quiz-length',
                                    type=int,
                                    default=int(os.environ.get('QUIZ_LENGTH', config.get('quiz_length', 0))),
                                    help='Number of questions to present.')
                parser.add_argument('--sanitization-policy',
                                    choices=['reject', 'remove', 'replace'],
                                    default=config.get('sanitization_policy', 'reject'),
                                    help='Policy for sanitizing invalid text.')
                parser.add_argument('--logging-enabled',
                                    action='store_true' if config.get('logging_enabled', True) else 'store_false',
                                    help='Enable or disable logging.')
                args = parser.parse_args()

                # Test that command-line arguments override config file
                self.assertEqual(args.quiz_length, 10)
                self.assertEqual(args.sanitization_policy, 'remove')
                self.assertTrue(args.logging_enabled)

        # Clean up temporary file
        os.remove(temp_config_path)

    def test_override_with_environment_variables(self):
        """Test overriding configuration with environment variables."""
        # Create a temporary config file
        config_data = {
            "quiz_length": 5,
            "input_file": "config_quiz.json",
            "output_file": "config_results.txt",
            "environment": "local",
            "sanitization_policy": "reject",
            "logging_enabled": False
        }
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_config:
            json.dump(config_data, temp_config)
            temp_config_path = temp_config.name

        # Mock environment variables
        env_vars = {
            'QUIZ_CONFIG_FILE': temp_config_path,
            'QUIZ_LENGTH': '15',
            'QUIZ_ENVIRONMENT': 'file',
            'QUIZ_INPUT_FILE': 'env_quiz.json',
            'QUIZ_OUTPUT_FILE': 'env_results.txt',
            'QUIZ_SANITIZATION_POLICY': 'replace',
            'QUIZ_LOGGING_ENABLED': 'True'
        }
        with patch.dict(os.environ, env_vars):
            config = load_config()
            # Mock sys.argv with no command-line arguments
            test_args = ['quiz_application.py']
            with patch.object(sys, 'argv', test_args):
                # Parse command-line arguments using argparse
                from quiz_application import argparse
                parser = argparse.ArgumentParser(description='Multiple-choice quiz application.')
                parser.add_argument('--mode', choices=['local', 'file', 'test', 'action'],
                                    default=os.environ.get('QUIZ_ENVIRONMENT', config.get('environment', 'local')),
                                    help='Mode in which to run the quiz.')
                parser.add_argument('--quiz-file',
                                    default=os.environ.get('QUIZ_INPUT_FILE', config.get('input_file', 'quiz.json')),
                                    help='Path to the quiz JSON file.')
                parser.add_argument('--input-file',
                                    default=os.environ.get('QUIZ_INPUT_FILE', config.get('input_file')),
                                    help='Input file for file-based mode.')
                parser.add_argument('--output-file',
                                    default=os.environ.get('QUIZ_OUTPUT_FILE', config.get('output_file')),
                                    help='Output file for file-based mode.')
                parser.add_argument('--quiz-length',
                                    type=int,
                                    default=int(os.environ.get('QUIZ_LENGTH', config.get('quiz_length', 0))),
                                    help='Number of questions to present.')
                parser.add_argument('--sanitization-policy',
                                    choices=['reject', 'remove', 'replace'],
                                    default=config.get('sanitization_policy', 'reject'),
                                    help='Policy for sanitizing invalid text.')
                parser.add_argument('--logging-enabled',
                                    action='store_true' if config.get('logging_enabled', True) else 'store_false',
                                    help='Enable or disable logging.')
                args = parser.parse_args()

                # Test that environment variables override config file and command-line arguments
                self.assertEqual(args.quiz_length, 15)
                self.assertEqual(args.mode, 'file')
                self.assertEqual(args.quiz_file, 'env_quiz.json')
                self.assertEqual(args.input_file, 'env_quiz.json')
                self.assertEqual(args.output_file, 'env_results.txt')
                self.assertEqual(args.sanitization_policy, 'replace')
                self.assertTrue(args.logging_enabled)

        # Clean up temporary file
        os.remove(temp_config_path)

    def test_precedence_of_configuration_sources(self):
        """Test the precedence of environment variables over command-line arguments and config file."""
        # Create a temporary config file
        config_data = {
            "quiz_length": 5,
            "input_file": "config_quiz.json",
            "output_file": "config_results.txt",
            "environment": "local",
            "sanitization_policy": "reject",
            "logging_enabled": False
        }
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_config:
            json.dump(config_data, temp_config)
            temp_config_path = temp_config.name

        # Mock environment variables
        env_vars = {
            'QUIZ_LENGTH': '20',
            'QUIZ_ENVIRONMENT': 'action',
            'QUIZ_INPUT_FILE': 'env_quiz.json',
            'QUIZ_OUTPUT_FILE': 'env_results.txt',
            'QUIZ_SANITIZATION_POLICY': 'remove',
            'QUIZ_LOGGING_ENABLED': 'True'
        }
        with patch.dict(os.environ, env_vars):
            config = load_config()
            # Mock sys.argv to simulate command-line arguments
            test_args = [
                'quiz_application.py',
                '--quiz-length', '10',
                '--sanitization-policy', 'replace',
                '--mode', 'file',
                '--quiz-file', 'cli_quiz.json',
                '--input-file', 'cli_input.txt',
                '--output-file', 'cli_output.txt',
                '--logging-enabled'
            ]
            with patch.object(sys, 'argv', test_args):
                # Parse command-line arguments using argparse
                from quiz_application import argparse
                parser = argparse.ArgumentParser(description='Multiple-choice quiz application.')
                parser.add_argument('--mode', choices=['local', 'file', 'test', 'action'],
                                    default=os.environ.get('QUIZ_ENVIRONMENT', config.get('environment', 'local')),
                                    help='Mode in which to run the quiz.')
                parser.add_argument('--quiz-file',
                                    default=os.environ.get('QUIZ_INPUT_FILE', config.get('input_file', 'quiz.json')),
                                    help='Path to the quiz JSON file.')
                parser.add_argument('--input-file',
                                    default=os.environ.get('QUIZ_INPUT_FILE', config.get('input_file')),
                                    help='Input file for file-based mode.')
                parser.add_argument('--output-file',
                                    default=os.environ.get('QUIZ_OUTPUT_FILE', config.get('output_file')),
                                    help='Output file for file-based mode.')
                parser.add_argument('--quiz-length',
                                    type=int,
                                    default=int(os.environ.get('QUIZ_LENGTH', config.get('quiz_length', 0))),
                                    help='Number of questions to present.')
                parser.add_argument('--sanitization-policy',
                                    choices=['reject', 'remove', 'replace'],
                                    default=config.get('sanitization_policy', 'reject'),
                                    help='Policy for sanitizing invalid text.')
                parser.add_argument('--logging-enabled',
                                    action='store_true' if config.get('logging_enabled', True) else 'store_false',
                                    help='Enable or disable logging.')
                args = parser.parse_args()

                # Test that environment variables have highest precedence
                self.assertEqual(args.quiz_length, 20)  # From env var
                self.assertEqual(args.mode, 'action')   # From env var
                self.assertEqual(args.quiz_file, 'env_quiz.json')  # From env var
                self.assertEqual(args.input_file, 'env_quiz.json')  # From env var
                self.assertEqual(args.output_file, 'env_results.txt')  # From env var
                self.assertEqual(args.sanitization_policy, 'remove')  # From env var
                self.assertTrue(args.logging_enabled)  # From env var

        # Clean up temporary file
        os.remove(temp_config_path)

if __name__ == '__main__':
    unittest.main()

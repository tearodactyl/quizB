# quiz_application.py

import argparse
import sys
import os
import json
import logging

from quiz_data import QuizData
from quiz_core import EnvironmentHandler, Quiz

def load_config(config_file='config.json'):
    """Load configuration from a JSON file.

    Args:
        config_file (str): Path to the config file.

    Returns:
        dict: Configuration dictionary.
    """
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing config file: {e}")
            sys.exit(1)
    return config

def setup_logging(logging_enabled=True):
    """Set up logging configuration.

    Args:
        logging_enabled (bool): Flag to enable or disable logging.
    """
    if logging_enabled:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    else:
        logging.disable(logging.CRITICAL)

def main():
    """Main function to run the quiz application."""
    config = load_config()

    parser = argparse.ArgumentParser(description='Multiple-choice quiz application.')
    parser.add_argument('--mode', choices=['local', 'file'],
                        default=os.environ.get('QUIZ_ENVIRONMENT', config.get('environment', 'local')),
                        help='Mode in which to run the quiz.')
    parser.add_argument('--quiz-file',
                        default=os.environ.get('QUIZ_INPUT_FILE', config.get('quiz_file', 'quiz.json')),
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

    setup_logging(logging_enabled=args.logging_enabled)

    env_handler = EnvironmentHandler(
        mode=args.mode,
        input_file=args.input_file,
        output_file=args.output_file
    )

    quiz_data = QuizData(
        filename=args.quiz_file,
        sanitization_policy=args.sanitization_policy,
        quiz_length=args.quiz_length
    )

    quiz = Quiz(quiz_data=quiz_data, env_handler=env_handler)
    quiz.start()

if __name__ == '__main__':
    main()

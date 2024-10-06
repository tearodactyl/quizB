# quiz_data.py

import json
import sys
import re
import logging

class QuizData:
    """Class responsible for loading and validating quiz data from a JSON file."""

    def __init__(self, filename='quiz.json', sanitization_policy='reject', quiz_length=0):
        """
        Initialize the QuizData instance.

        Args:
            filename (str): Path to the quiz JSON file.
            sanitization_policy (str): Policy for sanitizing invalid text ('reject', 'remove', 'replace').
            quiz_length (int): Number of questions to include in the quiz.
        """
        self.filename = filename
        self.sanitization_policy = sanitization_policy
        self.quiz_length = quiz_length
        self.questions = []
        self.quiz_info = {}
        self.load_quiz_data()

    def load_quiz_data(self):
        """Load and validate quiz data from the JSON file."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.quiz_info = {
                'title': data.get('title', None),
                'subtitle': data.get('subtitle', None),
                'description': data.get('description', None)
            }
            raw_questions = data.get('questions', [])
            for question in raw_questions:
                sanitized_question = self.sanitize_question(question)
                if sanitized_question and self.validate_question(sanitized_question):
                    self.questions.append(sanitized_question)
                else:
                    logging.warning(f"Invalid question skipped: {question.get('question', 'Unknown')}")
            if self.quiz_length > 0 and len(self.questions) > self.quiz_length:
                self.questions = self.questions[:self.quiz_length]
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Error loading quiz data: {e}")
            sys.exit(1)

    def validate_question(self, question):
        """Validate a single question.

        Args:
            question (dict): The question to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        required_fields = ['question', 'options', 'correct']
        for field in required_fields:
            if field not in question:
                return False
        if not isinstance(question['options'], list) or not question['options']:
            return False
        if not isinstance(question['correct'], int) or not (1 <= question['correct'] <= len(question['options'])):
            return False
        return True

    def sanitize_question(self, question):
        """Sanitize all text fields in a question.

        Args:
            question (dict): The question to sanitize.

        Returns:
            dict or None: Sanitized question or None if rejected.
        """
        sanitized_question = {}
        for key, value in question.items():
            if isinstance(value, str):
                sanitized_text = self.sanitize_text(value)
                if sanitized_text is None:
                    return None  # Reject the question
                sanitized_question[key] = sanitized_text
            elif isinstance(value, list):
                sanitized_options = []
                for option in value:
                    sanitized_option = self.sanitize_text(option)
                    if sanitized_option is None:
                        return None  # Reject the question
                    sanitized_options.append(sanitized_option)
                sanitized_question[key] = sanitized_options
            else:
                sanitized_question[key] = value
        return sanitized_question

    def sanitize_text(self, text):
        """Sanitize a text string based on the sanitization policy.

        Args:
            text (str): The text to sanitize.

        Returns:
            str or None: Sanitized text or None if rejected.
        """
        max_length = 1000
        disallowed_patterns = re.compile(r'[<>]')  # Example pattern to reject

        if not (1 <= len(text) <= max_length):
            logging.warning(f"Text length out of bounds: {text}")
            return None if self.sanitization_policy == 'reject' else text[:max_length]

        if disallowed_patterns.search(text):
            if self.sanitization_policy == 'reject':
                logging.warning(f"Disallowed characters found in text: {text}")
                return None
            elif self.sanitization_policy == 'remove':
                text = disallowed_patterns.sub('', text)
            elif self.sanitization_policy == 'replace':
                text = disallowed_patterns.sub('?', text)
        return text

    def additional_checks(self, text):
        """Placeholder for any additional checks on the text.

        Args:
            text (str): The text to check.

        Returns:
            bool: True if text passes the checks, False otherwise.
        """
        # Implement any additional checks here
        return True

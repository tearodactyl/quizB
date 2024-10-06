# tests/test_quiz_data.py

import unittest
from quiz_data import QuizData
import json
import os

class TestQuizData(unittest.TestCase):
    """Unit tests for the QuizData class."""

    def setUp(self):
        """Set up test environment."""
        # Create a sample quiz JSON data
        self.sample_quiz = {
            "title": "Sample Quiz",
            "description": "A sample description.",
            "questions": [
                {
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5"],
                    "correct": 2
                },
                {
                    "question": "Incomplete question",
                    "options": ["Option 1", "Option 2"]
                    # Missing 'correct' field
                },
                {
                    "question": "Invalid option number",
                    "options": ["Yes", "No"],
                    "correct": 3  # Out of range
                },
                {
                    "question": "<script>alert('XSS')</script>",
                    "options": ["Option 1", "Option 2"],
                    "correct": 1
                }
            ]
        }

        # Write the sample quiz data to a temporary file
        self.quiz_file = 'temp_quiz.json'
        with open(self.quiz_file, 'w', encoding='utf-8') as f:
            json.dump(self.sample_quiz, f)

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.quiz_file):
            os.remove(self.quiz_file)

    def test_load_quiz_data(self):
        """Test loading and sanitizing quiz data."""
        quiz_data = QuizData(
            filename=self.quiz_file,
            sanitization_policy='reject',
            quiz_length=10
        )
        # Should only load valid questions
        self.assertEqual(len(quiz_data.questions), 1)
        self.assertEqual(quiz_data.questions[0]['question'], "What is 2 + 2?")

    def test_validate_question(self):
        """Test the question validation method."""
        quiz_data = QuizData(
            filename=self.quiz_file,
            sanitization_policy='reject',
            quiz_length=10
        )
        valid_question = {
            "question": "Valid question?",
            "options": ["Yes", "No"],
            "correct": 1
        }
        invalid_question_missing_field = {
            "question": "Missing correct field",
            "options": ["Option 1", "Option 2"]
        }
        invalid_question_wrong_correct = {
            "question": "Correct index out of range",
            "options": ["Option 1", "Option 2"],
            "correct": 3
        }
        self.assertTrue(quiz_data.validate_question(valid_question))
        self.assertFalse(quiz_data.validate_question(invalid_question_missing_field))
        self.assertFalse(quiz_data.validate_question(invalid_question_wrong_correct))

    def test_sanitize_text_reject_policy(self):
        """Test sanitization with 'reject' policy."""
        quiz_data = QuizData(
            filename=self.quiz_file,
            sanitization_policy='reject',
            quiz_length=10
        )
        # Valid text
        sanitized = quiz_data.sanitize_text("Valid text.")
        self.assertEqual(sanitized, "Valid text.")

        # Text with disallowed characters
        sanitized = quiz_data.sanitize_text("Invalid text <script>")
        self.assertIsNone(sanitized)

    def test_sanitize_text_remove_policy(self):
        """Test sanitization with 'remove' policy."""
        quiz_data = QuizData(
            filename=self.quiz_file,
            sanitization_policy='remove',
            quiz_length=10
        )
        sanitized = quiz_data.sanitize_text("Invalid text <script>")
        self.assertEqual(sanitized, "Invalid text ")

    def test_sanitize_text_replace_policy(self):
        """Test sanitization with 'replace' policy."""
        quiz_data = QuizData(
            filename=self.quiz_file,
            sanitization_policy='replace',
            quiz_length=10
        )
        sanitized = quiz_data.sanitize_text("Invalid text <script>")
        self.assertEqual(sanitized, "Invalid text ?script?")

    def test_additional_checks(self):
        """Test the placeholder for additional checks."""
        quiz_data = QuizData(
            filename=self.quiz_file,
            sanitization_policy='reject',
            quiz_length=10
        )
        # Assuming additional_checks always returns True for now
        self.assertTrue(quiz_data.additional_checks("Some text"))

    def test_quiz_file_validation(self):
        """Test quiz file format validation with various JSON files."""
        test_files = [
            ('valid_quiz.json', True),
            ('missing_fields_quiz.json', False),
            ('invalid_types_quiz.json', False),
            ('exceeds_length_quiz.json', False),
            ('disallowed_chars_quiz.json', False),
            ('empty_quiz.json', True),
            ('partial_optional_fields.json', True)
        ]

        for filename, should_pass in test_files:
            with self.subTest(filename=filename):
                quiz_file = os.path.join('tests', 'quizzes', filename)
                try:
                    quiz_data = QuizData(
                        filename=quiz_file,
                        sanitization_policy='reject',
                        quiz_length=10
                    )
                    if should_pass:
                        self.assertTrue(len(quiz_data.questions) > 0 or 'empty' in filename)
                    else:
                        self.assertEqual(len(quiz_data.questions), 0)
                except Exception as e:
                    if should_pass:
                        self.fail(f"{filename} should pass but raised an exception: {e}")
                    else:
                        self.assertIsInstance(e, SystemExit)


if __name__ == '__main__':
    unittest.main()

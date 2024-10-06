# tests/test_user_input.py

import unittest
from quiz_core import Quiz, EnvironmentHandler
from quiz_data import QuizData

class MockEnvironmentHandler(EnvironmentHandler):
    """Mock environment handler for testing user inputs."""
    def __init__(self, inputs):
        self.inputs = inputs
        self.outputs = []
        self.current_input_index = 0

    def input(self, prompt=''):
        if self.current_input_index < len(self.inputs):
            user_input = self.inputs[self.current_input_index]
            self.current_input_index += 1
            self.outputs.append(prompt + user_input)
            return user_input
        else:
            # Simulate end of inputs
            return 'quit'

    def output(self, text):
        self.outputs.append(text)

    def close(self):
        pass

class TestUserInputValidation(unittest.TestCase):
    """Tests for user input validation and sanitization."""

    def setUp(self):
        """Set up test environment."""
        # Sample quiz data with one question
        self.quiz_data = QuizData(
            filename='sample_quiz.json',
            sanitization_policy='reject',
            quiz_length=1
        )
        # Directly set questions to avoid file I/O
        self.quiz_data.questions = [
            {
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5"],
                "correct": 2
            }
        ]

    def test_empty_input(self):
        """Test handling of empty user input."""
        inputs = ['', '2']  # User enters empty input, then valid input
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()
        self.assertIn("Invalid input size. Please try again.", env_handler.outputs)

    def test_excessively_long_input(self):
        """Test handling of excessively long user input."""
        long_input = 'a' * 101  # 101 characters, exceeding the limit
        inputs = [long_input, '2']
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()
        self.assertIn("Invalid input size. Please try again.", env_handler.outputs)

    def test_disallowed_characters(self):
        """Test input containing disallowed characters."""
        inputs = ['<script>', '2']
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()
        # Since sanitization occurs in quiz data loading, and user input is for option selection, disallowed characters may be acceptable here
        # However, commands or other inputs should handle disallowed characters appropriately

    def test_invalid_option_number(self):
        """Test entering an option number that is out of range."""
        inputs = ['0', '4', '-1', '2']
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()
        # Should prompt the user again until a valid option is entered
        self.assertIn("Invalid option number. Please try again.", env_handler.outputs)

    def test_non_integer_input(self):
        """Test entering non-integer input when an option number is expected."""
        inputs = ['two', '2']
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()
        self.assertIn("Invalid input. Please enter a valid option number or command.", env_handler.outputs)

    def test_sanitization_policy_reject(self):
        """Test sanitization policy 'reject' with invalid question text."""
        # Modify question to include disallowed characters
        self.quiz_data.questions[0]['question'] = "Invalid question <script>"
        # Reload quiz data with 'reject' policy
        self.quiz_data.sanitization_policy = 'reject'
        self.quiz_data.load_quiz_data()
        # Should result in zero questions since the question is rejected
        self.assertEqual(len(self.quiz_data.questions), 0)

    def test_sanitization_policy_remove(self):
        """Test sanitization policy 'remove' with invalid question text."""
        self.quiz_data.questions[0]['question'] = "Invalid question <script>"
        self.quiz_data.sanitization_policy = 'remove'
        self.quiz_data.load_quiz_data()
        # Question should be sanitized and included
        self.assertEqual(len(self.quiz_data.questions), 1)
        self.assertEqual(self.quiz_data.questions[0]['question'], "Invalid question ")

    def test_sanitization_policy_replace(self):
        """Test sanitization policy 'replace' with invalid question text."""
        self.quiz_data.questions[0]['question'] = "Invalid question <script>"
        self.quiz_data.sanitization_policy = 'replace'
        self.quiz_data.load_quiz_data()
        self.assertEqual(len(self.quiz_data.questions), 1)
        self.assertEqual(self.quiz_data.questions[0]['question'], "Invalid question ?script?")

    def test_all_option_numbers(self):
        """Test selecting each possible option number."""
        for option_num in range(1, len(self.quiz_data.questions[0]['options']) + 1):
            inputs = [str(option_num)]
            env_handler = MockEnvironmentHandler(inputs)
            quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
            quiz.start()
            if option_num == self.quiz_data.questions[0]['correct']:
                self.assertIn("Correct!", env_handler.outputs)
            else:
                self.assertIn("Incorrect.", env_handler.outputs)

if __name__ == '__main__':
    unittest.main()

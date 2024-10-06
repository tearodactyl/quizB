# tests/test_quiz.py

import unittest
from quiz_core import Quiz, EnvironmentHandler
from quiz_data import QuizData

class MockEnvironmentHandler(EnvironmentHandler):
    """Mock environment handler for testing the Quiz class."""

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
            return 'quit'

    def output(self, text):
        self.outputs.append(text)

    def close(self):
        pass  # Do nothing for the mock

class TestQuiz(unittest.TestCase):
    """Unit tests for the Quiz class."""

    def setUp(self):
        """Set up test environment."""
        # Sample quiz data
        self.quiz_data = QuizData(
            filename='sample_quiz.json',
            sanitization_policy='reject',
            quiz_length=10
        )
        # Create sample questions directly to avoid file I/O
        self.quiz_data.questions = [
            {
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5"],
                "correct": 2
            },
            {
                "question": "What is the capital of France?",
                "options": ["Berlin", "London", "Paris"],
                "correct": 3
            }
        ]

    def test_quiz_flow_correct_answers(self):
        """Test quiz flow where user answers all questions correctly."""
        inputs = ['2', '3']
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()

        self.assertIn("Correct!", env_handler.outputs[-4])
        self.assertIn("Correct!", env_handler.outputs[-2])
        self.assertEqual(quiz.correct_answers, 2)
        self.assertEqual(len(quiz.incorrect_questions), 0)

    def test_quiz_flow_incorrect_answers(self):
        """Test quiz flow where user answers questions incorrectly."""
        inputs = ['1', '1']
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()

        self.assertIn("Incorrect.", env_handler.outputs[-4])
        self.assertIn("Incorrect.", env_handler.outputs[-2])
        self.assertEqual(quiz.correct_answers, 0)
        self.assertEqual(len(quiz.incorrect_questions), 2)

    def test_quiz_flow_with_commands(self):
        """Test quiz flow with user commands like 'skip' and 'help'."""
        inputs = ['help', 's', '2', 'quit']
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()

        self.assertIn("Available commands:", env_handler.outputs)
        self.assertIn("Skipped questions: 1", env_handler.outputs[-3])

    def test_quiz_restart(self):
        """Test the 'restart' command during the quiz."""
        inputs = ['restart', '2', '3']
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()

        self.assertEqual(quiz.correct_answers, 2)
        self.assertEqual(len(quiz.incorrect_questions), 0)

    def test_invalid_input(self):
        """Test handling of invalid user inputs."""
        inputs = ['invalid', '5', '2', '3']
        env_handler = MockEnvironmentHandler(inputs)
        quiz = Quiz(quiz_data=self.quiz_data, env_handler=env_handler)
        quiz.start()

        self.assertIn("Invalid input", env_handler.outputs)
        self.assertIn("Invalid option number", env_handler.outputs)
        self.assertEqual(quiz.correct_answers, 2)

if __name__ == '__main__':
    unittest.main()

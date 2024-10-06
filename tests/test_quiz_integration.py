#test_quiz_integration.py

import unittest
from quiz_data import QuizData
from quiz_core import Quiz, EnvironmentHandler

class MockEnvironmentHandler(EnvironmentHandler):
    def __init__(self, inputs):
        self.inputs = inputs
        self.outputs = []
        self.input_index = 0

    def input(self, prompt=''):
        if self.input_index < len(self.inputs):
            user_input = self.inputs[self.input_index]
            self.input_index += 1
            self.outputs.append(prompt + user_input)
            return user_input
        else:
            return 'quit'

    def output(self, text):
        self.outputs.append(text)

class TestQuizIntegration(unittest.TestCase):
    def test_full_quiz_flow(self):
        inputs = ['1', 'skip', '2', 'quit']
        env_handler = MockEnvironmentHandler(inputs)
        quiz_data = QuizData(
            filename='test_quiz.json',
            sanitization_policy='reject',
            quiz_length=3
        )
        quiz = Quiz(quiz_data=quiz_data, env_handler=env_handler)
        quiz.start()

        # Check that the outputs contain expected strings
        self.assertIn('Correct!', env_handler.outputs)
        self.assertIn('Skipped questions: 1', env_handler.outputs)

if __name__ == '__main__':
    unittest.main()

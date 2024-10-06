# performance_tests/test_large_quiz.py

import unittest
from quiz_data import QuizData
import time

class TestLargeQuiz(unittest.TestCase):
    def test_loading_large_quiz(self):
        """Test loading and processing a large quiz file."""
        # Generate a large quiz file programmatically
        large_quiz = {
            "questions": []
        }
        for i in range(1000):
            question = {
                "question": f"What is the value of {i} + {i}?",
                "options": [str(i * 2), str(i * 2 + 1), str(i * 2 - 1)],
                "correct": 1
            }
            large_quiz["questions"].append(question)
        
        # Write to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_quiz_file:
            import json
            json.dump(large_quiz, temp_quiz_file)
            temp_quiz_filename = temp_quiz_file.name
        
        start_time = time.time()
        quiz_data = QuizData(
            filename=temp_quiz_filename,
            sanitization_policy='reject',
            quiz_length=0  # No limit
        )
        load_time = time.time() - start_time
        print(f"Loaded large quiz in {load_time:.2f} seconds")
        self.assertTrue(len(quiz_data.questions) == 1000)
        self.assertTrue(load_time < 5)  # Assert that loading takes less than 5 seconds
        
        # Clean up
        import os
        os.remove(temp_quiz_filename)

if __name__ == '__main__':
    unittest.main()

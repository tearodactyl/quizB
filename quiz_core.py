# quiz_core.py

import sys
import logging
import random
import re

class EnvironmentHandler:
    """Handles input and output operations based on the environment mode."""

    def __init__(self, mode='local', input_file=None, output_file=None):
        """
        Initialize the EnvironmentHandler.

        Args:
            mode (str): The mode of operation ('local', 'file').
            input_file (str): Path to the input file for 'file' mode.
            output_file (str): Path to the output file for 'file' mode.
        """
        self.mode = mode
        if mode == 'file':
            try:
                self.input_fd = open(input_file, 'r', encoding='utf-8')
                self.output_fd = open(output_file, 'w', encoding='utf-8')
            except IOError as e:
                logging.error(f"Error opening files: {e}")
                sys.exit(1)
        else:
            self.input_fd = sys.stdin
            self.output_fd = sys.stdout

    def input(self, prompt=''):
        """Get input from the user.

        Args:
            prompt (str): The prompt to display.

        Returns:
            str: The user's input.
        """
        if self.mode == 'file':
            line = self.input_fd.readline()
            if not line:
                logging.error("No more input data.")
                sys.exit(1)
            self.output_fd.write(prompt + line)
            return line.strip()
        else:
            return input(prompt)

    def output(self, text):
        """Output text to the user.

        Args:
            text (str): The text to output.
        """
        print(text, file=self.output_fd)

    def close(self):
        """Close any open file descriptors."""
        if self.mode == 'file':
            self.input_fd.close()
            self.output_fd.close()

class CommandProcessor:
    """Processes commands entered by the user."""

    def __init__(self):
        """Initialize the CommandProcessor."""
        self.commands = {
            'restart': ['restart', 'r'],
            'skip': ['skip', 's', 'n', 'next'],
            'quit': ['quit', 'q'],
            'help': ['help', 'h', '?']
        }

    def is_command(self, input_str):
        """Check if the input string is a command.

        Args:
            input_str (str): The input string.

        Returns:
            bool: True if it's a command, False otherwise.
        """
        input_str = input_str.lower()
        for aliases in self.commands.values():
            if input_str in aliases:
                return True
        return False

    def process_command(self, input_str):
        """Process the input command.

        Args:
            input_str (str): The input string.

        Returns:
            str or None: The command name or None if not recognized.
        """
        input_str = input_str.lower()
        for command, aliases in self.commands.items():
            if input_str in aliases:
                return command
        return None

    def get_help_text(self):
        """Get help text for available commands.

        Returns:
            str: Help text.
        """
        help_text = "Available commands:\n"
        for command, aliases in self.commands.items():
            help_text += f"  {', '.join(aliases)}\n"
        return help_text

class Quiz:
    """Main class for running the quiz."""

    def __init__(self, quiz_data, env_handler):
        """
        Initialize the Quiz.

        Args:
            quiz_data (QuizData): The quiz data to use.
            env_handler (EnvironmentHandler): The environment handler.
        """
        self.quiz_data = quiz_data
        self.env_handler = env_handler
        self.command_processor = CommandProcessor()
        self.correct_answers = 0
        self.incorrect_questions = []
        self.skipped_questions = []
        self.question_index = 0

    def start(self):
        """Start the quiz."""
        self.display_quiz_info()
        random.shuffle(self.quiz_data.questions)
        while self.question_index < len(self.quiz_data.questions):
            question = self.quiz_data.questions[self.question_index]
            self.ask_question(question)
            self.question_index += 1
        self.show_results()
        self.env_handler.close()

    def display_quiz_info(self):
        """Display quiz title and description."""
        if self.quiz_data.quiz_info.get('title'):
            self.env_handler.output(f"=== {self.quiz_data.quiz_info['title']} ===")
        if self.quiz_data.quiz_info.get('subtitle'):
            self.env_handler.output(self.quiz_data.quiz_info['subtitle'])
        if self.quiz_data.quiz_info.get('description'):
            self.env_handler.output(self.quiz_data.quiz_info['description'])

    def ask_question(self, question):
        """Present a question to the user and handle the response.

        Args:
            question (dict): The question to ask.
        """
        if question.get('title'):
            self.env_handler.output(f"\n{question['title']}")
        if question.get('subtitle'):
            self.env_handler.output(f"{question['subtitle']}")
        self.env_handler.output(f"\nQuestion {self.question_index + 1}: {question['question']}")
        for idx, option in enumerate(question['options'], start=1):
            self.env_handler.output(f"{idx}. {option}")

        while True:
            user_input = self.env_handler.input("Your answer (or command): ").strip()
            if not (1 <= len(user_input) <= 100):
                self.env_handler.output("Invalid input size. Please try again.")
                continue
            if self.command_processor.is_command(user_input):
                command = self.command_processor.process_command(user_input)
                if command == 'help':
                    self.env_handler.output(self.command_processor.get_help_text())
                elif command == 'skip':
                    self.skipped_questions.append(question)
                    self.env_handler.output("Question skipped.")
                    return
                elif command == 'restart':
                    self.env_handler.output("Restarting quiz...")
                    self.restart_quiz()
                    return
                elif command == 'quit':
                    self.env_handler.output("Exiting quiz.")
                    sys.exit(0)
                else:
                    self.env_handler.output("Unknown command. Type 'help' for available commands.")
            else:
                if not user_input.isdigit():
                    self.env_handler.output("Invalid input. Please enter a valid option number or command.")
                    continue
                option_number = int(user_input)
                if not (1 <= option_number <= len(question['options'])):
                    self.env_handler.output("Invalid option number. Please try again.")
                    continue
                if option_number == question['correct']:
                    self.env_handler.output("Correct!")
                    self.correct_answers += 1
                else:
                    self.env_handler.output("Incorrect.")
                    self.incorrect_questions.append(question)
                return

    def restart_quiz(self):
        """Restart the quiz."""
        self.correct_answers = 0
        self.incorrect_questions = []
        self.skipped_questions = []
        self.question_index = 0
        random.shuffle(self.quiz_data.questions)

    def show_results(self):
        """Display the quiz results to the user."""
        total_questions = len(self.quiz_data.questions)
        self.env_handler.output("\nQuiz Completed!")
        self.env_handler.output(f"Your score: {self.correct_answers}/{total_questions}")
        if self.incorrect_questions:
            self.env_handler.output("\nYou missed the following questions:")
            for question in self.incorrect_questions:
                self.env_handler.output(f"- {question['question']}")
        if self.skipped_questions:
            self.env_handler.output(f"\nSkipped questions: {len(self.skipped_questions)}")

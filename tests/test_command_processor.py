# tests/test_command_processor.py

import unittest
from quiz_core import CommandProcessor

class TestCommandProcessor(unittest.TestCase):
    """Unit tests for the CommandProcessor class."""

    def setUp(self):
        """Set up test environment."""
        self.command_processor = CommandProcessor()

    def test_is_command(self):
        """Test the is_command method with various inputs."""
        self.assertTrue(self.command_processor.is_command('restart'))
        self.assertTrue(self.command_processor.is_command('r'))
        self.assertTrue(self.command_processor.is_command('Skip'))
        self.assertTrue(self.command_processor.is_command('n'))
        self.assertTrue(self.command_processor.is_command('?'))
        self.assertFalse(self.command_processor.is_command('invalid'))

    def test_process_command(self):
        """Test the process_command method with various inputs."""
        self.assertEqual(self.command_processor.process_command('restart'), 'restart')
        self.assertEqual(self.command_processor.process_command('R'), 'restart')
        self.assertEqual(self.command_processor.process_command('s'), 'skip')
        self.assertEqual(self.command_processor.process_command('next'), 'skip')
        self.assertEqual(self.command_processor.process_command('Q'), 'quit')
        self.assertEqual(self.command_processor.process_command('h'), 'help')
        self.assertIsNone(self.command_processor.process_command('unknown'))

    def test_get_help_text(self):
        """Test that help text is generated correctly."""
        help_text = self.command_processor.get_help_text()
        self.assertIn('Available commands:', help_text)
        self.assertIn('restart, r', help_text)
        self.assertIn('skip, s, n, next', help_text)
        self.assertIn('quit, q', help_text)
        self.assertIn('help, h, ?', help_text)

if __name__ == '__main__':
    unittest.main()

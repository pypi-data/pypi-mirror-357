import unittest
from unittest.mock import patch, MagicMock
import sys
import io
from datetime import datetime
from colorama import Fore
from taskman_backend import TaskmanBackend

# Import your main interface functions
from v2_claude_dev import (
    add_task, edit_task, delete_task, 
    start_task, resume_task, 
    notes_interface, fast_notes_interface,
    generate_daily_report
)

class TestTaskmanInterface(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.mock_backend = MagicMock()
        self.test_tasks = []
        
        # Import the module first
        import v2_claude_dev
        
        # Create a patch for the backend
        self.backend_patcher = patch.object(v2_claude_dev, 'backend', self.mock_backend)
        self.backend_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.backend_patcher.stop()

    @patch('builtins.input')
    def test_add_task(self, mock_input):
        """Test adding a task"""
        # Mock user inputs for adding a custom task
        mock_input.side_effect = [
            "1",  # Custom task
            "Test Task",
            "Test Description",
            "2",  # 2 hours
            "30",  # 30 minutes
            "y"   # Confirm
        ]
        
        with patch('v2_claude_dev.tasks', self.test_tasks):
            add_task()
        
        # Verify task was added correctly
        self.assertEqual(len(self.test_tasks), 1)
        self.assertEqual(self.test_tasks[0]['name'], "Test Task")
        self.assertEqual(self.test_tasks[0]['duration'], 9000)  # 2.5 hours in seconds

    @patch('builtins.input')
    def test_edit_task(self, mock_input):
        """Test editing a task"""
        # Add a test task first
        self.test_tasks.append({
            'name': 'Original Task',
            'description': 'Original Description',
            'duration': 3600,
            'status': f"{Fore.YELLOW}Pending"
        })
        
        # Mock user inputs for editing
        mock_input.side_effect = [
            "1",  # Edit name
            "Updated Task",
            "4"   # Save and exit
        ]
        
        with patch('v2_claude_dev.tasks', self.test_tasks):
            with patch('v2_claude_dev.backend', self.mock_backend):
                edit_task(1)
        
        # Verify task was updated
        self.assertEqual(self.test_tasks[0]['name'], "Updated Task")

    def test_delete_task(self):
        """Test deleting a task"""
        # Add a test task
        self.test_tasks.append({
            'name': 'Task to Delete',
            'description': 'Will be deleted',
            'duration': 3600,
            'status': f"{Fore.YELLOW}Pending"
        })
        
        with patch('v2_claude_dev.tasks', self.test_tasks):
            delete_task("d1")  # Delete first task
        
        # Verify task was deleted
        self.assertEqual(len(self.test_tasks), 0)

    @patch('builtins.input')
    def test_generate_daily_report(self, mock_input):
        """Test report generation"""
        # Setup mock backend response
        self.mock_backend.load_tasks.return_value = {
            "tasks": [
                {
                    'name': 'Completed Task',
                    'description': 'Test',
                    'duration': 3600,
                    'status': f"{Fore.GREEN}Completed ✅"
                },
                {
                    'name': 'Pending Task',
                    'description': 'Test',
                    'duration': 1800,
                    'status': f"{Fore.YELLOW}Pending"
                }
            ]
        }
        
        with patch('v2_claude_dev.backend', self.mock_backend):
            report = generate_daily_report()
        
        # Verify report content
        self.assertIsNotNone(report)
        self.assertTrue(any("Completed Task" in str(line) for line in report))
        self.assertTrue(any("Pending Task" in str(line) for line in report))

if __name__ == '__main__':
    unittest.main()
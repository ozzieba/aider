import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from aider.plus.pm import AiderPlusPM
from aider.plus.state import Task, WorkflowState
from aider.utils import IgnorantTemporaryDirectory


class TestPM(unittest.TestCase):
    def setUp(self):
        self.tempdir_obj = IgnorantTemporaryDirectory()
        self.tempdir = Path(self.tempdir_obj.name)
        self.aider_dir = self.tempdir / ".aider"
        self.workflow_file = self.aider_dir / "workflow.json"

    def tearDown(self):
        self.tempdir_obj.cleanup()

    def test_load_state_no_file(self):
        pm = AiderPlusPM(root=self.tempdir)
        state = pm.load_state()
        self.assertIsInstance(state, WorkflowState)
        self.assertEqual(state.goal, "")
        self.assertEqual(state.tasks, [])

    def test_save_and_load_state(self):
        pm = AiderPlusPM(root=self.tempdir)

        # Create a state and save it
        original_state = WorkflowState(
            goal="Test Goal", tasks=[Task(name="Task 1"), Task(name="Task 2")]
        )
        pm.state = original_state
        pm.save_state()

        # Check if file was created
        self.assertTrue(self.workflow_file.exists())

        # Verify content
        with open(self.workflow_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["goal"], "Test Goal")
        self.assertEqual(len(data["tasks"]), 2)

        # Load the state back
        pm_new = AiderPlusPM(root=self.tempdir)
        loaded_state = pm_new.state

        self.assertEqual(loaded_state.goal, original_state.goal)
        self.assertEqual(len(loaded_state.tasks), len(original_state.tasks))
        self.assertEqual(loaded_state.tasks[0].name, original_state.tasks[0].name)
        self.assertEqual(loaded_state, original_state)

    def test_load_state_corrupted_file(self):
        self.aider_dir.mkdir()
        with open(self.workflow_file, "w", encoding="utf-8") as f:
            f.write("this is not json")

        pm = AiderPlusPM(root=self.tempdir)
        state = pm.load_state()
        self.assertIsInstance(state, WorkflowState)
        self.assertEqual(state.goal, "")
        self.assertEqual(state.tasks, [])

    def test_load_state_empty_file(self):
        self.aider_dir.mkdir()
        self.workflow_file.touch()

        pm = AiderPlusPM(root=self.tempdir)
        state = pm.load_state()
        self.assertIsInstance(state, WorkflowState)
        self.assertEqual(state.goal, "")

    def test_init_loads_state(self):
        original_state = WorkflowState(goal="Initial Goal")
        self.aider_dir.mkdir()
        with open(self.workflow_file, "w", encoding="utf-8") as f:
            json.dump(original_state.to_dict(), f)

        pm = AiderPlusPM(root=self.tempdir)
        self.assertEqual(pm.state.goal, "Initial Goal")

    def test_checkpoints(self):
        mock_repo = MagicMock()
        mock_repo.create_task_stash.return_value = True
        mock_repo.restore_task_stash.return_value = True

        pm = AiderPlusPM(repo=mock_repo, root=self.tempdir)
        task = Task(name="test task")

        # Test create checkpoint
        res = pm.create_checkpoint(task)
        self.assertTrue(res)
        mock_repo.create_task_stash.assert_called_once_with(task.id, task.name)

        # Test revert to checkpoint
        res = pm.revert_to_checkpoint(task)
        self.assertTrue(res)
        mock_repo.restore_task_stash.assert_called_once_with(task.id)

    def test_checkpoints_no_repo(self):
        pm = AiderPlusPM(repo=None, root=self.tempdir)
        task = Task(name="test task")

        # Test create checkpoint
        res = pm.create_checkpoint(task)
        self.assertFalse(res)

        # Test revert to checkpoint
        res = pm.revert_to_checkpoint(task)
        self.assertFalse(res)

import json
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aider.plus.pm import AiderPlusPM
from aider.plus.state import Task, TaskStatus, WorkflowState
from aider.utils import GitTemporaryDirectory, IgnorantTemporaryDirectory


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

    @patch("aider.plus.pm.AIEngineeringTeam")
    @patch("aider.coders.Coder.create")
    def test_execute_plan(self, MockCoderCreate, MockTeam):
        with GitTemporaryDirectory() as repo_dir:
            repo_dir = Path(repo_dir)
            test_file = repo_dir / "test_file.py"
            test_file.write_text("def hello():\n    print('Hello, world!')\n")

            # Setup mock team and models
            mock_team_instance = MockTeam.return_value
            mock_coder_model = MagicMock()
            mock_team_instance.get_coder.return_value = mock_coder_model

            pm = AiderPlusPM(
                repo=MagicMock(),
                root=repo_dir,
                main_model=MagicMock(),
                io=MagicMock(),
                team_config={},
            )
            task = Task(name="Refactor hello function")
            pm.state.tasks = [task]

            mock_coder_instance = MockCoderCreate.return_value
            mock_coder_instance.run.return_value = None

            pm.create_checkpoint = MagicMock(return_value=True)
            pm.save_state = MagicMock()

            pm.execute_plan()

            pm.create_checkpoint.assert_called_once_with(task)
            mock_coder_instance.run.assert_called_once_with(with_message="Refactor hello function")
            self.assertEqual(task.status, TaskStatus.COMPLETED)
            pm.save_state.assert_called()

            # Verify the correct model from the team was used
            MockCoderCreate.assert_called_once()
            self.assertEqual(MockCoderCreate.call_args.kwargs["main_model"], mock_coder_model)

    @patch("aider.plus.pm.AIEngineeringTeam")
    @patch("aider.coders.Coder.create")
    @patch("aider.plus.pm.run_cmd")
    def test_execute_plan_with_tdd_and_critique(self, mock_run_cmd, MockCoderCreate, MockTeam):
        with GitTemporaryDirectory() as repo_dir:
            repo_dir = Path(repo_dir)

            # Mocks for Coder instances
            mock_coder_test = MagicMock()
            mock_coder_impl = MagicMock()
            mock_coder_reviewer1 = MagicMock()
            mock_coder_reviewer1.partial_response_content = "This can be improved."
            mock_coder_fixer = MagicMock()
            mock_coder_reviewer2 = MagicMock()
            mock_coder_reviewer2.partial_response_content = ""
            MockCoderCreate.side_effect = [
                mock_coder_test,
                mock_coder_impl,
                mock_coder_reviewer1,
                mock_coder_fixer,
                mock_coder_reviewer2,
            ]

            # Setup mock team and models
            mock_team_instance = MockTeam.return_value
            mock_test_writer_model = MagicMock(name="test_writer_model")
            mock_coder_model = MagicMock(name="coder_model")
            mock_reviewer_model = MagicMock(name="reviewer_model")
            mock_team_instance.get_test_writer.return_value = mock_test_writer_model
            mock_team_instance.get_coder.return_value = mock_coder_model
            mock_team_instance.get_reviewer.return_value = mock_reviewer_model

            # Mock for run_cmd: fail first, then succeed, then succeed again after fix
            mock_run_cmd.side_effect = [
                (1, "tests failed"),
                (0, "tests passed"),
                (0, "tests passed again"),
            ]

            pm = AiderPlusPM(
                repo=MagicMock(),
                root=repo_dir,
                main_model=MagicMock(),
                io=MagicMock(),
                test_cmd="pytest",
                team_config={},
            )
            task = Task(name="Refactor hello function")
            pm.state.tasks = [task]

            pm.create_checkpoint = MagicMock(return_value=True)
            pm.save_state = MagicMock()

            pm.execute_plan()

            # Verify Coder creation
            self.assertEqual(MockCoderCreate.call_count, 5)
            create_calls = MockCoderCreate.call_args_list
            self.assertEqual(create_calls[0].kwargs["main_model"], mock_test_writer_model)
            self.assertEqual(create_calls[1].kwargs["main_model"], mock_coder_model)
            self.assertEqual(create_calls[2].kwargs["main_model"], mock_reviewer_model)
            self.assertEqual(create_calls[3].kwargs["main_model"], mock_coder_model)
            self.assertEqual(create_calls[4].kwargs["main_model"], mock_reviewer_model)

            # Verify test coder was run
            mock_coder_test.run.assert_called_once_with(
                with_message="Write a failing test for: Refactor hello function"
            )

            # Verify run_cmd was called three times
            self.assertEqual(mock_run_cmd.call_count, 3)
            mock_run_cmd.assert_any_call("pytest")

            # Verify implementation coder was run
            mock_coder_impl.run.assert_called_once_with(
                with_message=(
                    "Implement the feature for: Refactor hello function to make the test pass."
                )
            )

            # Verify reviewer1 was run
            mock_coder_reviewer1.run.assert_called_once_with(
                with_message="Critique the implementation for: Refactor hello function"
            )

            # Verify fixer was run
            mock_coder_fixer.run.assert_called_once_with(with_message="This can be improved.")

            # Verify reviewer2 was run
            mock_coder_reviewer2.run.assert_called_once_with(
                with_message="Critique the implementation for: Refactor hello function"
            )

            # Verify task status and state saving
            self.assertEqual(task.status, TaskStatus.COMPLETED)
            pm.save_state.assert_called()

    @patch("aider.plus.pm.AIEngineeringTeam")
    @patch("aider.coders.Coder.create")
    @patch("aider.plus.pm.run_cmd")
    def test_execute_plan_with_tdd(self, mock_run_cmd, MockCoderCreate, MockTeam):
        with GitTemporaryDirectory() as repo_dir:
            repo_dir = Path(repo_dir)

            # Mocks for Coder instances
            mock_coder_test = MagicMock()
            mock_coder_impl = MagicMock()
            mock_reviewer = MagicMock()
            mock_reviewer.partial_response_content = ""  # No critique
            MockCoderCreate.side_effect = [mock_coder_test, mock_coder_impl, mock_reviewer]

            # Setup mock team and models
            mock_team_instance = MockTeam.return_value
            mock_test_writer_model = MagicMock(name="test_writer_model")
            mock_coder_model = MagicMock(name="coder_model")
            mock_reviewer_model = MagicMock(name="reviewer_model")
            mock_team_instance.get_test_writer.return_value = mock_test_writer_model
            mock_team_instance.get_coder.return_value = mock_coder_model
            mock_team_instance.get_reviewer.return_value = mock_reviewer_model

            # Mock for run_cmd: fail first, then succeed
            mock_run_cmd.side_effect = [(1, "tests failed"), (0, "tests passed")]

            pm = AiderPlusPM(
                repo=MagicMock(),
                root=repo_dir,
                main_model=MagicMock(),
                io=MagicMock(),
                test_cmd="pytest",
                team_config={},
            )
            task = Task(name="Refactor hello function")
            pm.state.tasks = [task]

            pm.create_checkpoint = MagicMock(return_value=True)
            pm.save_state = MagicMock()

            pm.execute_plan()

            # Verify Coder creation
            self.assertEqual(MockCoderCreate.call_count, 3)
            create_calls = MockCoderCreate.call_args_list
            self.assertEqual(create_calls[0].kwargs["main_model"], mock_test_writer_model)
            self.assertEqual(create_calls[1].kwargs["main_model"], mock_coder_model)
            self.assertEqual(create_calls[2].kwargs["main_model"], mock_reviewer_model)

            # Verify test coder was run
            mock_coder_test.run.assert_called_once_with(
                with_message="Write a failing test for: Refactor hello function"
            )

            # Verify run_cmd was called twice
            self.assertEqual(mock_run_cmd.call_count, 2)
            mock_run_cmd.assert_any_call("pytest")

            # Verify implementation coder was run
            mock_coder_impl.run.assert_called_once_with(
                with_message="Implement the feature for: Refactor hello function to make the test"
                " pass."
            )

            # Verify reviewer was run
            mock_reviewer.run.assert_called_once_with(
                with_message="Critique the implementation for: Refactor hello function"
            )

            # Verify task status and state saving
            self.assertEqual(task.status, TaskStatus.COMPLETED)
            pm.save_state.assert_called()

    @patch("aider.plus.pm.AIEngineeringTeam")
    @patch("aider.coders.Coder.create")
    def test_execute_plan_in_parallel(self, MockCoderCreate, MockTeam):
        with GitTemporaryDirectory() as repo_dir:
            task_a = Task(name="Task A")
            task_b = Task(name="Task B")
            task_c = Task(name="Task C", dependencies=[task_a.id, task_b.id])

            pm = AiderPlusPM(
                repo=MagicMock(),
                root=repo_dir,
                main_model=MagicMock(),
                io=MagicMock(),
                team_config={},
            )
            pm.state.tasks = [task_a, task_b, task_c]
            pm.save_state = MagicMock()

            # Mock coder execution
            execution_times = {}
            lock = threading.Lock()

            def mock_run(with_message):
                task_name = with_message
                start_time = time.time()
                time.sleep(0.1)  # Simulate work
                end_time = time.time()
                with lock:
                    execution_times[task_name] = (start_time, end_time)

            mock_coder = MagicMock()
            mock_coder.run.side_effect = mock_run
            MockCoderCreate.return_value = mock_coder

            pm.execute_plan()

            # Verify execution times
            self.assertIn("Task A", execution_times)
            self.assertIn("Task B", execution_times)
            self.assertIn("Task C", execution_times)

            start_a, end_a = execution_times["Task A"]
            start_b, end_b = execution_times["Task B"]
            start_c, _ = execution_times["Task C"]

            # Check for parallel execution of A and B (overlap)
            self.assertTrue(start_b < end_a)
            self.assertTrue(start_a < end_b)

            # Check that C starts after both A and B finish
            self.assertTrue(start_c > end_a)
            self.assertTrue(start_c > end_b)

    @patch("aider.plus.pm.AIEngineeringTeam")
    @patch("aider.coders.Coder.create")
    @patch("aider.plus.pm.run_cmd")
    def test_execute_plan_with_failure_and_retry(self, mock_run_cmd, MockCoderCreate, MockTeam):
        with GitTemporaryDirectory() as repo_dir:
            task = Task(name="Task A")
            mock_io = MagicMock()

            pm = AiderPlusPM(
                repo=MagicMock(),
                root=repo_dir,
                main_model=MagicMock(),
                io=mock_io,
                test_cmd="pytest",
            )
            pm.state.tasks = [task]
            pm.revert_to_checkpoint = MagicMock()

            # Mock Coder instances
            mock_coder_test = MagicMock()
            mock_coder_impl_fail = MagicMock()
            mock_coder_impl_success = MagicMock()
            mock_reviewer = MagicMock()
            mock_reviewer.partial_response_content = ""
            MockCoderCreate.side_effect = [
                mock_coder_test,
                mock_coder_impl_fail,
                mock_coder_impl_success,
                mock_reviewer,
            ]

            # Mock run_cmd to fail after 1st impl, then succeed after retry
            mock_run_cmd.side_effect = [
                (1, "tests failed before impl"),  # After test coder
                (1, "tests failed after impl"),  # After 1st impl coder
                (0, "tests passed after retry"),  # After 2nd impl coder
            ]

            # Mock user choosing 'retry'
            mock_io.get_input.return_value = "retry"

            pm.execute_plan()

            # Verify that run_cmd was called three times
            self.assertEqual(mock_run_cmd.call_count, 3)
            # Verify user was asked to retry
            mock_io.get_input.assert_called_once()
            # Verify task is marked as completed
            self.assertEqual(task.status, TaskStatus.COMPLETED)
            # Verify both implementation attempts were made
            mock_coder_impl_fail.run.assert_called_once()
            mock_coder_impl_success.run.assert_called_once()
            # Verify we reverted before retrying
            pm.revert_to_checkpoint.assert_called_once_with(task)

    @patch("aider.plus.pm.AIEngineeringTeam")
    @patch("aider.coders.Coder.create")
    @patch("aider.plus.pm.run_cmd")
    def test_execute_plan_with_failure_and_skip(self, mock_run_cmd, MockCoderCreate, MockTeam):
        with GitTemporaryDirectory() as repo_dir:
            task = Task(name="Task A")
            mock_io = MagicMock()
            pm = AiderPlusPM(
                repo=MagicMock(),
                root=repo_dir,
                main_model=MagicMock(),
                io=mock_io,
                test_cmd="pytest",
            )
            pm.state.tasks = [task]
            MockCoderCreate.return_value = MagicMock()
            mock_run_cmd.side_effect = [(1, "fail"), (1, "fail")]
            mock_io.get_input.return_value = "skip"

            pm.execute_plan()

            self.assertEqual(mock_run_cmd.call_count, 2)
            mock_io.get_input.assert_called_once()
            self.assertEqual(task.status, TaskStatus.COMPLETED)

    @patch("aider.plus.pm.AIEngineeringTeam")
    @patch("aider.coders.Coder.create")
    @patch("aider.plus.pm.run_cmd")
    def test_execute_plan_with_failure_and_abort(self, mock_run_cmd, MockCoderCreate, MockTeam):
        with GitTemporaryDirectory() as repo_dir:
            task_a = Task(name="Task A")
            task_b = Task(name="Task B", dependencies=[task_a.id])
            mock_io = MagicMock()
            pm = AiderPlusPM(
                repo=MagicMock(),
                root=repo_dir,
                main_model=MagicMock(),
                io=mock_io,
                test_cmd="pytest",
            )
            pm.state.tasks = [task_a, task_b]

            mock_coder_test = MagicMock()
            mock_coder_impl = MagicMock()
            MockCoderCreate.side_effect = [mock_coder_test, mock_coder_impl]

            # Test fails, user aborts
            mock_run_cmd.side_effect = [(1, "fail"), (1, "fail")]
            mock_io.get_input.return_value = "abort"

            pm.execute_plan()

            # Verify that the first task failed and the second was not started
            self.assertEqual(task_a.status, TaskStatus.FAILED)
            self.assertEqual(task_b.status, TaskStatus.PENDING)

            # Verify the sequence of calls
            self.assertEqual(mock_run_cmd.call_count, 2)
            mock_io.get_input.assert_called_once()
            mock_coder_test.run.assert_called_once()
            mock_coder_impl.run.assert_called_once()

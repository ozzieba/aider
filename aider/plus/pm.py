import json
from pathlib import Path

from aider.plus.state import TaskStatus, WorkflowState
from aider.run_cmd import run_cmd


class AiderPlusPM:
    def __init__(self, repo=None, root=".", main_model=None, io=None, test_cmd=None):
        self.repo = repo
        self.main_model = main_model
        self.io = io
        self.test_cmd = test_cmd
        if self.repo:
            self.root = Path(self.repo.root)
        else:
            self.root = Path(root)
        self.workflow_file = self.root / ".aider" / "workflow.json"
        self.state = self.load_state()

    def save_state(self):
        """
        Saves the current WorkflowState to .aider/workflow.json.
        """
        self.workflow_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.workflow_file, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, indent=4)

    def load_state(self):
        """
        Loads WorkflowState from .aider/workflow.json.
        Returns a new WorkflowState if the file doesn't exist or is invalid.
        """
        if not self.workflow_file.exists():
            return WorkflowState()
        try:
            with open(self.workflow_file, "r", encoding="utf-8") as f:
                content = f.read()
                if not content:
                    return WorkflowState()
                data = json.loads(content)
            return WorkflowState.from_dict(data)
        except (json.JSONDecodeError, FileNotFoundError, TypeError, KeyError):
            # If file is corrupted, malformed, or empty, start fresh
            return WorkflowState()

    def make_plan(self, goal):
        """
        Uses an LLM to break down the user's goal into a multi-step plan.
        This is a placeholder and will be implemented in a future step.
        """
        pass

    def create_checkpoint(self, task):
        """Creates a git stash checkpoint for the given task."""
        if not self.repo:
            return False
        return self.repo.create_task_stash(task.id, task.name)

    def revert_to_checkpoint(self, task):
        """Reverts the repo to the git stash checkpoint for the given task."""
        if not self.repo:
            return False
        return self.repo.restore_task_stash(task.id)

    def execute_plan(self):
        """
        Executes the plan stored in the WorkflowState.
        """
        from aider.coders import Coder

        for task in self.state.tasks:
            if task.status == TaskStatus.PENDING:
                self.create_checkpoint(task)

                if self.test_cmd:
                    # TDD Cycle
                    # 1. Write a failing test
                    test_coder = Coder.create(
                        main_model=self.main_model,
                        io=self.io,
                        repo=self.repo,
                    )
                    test_coder.run(with_message=f"Write a failing test for: {task.name}")

                    # 2. Run the test, expect failure
                    exit_code, _ = run_cmd(self.test_cmd)
                    if exit_code == 0:
                        if self.io:
                            self.io.tool_warning(
                                f"Tests passed for `{task.name}` before implementation. Skipping"
                                " implementation."
                            )
                        task.status = TaskStatus.COMPLETED
                        self.save_state()
                        continue

                    # 3. Implement the feature
                    impl_coder = Coder.create(
                        main_model=self.main_model,
                        io=self.io,
                        repo=self.repo,
                    )
                    impl_coder.run(
                        with_message=(
                            f"Implement the feature for: {task.name} to make the test"
                            " pass."
                        )
                    )

                    # 4. Run the test, expect success
                    exit_code, _ = run_cmd(self.test_cmd)
                    if exit_code != 0:
                        if self.io:
                            self.io.tool_error(
                                f"Tests failed for `{task.name}` after implementation."
                            )
                        task.status = TaskStatus.FAILED
                        self.save_state()
                        continue
                else:
                    # Standard execution without TDD
                    coder = Coder.create(
                        main_model=self.main_model,
                        io=self.io,
                        repo=self.repo,
                    )
                    coder.run(with_message=task.name)

                task.status = TaskStatus.COMPLETED
                self.save_state()

import json
from pathlib import Path

from aider.plus.state import WorkflowState


class AiderPlusPM:
    def __init__(self, repo=None, root=".", main_model=None, io=None):
        self.repo = repo
        self.main_model = main_model
        self.io = io
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

import json
from pathlib import Path

from aider.plus.state import WorkflowState


class AiderPlusPM:
    def __init__(self, root="."):
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

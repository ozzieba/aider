import json
import unittest
from uuid import UUID, uuid4

from aider.plus.state import Task, TaskStatus, WorkflowState


class TestState(unittest.TestCase):
    def test_task_instantiation(self):
        task = Task(name="Test Task", agent="planner")
        self.assertIsInstance(task.id, UUID)
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.agent, "planner")
        self.assertEqual(task.dependencies, [])
        self.assertIsNone(task.result)
        self.assertEqual(task.history, [])

    def test_workflow_state_instantiation(self):
        state = WorkflowState(goal="Test Goal")
        self.assertEqual(state.goal, "Test Goal")
        self.assertEqual(state.tasks, [])

    def test_task_serialization(self):
        task_id = uuid4()
        dep_id = uuid4()
        task = Task(
            id=task_id,
            name="Test Task",
            status=TaskStatus.COMPLETED,
            dependencies=[dep_id],
            agent="executor",
            result="Success",
            history=["action1", "action2"],
        )
        task_dict = task.to_dict()

        # for JSON compatibility check
        json.dumps(task_dict)

        self.assertEqual(task_dict["id"], str(task_id))
        self.assertEqual(task_dict["name"], "Test Task")
        self.assertEqual(task_dict["status"], "completed")
        self.assertEqual(task_dict["dependencies"], [str(dep_id)])
        self.assertEqual(task_dict["agent"], "executor")
        self.assertEqual(task_dict["result"], "Success")
        self.assertEqual(task_dict["history"], ["action1", "action2"])

        # Test deserialization
        new_task = Task.from_dict(task_dict)
        self.assertEqual(task, new_task)

    def test_workflow_state_with_tasks_serialization(self):
        task1 = Task(name="Task 1")
        task2 = Task(name="Task 2")
        state = WorkflowState(goal="Main Goal", tasks=[task1, task2])
        state_dict = state.to_dict()

        # for JSON compatibility check
        json.dumps(state_dict)

        self.assertEqual(state_dict["goal"], "Main Goal")
        self.assertEqual(len(state_dict["tasks"]), 2)
        self.assertEqual(state_dict["tasks"][0]["name"], "Task 1")
        self.assertEqual(state_dict["tasks"][1]["name"], "Task 2")

        # Test deserialization
        new_state = WorkflowState.from_dict(state_dict)
        self.assertEqual(state, new_state)

    def test_task_status_enum(self):
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        self.assertEqual(TaskStatus.FAILED.value, "failed")

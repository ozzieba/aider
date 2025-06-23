from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[UUID] = field(default_factory=list)
    agent: str = ""
    result: Optional[str] = None
    history: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "status": self.status.value,
            "dependencies": [str(d) for d in self.dependencies],
            "agent": self.agent,
            "result": self.result,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            status=TaskStatus(data["status"]),
            dependencies=[UUID(d) for d in data.get("dependencies", [])],
            agent=data["agent"],
            result=data.get("result"),
            history=data.get("history", []),
        )


@dataclass
class WorkflowState:
    goal: str = ""
    tasks: List[Task] = field(default_factory=list)

    def to_dict(self):
        return {
            "goal": self.goal,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            goal=data["goal"],
            tasks=[Task.from_dict(t) for t in data["tasks"]],
        )

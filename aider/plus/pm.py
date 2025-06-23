import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from aider.plus.state import Task, TaskStatus, WorkflowState
from aider.plus.team import AIEngineeringTeam
from aider.run_cmd import run_cmd


class _AbortExecution(Exception):
    pass


class AiderPlusPM:
    def __init__(self, repo=None, root=".", main_model=None, io=None, test_cmd=None, team_config=None):
        self.repo = repo
        self.team = AIEngineeringTeam(main_model, team_config=team_config)
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

    def _execute_task(self, task):
        from aider.coders import Coder

        self.create_checkpoint(task)

        if self.test_cmd:
            # TDD Cycle
            # 1. Write a failing test
            test_coder = Coder.create(
                main_model=self.team.get_test_writer(),
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
                return TaskStatus.COMPLETED

            # 3. Implement the feature
            while True:
                impl_coder = Coder.create(
                    main_model=self.team.get_coder(),
                    io=self.io,
                    repo=self.repo,
                )
                impl_coder.run(
                    with_message=f"Implement the feature for: {task.name} to make the test"
                    " pass."
                )

                # 4. Run the test, expect success
                exit_code, output = run_cmd(self.test_cmd)
                if exit_code == 0:
                    break  # Success

                if not self.io:
                    return TaskStatus.FAILED

                error_message = f"Tests failed for `{task.name}` after implementation."
                if output:
                    error_message += f"\n{output}"
                self.io.tool_error(error_message)

                response = self.io.get_input(
                    "Choose an action: [Retry|Skip|Abort] ",
                    default="retry",
                ).lower()

                if response == "retry":
                    self.revert_to_checkpoint(task)
                    continue
                elif response == "skip":
                    return TaskStatus.COMPLETED
                elif response == "abort":
                    raise _AbortExecution()
                else:
                    return TaskStatus.FAILED

            # 5. Critique and self-correction loop
            while True:
                reviewer = Coder.create(
                    main_model=self.team.get_reviewer(), io=self.io, repo=self.repo
                )
                reviewer.run(with_message=f"Critique the implementation for: {task.name}")
                critique = reviewer.partial_response_content.strip()

                if not critique:
                    break

                fixer = Coder.create(main_model=self.team.get_coder(), io=self.io, repo=self.repo)
                fixer.run(with_message=critique)

                exit_code, _ = run_cmd(self.test_cmd)
                if exit_code != 0:
                    if self.io:
                        self.io.tool_error(
                            f"Tests failed for `{task.name}` after applying critique."
                        )
                    return TaskStatus.FAILED  # For now, just fail
        else:
            # Standard execution without TDD
            coder = Coder.create(
                main_model=self.team.get_coder(),
                io=self.io,
                repo=self.repo,
            )
            coder.run(with_message=task.name)

        return TaskStatus.COMPLETED

    def execute_plan(self):
        """
        Executes the plan stored in the WorkflowState.
        """
        completed_tasks = {
            task.id for task in self.state.tasks if task.status == TaskStatus.COMPLETED
        }
        in_progress_tasks = set()

        with ThreadPoolExecutor() as executor:
            while len(completed_tasks) < len(self.state.tasks):
                runnable_tasks = [
                    task
                    for task in self.state.tasks
                    if task.status == TaskStatus.PENDING
                    and task.id not in in_progress_tasks
                    and all(dep in completed_tasks for dep in task.dependencies)
                ]

                if not runnable_tasks and not in_progress_tasks:
                    # No runnable tasks and no tasks in progress, so we're done or stuck
                    break

                futures = {
                    executor.submit(self._execute_task, task): task for task in runnable_tasks
                }
                for task in runnable_tasks:
                    task.status = TaskStatus.IN_PROGRESS
                    in_progress_tasks.add(task.id)

                try:
                    for future in as_completed(futures):
                        task = futures[future]
                        try:
                            result_status = future.result()
                            task.status = result_status
                            if result_status == TaskStatus.COMPLETED:
                                completed_tasks.add(task.id)
                        except _AbortExecution:
                            if self.io:
                                self.io.tool_error(f"Execution aborted during task {task.name}.")
                            task.status = TaskStatus.FAILED

                            # Cancel other futures and set their tasks to PENDING
                            for f, t in futures.items():
                                if f != future:
                                    f.cancel()
                                    if t.status == TaskStatus.IN_PROGRESS:
                                        t.status = TaskStatus.PENDING

                            self.save_state()
                            return
                        except Exception as e:
                            if self.io:
                                self.io.tool_error(f"Error executing task {task.name}: {e}")
                            task.status = TaskStatus.FAILED
                        finally:
                            in_progress_tasks.remove(task.id)
                            self.save_state()
                except KeyboardInterrupt:
                    if self.io:
                        self.io.tool_error("Execution interrupted.")
                    for f in futures:
                        f.cancel()
                    return

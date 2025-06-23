import subprocess
from pathlib import Path

from aider.run_cmd import run_cmd


class Sandbox:
    def __init__(self, config=None, root=None, io=None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", False)
        self.sandbox_type = self.config.get("type", "docker")
        self.docker_image = self.config.get("docker_image")
        self.root = Path(root) if root else Path.cwd()
        self.io = io

    def run(self, command):
        if not self.enabled:
            return run_cmd(command, cwd=self.root)

        if self.sandbox_type == "docker":
            return self.run_in_docker(command)
        else:
            if self.io:
                self.io.tool_error(
                    f"Unsupported sandbox type: {self.sandbox_type}. Only 'docker' is currently"
                    " supported."
                )
            return 1, f"Unsupported sandbox type: {self.sandbox_type}"

    def run_in_docker(self, command):
        if not self.docker_image:
            if self.io:
                self.io.tool_error("Docker sandbox is enabled but no docker_image is configured.")
            return 1, "Docker sandbox enabled but no docker_image configured."

        # Check if docker is available
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            if self.io:
                self.io.tool_error("Docker is not available. Please install it to use the sandbox.")
            return 1, "Docker not found."

        # Basic check to see if image exists
        try:
            subprocess.run(
                ["docker", "image", "inspect", self.docker_image], check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            if self.io:
                self.io.tool_error(
                    f"Docker image '{self.docker_image}' not found. Please build or pull it."
                )
            return 1, f"Docker image '{self.docker_image}' not found."

        docker_command_str = (
            f"docker run --rm -v '{self.root.resolve()}:/app' -w /app {self.docker_image}"
            f" {command}"
        )

        return run_cmd(docker_command_str)

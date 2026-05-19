"""Service tool for starting background services with task isolation."""

import os
import asyncio
from typing import Any, TYPE_CHECKING

from loguru import logger

from nanobot.agent.tools.base import Tool, tool_parameters
from nanobot.agent.tools.schema import StringSchema, tool_parameters_schema

if TYPE_CHECKING:
    from nanobot.usage.services import ServiceManager
    from nanobot.agent.tools.context import ToolContext


@tool_parameters(
    tool_parameters_schema(
        task_id=StringSchema("Unique identifier for this service (e.g. 'todo-backend')"),
        command=StringSchema("The shell command to start the service (e.g. 'python app.py')"),
        required=["task_id", "command"],
    )
)
class StartServiceTool(Tool):
    """Tool to start a background service with an automatically assigned port."""

    @classmethod
    def enabled(cls, ctx: "ToolContext") -> bool:
        return ctx.service_manager is not None

    @classmethod
    def create(cls, ctx: "ToolContext") -> StartServiceTool:
        assert ctx.service_manager is not None
        return cls(service_manager=ctx.service_manager)

    def __init__(self, service_manager: "ServiceManager"):
        self._service_manager = service_manager

    @property
    def name(self) -> str:
        return "start_service"

    @property
    def description(self) -> str:
        return (
            "Start a background service with an automatically assigned port. "
            "The service will be isolated by task_id and accessible via /proxy/<task_id>/. "
            "The assigned port is provided to the service via the PORT environment variable. "
            "Use this for running backends, databases, or any long-running process."
        )

    async def execute(self, task_id: str, command: str, **kwargs: Any) -> str:
        """Start the service and register it."""
        try:
            # 1. Find a free port
            port = self._service_manager.find_free_port()
            
            # 2. Register the mapping
            self._service_manager.register_service(task_id, port)
            
            # 3. Launch the process in background
            # We use nohup and redirect to a log file in the workspace
            log_file = self._service_manager.workspace / f"service_{task_id}.log"
            
            # Prepare the environment
            env = os.environ.copy()
            env["PORT"] = str(port)
            
            # Wrap the command to run in background and detach
            full_command = f"nohup {command} > {log_file} 2>&1 &"
            
            # We use asyncio.create_subprocess_shell but we don't wait for it
            # since it's a background service.
            process = await asyncio.create_subprocess_shell(
                full_command,
                cwd=str(self._service_manager.workspace),
                env=env,
                start_new_session=True # Detach from parent
            )
            
            return (
                f"Service '{task_id}' started successfully.\n"
                f"- Internal Port: {port}\n"
                f"- Log File: service_{task_id}.log\n"
                f"- Proxy URL: /proxy/{task_id}/\n\n"
                f"You can now tell the user they can reach this service via the proxy URL."
            )
        except Exception as e:
            logger.error("Failed to start service {}: {}", task_id, e)
            return f"Error: Failed to start service: {str(e)}"

"""Service and port management for full-stack apps."""

import json
import socket
from pathlib import Path
from typing import Any

from loguru import logger


class ServiceManager:
    """Manages internal services and port mappings."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.services_file = workspace / "services.json"
        self._mappings: dict[str, int] = self._load()

    def _load(self) -> dict[str, int]:
        if not self.services_file.exists():
            return {}
        try:
            return json.loads(self.services_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Failed to load services mapping: {}", e)
            return {}

    def _save(self) -> None:
        try:
            self.services_file.write_text(
                json.dumps(self._mappings, indent=2), encoding="utf-8"
            )
        except Exception as e:
            logger.warning("Failed to save services mapping: {}", e)

    def find_free_port(self, start_port: int = 10000, end_port: int = 20000) -> int:
        """Find an available TCP port."""
        # First, check if we already have a mapping for this task_id? 
        # No, this is a general finder.
        
        # Check active mappings first to avoid collisions
        active_ports = set(self._mappings.values())
        
        for port in range(start_port, end_port):
            if port in active_ports:
                continue
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        raise RuntimeError("No free ports available in range")

    def register_service(self, task_id: str, port: int) -> None:
        """Register a port for a task ID."""
        self._mappings[task_id] = port
        self._save()

    def get_port(self, task_id: str) -> int | None:
        """Get the port for a task ID."""
        return self._mappings.get(task_id)

    def list_services(self) -> dict[str, int]:
        """List all registered services."""
        return self._mappings.copy()

"""Path resolver for finding absolute paths to commands."""

import logging
import shutil
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


class PathResolver:
    """Resolves absolute paths for commands like uvx and npx."""

    def __init__(self):
        """Initialize the path resolver."""
        self._cached_paths = {}

    async def resolve_command_path(self, command: str) -> Optional[str]:
        """Resolve the absolute path for a command."""
        if command in self._cached_paths:
            return self._cached_paths[command]

        try:
            absolute_path = shutil.which(command)
            if absolute_path:
                self._cached_paths[command] = absolute_path
                logger.debug(f"Resolved {command} to {absolute_path}")
                return absolute_path
            else:
                logger.warning(f"Could not find command: {command}")
                return None
        except Exception as e:
            logger.error(f"Error resolving path for {command}: {e}")
            return None

    def clear_cache(self):
        """Clear the cached paths."""
        self._cached_paths.clear()
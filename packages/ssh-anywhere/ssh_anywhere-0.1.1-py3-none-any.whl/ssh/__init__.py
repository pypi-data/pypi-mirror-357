"""SSH Anywhere - High-performance SSH library with unified API for direct and jump host connections."""

from .client import SSHClient, CommandResult
from .exceptions import SSHConnectionError, SSHAuthenticationError, SSHError
from .utils import cleanup_ssh_sockets

__version__ = "0.1.1"
__all__ = [
    "SSHClient",
    "CommandResult", 
    "SSHConnectionError",
    "SSHAuthenticationError",
    "SSHError",
    "cleanup_ssh_sockets"
] 
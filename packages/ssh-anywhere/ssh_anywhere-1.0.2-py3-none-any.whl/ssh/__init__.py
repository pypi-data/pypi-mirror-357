"""
SSH Anywhere - A unified SSH client library for Python.

This library provides a simple, unified interface for SSH connections
with support for direct connections, jump hosts, and various authentication methods.
"""

__version__ = "1.0.2"
__author__ = "Cyril Chabarot"
__email__ = "cyril@chabarot.fr"

from .client import SSHClient, CommandResult
from .exceptions import SSHError, SSHConnectionError, SSHAuthenticationError, SSHCommandError, SSHTimeoutError
from .utils import cleanup_ssh_sockets

__all__ = [
    'SSHClient',
    'CommandResult', 
    'SSHError',
    'SSHConnectionError',
    'SSHAuthenticationError', 
    'SSHCommandError',
    'SSHTimeoutError',
    "cleanup_ssh_sockets"
] 
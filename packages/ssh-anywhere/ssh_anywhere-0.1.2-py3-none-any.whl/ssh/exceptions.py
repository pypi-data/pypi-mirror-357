"""SSH-related exceptions."""


class SSHError(Exception):
    """Base SSH exception."""
    pass


class SSHConnectionError(SSHError):
    """SSH connection failed."""
    pass


class SSHAuthenticationError(SSHError):
    """SSH authentication failed."""
    pass


class SSHCommandError(SSHError):
    """SSH command execution failed."""
    pass


class SSHTimeoutError(SSHError):
    """SSH operation timed out."""
    pass
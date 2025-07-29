"""Unified SSH client supporting both direct and jump host connections."""

import os
import sys
import subprocess
import signal
import termios
import time
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Union

try:
    from .exceptions import *
except ImportError:
    # Handle direct imports when not run as a package
    from exceptions import *


class CommandResult:
    """Result of an SSH command execution."""
    
    def __init__(self, returncode: int, stdout: str, stderr: str, success: bool = None):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.success = success if success is not None else (returncode == 0)


class SSHClient:
    """Unified SSH client for direct and jump host connections.
    
    This client can:
    - Connect directly to a host
    - Connect through a jump host (or chain of jump hosts)
    - Use password or key authentication
    - Maintain persistent control sockets for fast subsequent connections
    """
    
    def __init__(self,
                 hostname: str,
                 username: str = None,
                 port: int = 22,
                 password: str = None,
                 private_key_path: str = None,
                 jump_host: Optional['SSHClient'] = None,
                 ssh_options: Dict[str, Any] = None,
                 establish_master: bool = True):
        """
        Initialize SSH client.
        
        Args:
            hostname: Target hostname or IP
            username: SSH username (defaults to current user)
            port: SSH port (default: 22)
            password: Password for authentication (optional)
            private_key_path: Path to private key (optional)
            jump_host: Another SSHClient instance to use as jump host
            ssh_options: Additional SSH options
            establish_master: Whether to establish control master on init
        """
        # Input validation
        if not hostname or not hostname.strip():
            raise ValueError("Hostname cannot be empty")
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        
        self.hostname = hostname.strip()
        self.username = username or os.getenv('USER')
        self.port = port
        self.password = password
        self.private_key_path = Path(private_key_path).expanduser() if private_key_path else None
        self.jump_host = jump_host
        self.ssh_options = ssh_options or {}
        
        # Determine authentication type and key passphrase
        self._setup_authentication()
        
        # Setup sockets directory
        self.sockets_dir = Path.home() / ".ssh" / "sockets"
        self.sockets_dir.mkdir(mode=0o700, exist_ok=True)
        
        # Control socket for this connection
        self.control_socket = self.sockets_dir / f"ctl.{self.username}@{self.hostname}:{self.port}"
        
        # Establish master connection if requested
        if establish_master:
            self._establish_master_connection()
    
    def _setup_authentication(self):
        """
        Set up authentication type and key passphrase based on provided parameters.
        
        Rules:
        1. If password is None, use key-based authentication
        2. If password is not None and private_key_path exists, use key with passphrase
        3. If password is not None and no private_key_path, use password authentication
        """
        if self.password is None:
            # Rule 1: No password -> key-based auth
            self.use_password_auth = False
            self.key_passphrase = None
        elif self.private_key_path and self.private_key_path.exists():
            # Rule 2: Password + key exists -> key auth with passphrase
            self.use_password_auth = False
            self.key_passphrase = self.password
        else:
            # Rule 3: Password + no key -> password auth
            self.use_password_auth = True
            self.key_passphrase = None
    
    def _clean_command_output(self, output: str) -> str:
        """Clean command output by removing pagination artifacts and debug messages."""
        if not output:
            return output
            
        import re
        
        lines = output.split('\n')
        cleaned_lines = []
        content_started = False
        
        for line in lines:
            # Skip spawn command lines
            if line.startswith('spawn ssh'):
                continue
            # Skip debug messages
            if 'DEBUG:' in line:
                continue
            # Skip pagination prompts and artifacts
            if '--More--' in line:
                continue
            if 'Press any key to continue' in line:
                continue
            if line.strip() == 'Unknown action 0':
                continue
            # Skip expect log messages
            if line.startswith('send ') or line.startswith('expect '):
                continue
            
            # Handle shell prompts - use a simpler, more robust approach
            # Look for pattern: anything ending with " # " followed by content
            if ' # ' in line:
                # Split on the first occurrence of " # "
                parts = line.split(' # ', 1)
                if len(parts) == 2:
                    prompt_part = parts[0] + ' # '
                    content_part = parts[1]
                    
                    # If this line contains the command being executed, skip it entirely
                    if any(cmd in content_part for cmd in ['get ', 'show ', 'config ', 'end']):
                        continue
                        
                    # If there's actual output after the prompt, keep only the content
                    if content_part.strip():
                        line = content_part.strip()
                    else:
                        continue
                else:
                    # Line just ends with " # " (bare prompt)
                    if line.strip().endswith(' # ') or line.strip().endswith(' #'):
                        continue
            
            # Remove ANSI escape sequences
            if '\x1b[' in line:
                line = re.sub(r'\x1b\[[0-9;]*[mK]', '', line)
                line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)
            
            # Remove carriage returns
            line = line.replace('\r', '')
            
            # If we haven't started content yet, look for the first real content line
            if not content_started:
                # Real content usually starts with actual data, not prompts or commands
                if line.strip() and not line.strip().startswith(('get ', 'show ', 'config ', '#', '$', '>')):
                    content_started = True
                    cleaned_lines.append(line)
                # Skip everything before content starts
                continue
            else:
                # Add line if we're in content mode
                cleaned_lines.append(line)
        
        # Join and clean up whitespace
        result = '\n'.join(cleaned_lines)
        
        # Remove any blank lines that were left by pagination prompts
        lines = result.split('\n')
        final_lines = []
        
        for i, line in enumerate(lines):
            # If this is a blank line, check context
            if line.strip() == '':
                # Look at previous and next lines to see if this blank line makes sense
                prev_line = lines[i-1].strip() if i > 0 else ''
                next_line = lines[i+1].strip() if i < len(lines)-1 else ''
                
                # Keep blank lines that separate logical sections
                # But remove ones that seem to be pagination artifacts
                if prev_line and next_line:
                    # If both adjacent lines contain substantive content, keep one blank line
                    if not final_lines or final_lines[-1].strip() != '':
                        final_lines.append('')
                else:
                    # Skip isolated blank lines
                    continue
            else:
                final_lines.append(line)
        
        result = '\n'.join(final_lines)
        
        # Remove multiple consecutive newlines (more than 1)
        result = re.sub(r'\n\s*\n+', '\n', result)
        
        # Remove leading/trailing whitespace
        result = result.strip()
        
        return result
    
    def _build_proxy_command(self) -> Optional[str]:
        """Build ProxyCommand string if using jump host."""
        if not self.jump_host:
            return None
            
        # Always use the jump host's control socket for the proxy
        # This ensures we benefit from the jump host's multiplexing
        return f"ssh -o ControlPath={self.jump_host.control_socket} -o ControlMaster=no -W %h:%p {self.jump_host.username}@{self.jump_host.hostname}"
    
    def _establish_master_connection(self):
        """Establish a persistent master connection."""
        if self.control_socket.exists():
            return  # Socket already exists
            
        print(f"Establishing control master for {self.username}@{self.hostname}...")
        
        # Build SSH command for master connection
        ssh_cmd = [
            'ssh',
            '-f',  # Background
            '-N',  # No command
            '-M',  # Master mode
            '-o', f'ControlPath={self.control_socket}',
            '-o', 'ControlPersist=600',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'LogLevel=ERROR',
            '-p', str(self.port)
        ]
        
        # Add proxy command if using jump host
        proxy_command = self._build_proxy_command()
        if proxy_command:
            # For jump hosts, create a temporary script to avoid quoting issues
            proxy_script_content = f"#!/bin/bash\n{proxy_command}"
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(proxy_script_content)
                proxy_script_path = f.name
            os.chmod(proxy_script_path, 0o755)
            ssh_cmd.extend(['-o', f'ProxyCommand={proxy_script_path} %h %p'])
        else:
            proxy_script_path = None
        
        # Add authentication options
        if self.use_password_auth:
            # Password authentication
            ssh_cmd.extend([
                '-o', 'PasswordAuthentication=yes',
                '-o', 'PubkeyAuthentication=no',
                '-o', 'PreferredAuthentications=password,keyboard-interactive'
            ])
        else:
            # Key authentication (default)
            ssh_cmd.extend([
                '-o', 'PasswordAuthentication=no',
                '-o', 'PubkeyAuthentication=yes'
            ])
            if self.private_key_path and self.private_key_path.exists():
                ssh_cmd.extend(['-o', f'IdentityFile={self.private_key_path}'])
        
        ssh_cmd.append(f'{self.username}@{self.hostname}')
        
        try:
            if self.use_password_auth and proxy_command:
                # For password auth through jump hosts, use expect to establish master
                print(f"Attempting to establish control master with expect...")
                self._establish_master_with_expect()
                return
            elif self.use_password_auth:
                # Direct password auth without jump host
                print(f"Note: Using password authentication - control socket will be created on first use")
                return
            else:
                # Key-based auth - establish master connection
                result = subprocess.run(
                    ssh_cmd,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=15
                )
                
                # Give it time to establish
                time.sleep(2)
                
                # Check if socket was created
                if self.control_socket.exists():
                    print(f"✓ Control master established for {self.username}@{self.hostname}")
                else:
                    print("Warning: Control socket not created, will be established on first use")
                    if result.stderr:
                        print(f"SSH output: {result.stderr.decode()}")
                    
        except Exception as e:
            print(f"Error establishing master: {e}")
        finally:
            # Clean up proxy script
            if proxy_script_path:
                try:
                    os.unlink(proxy_script_path)
                except:
                    pass
    
    def _establish_master_with_expect(self):
        """Establish master connection using expect for password authentication."""
        if not shutil.which('expect'):
            print("expect not found, skipping master establishment")
            return
            
        # Create proxy script to avoid quoting issues
        proxy_script_content = f'''#!/bin/bash
ssh -o ControlPath={self.jump_host.control_socket} \\
    -o ControlMaster=no \\
    -W "$1:$2" \\
    {self.jump_host.username}@{self.jump_host.hostname}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(proxy_script_content)
            proxy_script_path = f.name
        os.chmod(proxy_script_path, 0o755)
        
        # Escape password for expect
        escaped_password = self.password
        for char, escape in [('\\', '\\\\'), ('"', '\\"'), ('$', '\\$'), ('[', '\\['), (']', '\\]'), ('{', '\\{'), ('}', '\\}')]:
            escaped_password = escaped_password.replace(char, escape)
        
        # Create expect script for master establishment
        expect_script = f'''#!/usr/bin/expect -f
set timeout 30

# Spawn SSH in master mode, background after auth
spawn ssh -f -N -M \\
    -o ControlPath={self.control_socket} \\
    -o ControlPersist=600 \\
    -o StrictHostKeyChecking=no \\
    -o UserKnownHostsFile=/dev/null \\
    -o LogLevel=ERROR \\
    -o ProxyCommand="{proxy_script_path} %h %p" \\
    -o PasswordAuthentication=yes \\
    -o PubkeyAuthentication=no \\
    -p {self.port} \\
    {self.username}@{self.hostname}

expect {{
    "Are you sure you want to continue connecting" {{
        send "yes\\r"
        exp_continue
    }}
    "password:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Password:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "*password*:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Enter passphrase for key*:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Bad passphrase*" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Permission denied" {{
        exit 1
    }}
    eof {{
        # SSH has backgrounded successfully
        exit 0
    }}
    timeout {{
        exit 1
    }}
}}

# Wait for backgrounding to complete
wait
exit 0
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as f:
            f.write(expect_script)
            expect_file = f.name
        os.chmod(expect_file, 0o755)
        
        try:
            # Run expect script
            result = subprocess.run(['expect', expect_file], 
                                  capture_output=True, text=True, timeout=30)
            
            # Debug output
            if result.returncode != 0:
                print(f"Expect failed with code {result.returncode}")
                if result.stderr:
                    print(f"Expect stderr: {result.stderr}")
            
            # Give it time to establish
            time.sleep(2)
            
            # Check if socket was created
            if self.control_socket.exists():
                print(f"✓ Control master established for {self.username}@{self.hostname}")
            else:
                print(f"Note: Control socket not established, will use on-demand authentication")
                if result.stdout:
                    print(f"Debug - expect output: {result.stdout[:200]}...")
                
        except Exception as e:
            print(f"Error establishing master with expect: {e}")
        finally:
            # Clean up scripts
            try:
                os.unlink(expect_file)
                os.unlink(proxy_script_path)
            except:
                pass
    
    def _build_ssh_command(self, command: str = None) -> list:
        """Build SSH command list."""
        cmd = ['ssh']
        
        # Basic options
        cmd.extend([
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'LogLevel=ERROR',
            '-o', 'CheckHostIP=no',
            '-o', 'GlobalKnownHostsFile=/dev/null',
            '-o', f'ControlPath={self.control_socket}',
            '-o', 'ControlMaster=auto',
            '-o', 'ControlPersist=600',
            '-p', str(self.port)
        ])
        
        # ProxyCommand if using jump host
        proxy_command = self._build_proxy_command()
        if proxy_command:
            cmd.extend(['-o', f'ProxyCommand={proxy_command}'])
        
        # Authentication
        if self.use_password_auth:
            cmd.extend([
                '-o', 'PasswordAuthentication=yes',
                '-o', 'PubkeyAuthentication=no',
                '-o', 'PreferredAuthentications=password,keyboard-interactive'
            ])
        else:
            if self.private_key_path and self.private_key_path.exists():
                cmd.extend(['-o', f'IdentityFile={self.private_key_path}'])
                
        # Additional SSH options
        for key, value in self.ssh_options.items():
            if key != 'ProxyCommand':  # Don't override our ProxyCommand
                cmd.extend(['-o', f'{key}={value}'])
                
        # Target
        cmd.append(f'{self.username}@{self.hostname}')
        
        # Command
        if command:
            cmd.append(command)
            
        return cmd
    
    def exec_cmd(self, command: str, timeout: int = 30) -> CommandResult:
        """Execute a command via SSH."""
        # If we have a control socket, try to use it first (multiplexed)
        if self.control_socket.exists():
            try:
                return self._execute_command_direct(command, timeout)
            except Exception:
                # Fall back to expect if direct fails
                pass
        
        # Use appropriate method based on authentication
        if self.use_password_auth or self.key_passphrase:
            # Use expect for password authentication or key with passphrase
            return self._execute_command_with_expect(command, timeout)
        else:
            # Use direct SSH for key-based authentication without passphrase
            return self._execute_command_direct(command, timeout)
    
    def exec_sequential_commands(self, commands: list, timeout: int = 60, command_delay: float = 0.5) -> list:
        """
        Execute a list of commands sequentially while maintaining session state.
        
        Args:
            commands: List of commands to execute in sequence
            timeout: Total timeout for the entire sequence
            command_delay: Delay between commands in seconds
            
        Returns:
            List of CommandResult objects, one for each command
        """
        if not commands:
            return []
            
        # Use expect for sequential commands to maintain state
        if self.use_password_auth or self.key_passphrase:
            return self._execute_sequential_commands_with_expect(commands, timeout, command_delay)
        else:
            return self._execute_sequential_commands_direct(commands, timeout, command_delay)
    
    def _execute_command_direct(self, command: str, timeout: int = 30) -> CommandResult:
        """Execute command using direct SSH."""
        ssh_cmd = self._build_ssh_command(command)
        
        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Clean the output before returning
            cleaned_stdout = self._clean_command_output(result.stdout)
            
            return CommandResult(
                returncode=result.returncode,
                stdout=cleaned_stdout,
                stderr=result.stderr,
                success=result.returncode == 0
            )
            
        except subprocess.TimeoutExpired:
            raise SSHTimeoutError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise SSHCommandError(f"Command execution failed: {e}")
    
    def _execute_command_with_expect(self, command: str, timeout: int = 30) -> CommandResult:
        """Execute command using expect for password authentication."""
        if not shutil.which('expect'):
            raise SSHError("expect command not found. Please install expect")
            
        # Create temporary script for ProxyCommand if needed
        proxy_script_path = None
        if self.jump_host:
            # Create proxy script inline like JumpHostClient does
            proxy_script_content = f'''#!/bin/bash
ssh -o StrictHostKeyChecking=no \\
    -o UserKnownHostsFile=/dev/null \\
    -o LogLevel=ERROR \\
    -o ControlPath={self.jump_host.control_socket} \\
    -o ControlMaster=auto \\
    -o ControlPersist=600 \\
    {f'-o IdentityFile={self.jump_host.private_key_path}' if self.jump_host.private_key_path and self.jump_host.private_key_path.exists() else ''} \\
    -W "$1:$2" {self.jump_host.username}@{self.jump_host.hostname}
'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(proxy_script_content)
                proxy_script_path = f.name
            os.chmod(proxy_script_path, 0o755)
        
        # Build SSH command parts to avoid quoting issues
        ssh_parts = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-o", "CheckHostIP=no",
            "-o", "GlobalKnownHostsFile=/dev/null",
            "-o", f"ControlPath={self.control_socket}",
            "-o", "ControlMaster=auto",
            "-o", "ControlPersist=600",
            "-p", str(self.port)
        ]
        
        if proxy_script_path:
            ssh_parts.extend(["-o", f"ProxyCommand={proxy_script_path} %h %p"])
            
        if self.use_password_auth:
            ssh_parts.extend([
                "-o", "PasswordAuthentication=yes",
                "-o", "PubkeyAuthentication=no",
                "-o", "PreferredAuthentications=password,keyboard-interactive"
            ])
        elif self.private_key_path and self.private_key_path.exists():
            ssh_parts.extend(["-o", f"IdentityFile={self.private_key_path}"])
            
        ssh_parts.extend([f"{self.username}@{self.hostname}", command])
        
        # Join with proper escaping for expect script
        ssh_command = " ".join(f'"{part}"' if " " in part or "(" in part or ")" in part else part for part in ssh_parts)
        
        # Determine which password/passphrase to use and escape it for expect
        auth_password = self.password if self.use_password_auth else self.key_passphrase
        escaped_password = auth_password if auth_password else ""
        for char, escape in [('\\', '\\\\'), ('"', '\\"'), ('$', '\\$'), ('[', '\\['), (']', '\\]'), ('{', '\\{'), ('}', '\\}')]:
            escaped_password = escaped_password.replace(char, escape)
        
        # Create expect script for command execution with pagination handling
        expect_script = f'''#!/usr/bin/expect -f
set timeout {timeout}
log_user 1

puts "DEBUG: Spawning SSH command..."
spawn {ssh_command}

expect {{
    "Are you sure you want to continue connecting" {{
        puts "DEBUG: Host key prompt detected"
        send "yes\\r"
        exp_continue
    }}
    "password:" {{
        puts "DEBUG: Password prompt detected (lowercase)"
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Password:" {{
        puts "DEBUG: Password prompt detected (uppercase)"
        send "{escaped_password}\\r"
        exp_continue
    }}
    "*password*:" {{
        puts "DEBUG: Generic password prompt detected"
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Enter passphrase for key*:" {{
        puts "DEBUG: SSH key passphrase prompt detected"
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Bad passphrase*" {{
        puts "DEBUG: Bad passphrase - retrying"
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Permission denied" {{
        puts "DEBUG: Permission denied"
        exit 1
    }}
    "Connection refused" {{
        puts "DEBUG: Connection refused"
        exit 1
    }}
    -re ".*--More--.*" {{
        puts "DEBUG: Pagination detected, sending space"
        send " "
        exp_continue
    }}
    -re "\\\\s*--More--\\\\s*" {{
        puts "DEBUG: Pagination prompt detected"
        send " "
        exp_continue
    }}
    -re "\\\\(Press.*to continue\\\\)" {{
        puts "DEBUG: Continue prompt detected"
        send " "
        exp_continue
    }}
    eof {{
        puts "DEBUG: Command completed (EOF)"
    }}
    timeout {{
        puts "DEBUG: Command timed out after {timeout} seconds"
        exit 1
    }}
}}

# Wait for process to finish and get exit code
catch wait result
set exit_code [lindex $result 3]
puts "DEBUG: Exit code: $exit_code"

{'file delete ' + proxy_script_path if proxy_script_path else ''}
exit $exit_code
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as f:
            f.write(expect_script)
            expect_file = f.name
        os.chmod(expect_file, 0o755)
        
        try:
            result = subprocess.run(
                ['expect', expect_file],
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            # Clean the output before returning
            cleaned_stdout = self._clean_command_output(result.stdout)
            
            return CommandResult(
                returncode=result.returncode,
                stdout=cleaned_stdout,
                stderr=result.stderr,
                success=result.returncode == 0
            )
            
        except subprocess.TimeoutExpired:
            raise SSHTimeoutError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise SSHCommandError(f"Command execution failed: {e}")
        finally:
            try:
                os.unlink(expect_file)
                if proxy_script_path:
                    os.unlink(proxy_script_path)
            except:
                pass
    
    def _execute_sequential_commands_direct(self, commands: list, timeout: int = 60, command_delay: float = 0.5) -> list:
        """Execute sequential commands using direct SSH with persistent session."""
        if not shutil.which('expect'):
            raise SSHError("expect command not found. Sequential commands require expect for session persistence")
        
        # Create expect script for persistent session
        ssh_cmd = self._build_ssh_command()
        ssh_command = " ".join(f'"{part}"' if " " in part else part for part in ssh_cmd)
        
        # Create expect script that maintains session
        expect_script = f'''#!/usr/bin/expect -f
set timeout {timeout}
log_user 0

spawn {ssh_command}

# Wait for initial prompt
expect {{
    -re "\\$ |# |> " {{
        # Connected successfully
    }}
    timeout {{
        puts "TIMEOUT: Failed to get initial prompt"
        exit 1
    }}
    eof {{
        puts "ERROR: Connection closed"
        exit 1
    }}
}}

# Execute commands sequentially
'''
        
        for i, cmd in enumerate(commands):
            escaped_cmd = cmd.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$')
            expect_script += f'''
puts "COMMAND_{i}_START"
send "{escaped_cmd}\\r"
expect {{
    -re ".*--More--.*" {{
        send " "
        exp_continue
    }}
    -re "\\\\s*--More--\\\\s*" {{
        send " "
        exp_continue
    }}
    -re "\\\\(Press.*to continue\\\\)" {{
        send " "
        exp_continue
    }}
    -re "\\$ |# |> " {{
        puts "COMMAND_{i}_END"
        if {{{i + 1} < {len(commands)}}} {{
            sleep {command_delay}
        }}
    }}
    timeout {{
        puts "TIMEOUT: Command {i} timed out"
        exit 1
    }}
    eof {{
        puts "ERROR: Connection closed during command {i}"
        exit 1
    }}
}}
'''
        
        expect_script += '''
exit 0
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as f:
            f.write(expect_script)
            expect_file = f.name
        os.chmod(expect_file, 0o755)
        
        try:
            result = subprocess.run(
                ['expect', expect_file],
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )
            
            # Parse output to extract individual command results
            return self._parse_sequential_output(result.stdout, commands, result.returncode)
            
        except subprocess.TimeoutExpired:
            raise SSHTimeoutError(f"Sequential commands timed out after {timeout} seconds")
        except Exception as e:
            raise SSHCommandError(f"Sequential command execution failed: {e}")
        finally:
            try:
                os.unlink(expect_file)
            except:
                pass
    
    def _execute_sequential_commands_with_expect(self, commands: list, timeout: int = 60, command_delay: float = 0.5) -> list:
        """Execute sequential commands using expect for password authentication."""
        if not shutil.which('expect'):
            raise SSHError("expect command not found. Please install expect")
        
        # Create temporary script for ProxyCommand if needed
        proxy_script_path = None
        if self.jump_host:
            proxy_script_content = f'''#!/bin/bash
ssh -o StrictHostKeyChecking=no \\
    -o UserKnownHostsFile=/dev/null \\
    -o LogLevel=ERROR \\
    -o ControlPath={self.jump_host.control_socket} \\
    -o ControlMaster=auto \\
    -o ControlPersist=600 \\
    {f'-o IdentityFile={self.jump_host.private_key_path}' if self.jump_host.private_key_path and self.jump_host.private_key_path.exists() else ''} \\
    -W "$1:$2" {self.jump_host.username}@{self.jump_host.hostname}
'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(proxy_script_content)
                proxy_script_path = f.name
            os.chmod(proxy_script_path, 0o755)
        
        # Build SSH command
        ssh_parts = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-o", "CheckHostIP=no",
            "-o", "GlobalKnownHostsFile=/dev/null",
            "-o", f"ControlPath={self.control_socket}",
            "-o", "ControlMaster=auto",
            "-o", "ControlPersist=600",
            "-p", str(self.port)
        ]
        
        if proxy_script_path:
            ssh_parts.extend(["-o", f"ProxyCommand={proxy_script_path} %h %p"])
            
        if self.use_password_auth:
            ssh_parts.extend([
                "-o", "PasswordAuthentication=yes",
                "-o", "PubkeyAuthentication=no",
                "-o", "PreferredAuthentications=password,keyboard-interactive"
            ])
        elif self.private_key_path and self.private_key_path.exists():
            ssh_parts.extend(["-o", f"IdentityFile={self.private_key_path}"])
            
        ssh_parts.append(f"{self.username}@{self.hostname}")
        ssh_command = " ".join(f'"{part}"' if " " in part else part for part in ssh_parts)
        
        # Determine which password/passphrase to use and escape it
        auth_password = self.password if self.use_password_auth else self.key_passphrase
        escaped_password = auth_password if auth_password else ""
        for char, escape in [('\\', '\\\\'), ('"', '\\"'), ('$', '\\$'), ('[', '\\['), (']', '\\]'), ('{', '\\{'), ('}', '\\}')]:
            escaped_password = escaped_password.replace(char, escape)
        
        # Create expect script
        expect_script = f'''#!/usr/bin/expect -f
set timeout {timeout}
log_user 1

spawn {ssh_command}

# Handle authentication
expect {{
    "Are you sure you want to continue connecting" {{
        send "yes\\r"
        exp_continue
    }}
    "password:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Password:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "*password*:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Enter passphrase for key*:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Bad passphrase*" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Permission denied" {{
        puts "ERROR: Authentication failed"
        exit 1
    }}
    -re "\\$ |# |> " {{
        # Connected successfully
    }}
    timeout {{
        puts "TIMEOUT: Failed to authenticate"
        exit 1
    }}
    eof {{
        puts "ERROR: Connection closed"
        exit 1
    }}
}}

# Execute commands sequentially
'''
        
        for i, cmd in enumerate(commands):
            escaped_cmd = cmd.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$')
            expect_script += f'''
puts "COMMAND_{i}_START"
send "{escaped_cmd}\\r"
expect {{
    -re ".*--More--.*" {{
        send " "
        exp_continue
    }}
    -re "\\\\s*--More--\\\\s*" {{
        send " "
        exp_continue
    }}
    -re "\\\\(Press.*to continue\\\\)" {{
        send " "
        exp_continue
    }}
    -re "(\\\\$ |# |> |\\\\) # )" {{
        puts "COMMAND_{i}_END"
        if {{{i + 1} < {len(commands)}}} {{
            sleep {command_delay}
        }}
    }}
    timeout {{
        puts "COMMAND_{i}_END"
        puts "TIMEOUT: Command {i} timed out"
    }}
    eof {{
        puts "COMMAND_{i}_END"
        puts "ERROR: Connection closed during command {i}"
        exit 1
    }}
}}
'''
        
        expect_script += f'''
exit 0
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as f:
            f.write(expect_script)
            expect_file = f.name
        os.chmod(expect_file, 0o755)
        
        try:
            result = subprocess.run(
                ['expect', expect_file],
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )
            

            
            # Parse output to extract individual command results
            return self._parse_sequential_output(result.stdout, commands, result.returncode)
            
        except subprocess.TimeoutExpired:
            raise SSHTimeoutError(f"Sequential commands timed out after {timeout} seconds")
        except Exception as e:
            raise SSHCommandError(f"Sequential command execution failed: {e}")
        finally:
            try:
                os.unlink(expect_file)
                if proxy_script_path:
                    os.unlink(proxy_script_path)
            except:
                pass
    
    def _parse_sequential_output(self, output: str, commands: list, overall_returncode: int) -> list:
        """Parse the output from sequential command execution into individual CommandResult objects."""
        results = []
        lines = output.split('\n')
        
        current_command_idx = None
        current_output = []
        
        for line in lines:
            if 'COMMAND_' in line and '_START' in line:
                # Extract command index
                try:
                    # Find the COMMAND_X_START pattern
                    marker = [part for part in line.split() if part.startswith('COMMAND_') and part.endswith('_START')][0]
                    current_command_idx = int(marker.split('_')[1])
                    current_output = []
                except (ValueError, IndexError):
                    continue
                    
            elif 'COMMAND_' in line and '_END' in line:
                # End of command output
                if current_command_idx is not None:
                    # Clean and create result
                    output_text = '\n'.join(current_output)
                    cleaned_output = self._clean_command_output(output_text)
                    
                    # For sequential commands, success is determined by overall success
                    # Individual commands are considered successful unless there's an obvious error
                    cmd_success = overall_returncode == 0 and not any(
                        error_indicator in cleaned_output.lower() 
                        for error_indicator in ['error:', 'failed:', 'permission denied', 'command not found']
                    )
                    
                    results.append(CommandResult(
                        returncode=0 if cmd_success else 1,
                        stdout=cleaned_output,
                        stderr="",
                        success=cmd_success
                    ))
                    current_command_idx = None
                    current_output = []
                    
            elif current_command_idx is not None:
                # Accumulate output for current command
                current_output.append(line)
        
        # Handle case where we have fewer results than commands (due to errors)
        while len(results) < len(commands):
            results.append(CommandResult(
                returncode=1,
                stdout="",
                stderr="Command execution failed or timed out",
                success=False
            ))
        
        return results
    
    def interact(self, escape_char: str = '~'):
        """Start an interactive SSH session."""
        print(f"Connecting to {self.hostname}...")
        if self.jump_host:
            print(f"Through jump host: {self.jump_host.hostname}")
        print(f"User: {self.username}")
        auth_type = "Password" if self.use_password_auth else ("Key with passphrase" if self.key_passphrase else "Key-based")
        print(f"Authentication: {auth_type}")
        print("-" * 50)
        
        # Save terminal state
        old_settings = None
        if os.isatty(0):
            old_settings = termios.tcgetattr(0)
            
        try:
            # Use expect for password auth, key with passphrase, or jump host connections
            if self.use_password_auth or self.key_passphrase or self.jump_host:
                return self._run_expect_interactive_session(old_settings)
            else:
                return self._run_direct_interactive_session(old_settings)
                
        finally:
            if old_settings and os.isatty(0):
                try:
                    termios.tcsetattr(0, termios.TCSADRAIN, old_settings)
                except:
                    pass
                # Always try stty sane as fallback
                try:
                    subprocess.run(['stty', 'sane'], check=False, timeout=5)
                except:
                    pass
    
    def _run_direct_interactive_session(self, old_settings):
        """Run direct interactive SSH session."""
        ssh_cmd = self._build_ssh_command()
        
        def cleanup_terminal():
            if old_settings and os.isatty(0):
                try:
                    termios.tcsetattr(0, termios.TCSADRAIN, old_settings)
                except:
                    pass
            try:
                subprocess.run(['stty', 'sane'], check=False, timeout=5)
            except:
                pass
                
        def signal_handler(signum, frame):
            cleanup_terminal()
            raise KeyboardInterrupt()
            
        # Set up signal handlers
        old_sigint = signal.signal(signal.SIGINT, signal_handler)
        old_sigterm = signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            process = subprocess.Popen(
                ssh_cmd,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            
            return_code = process.wait()
            return return_code == 0
            
        except KeyboardInterrupt:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            raise
            
        finally:
            signal.signal(signal.SIGINT, old_sigint)
            signal.signal(signal.SIGTERM, old_sigterm)
            cleanup_terminal()
    
    def _run_expect_interactive_session(self, old_settings):
        """Run interactive session using expect for password authentication."""
        if not shutil.which('expect'):
            raise SSHError("expect command not found. Please install expect")
            
        # Create expect script
        expect_script = self._create_interactive_expect_script()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as f:
            f.write(expect_script)
            expect_file = f.name
            
        try:
            os.chmod(expect_file, 0o755)
            
            def cleanup_terminal():
                if old_settings and os.isatty(0):
                    try:
                        termios.tcsetattr(0, termios.TCSADRAIN, old_settings)
                    except:
                        pass
                try:
                    subprocess.run(['stty', 'sane'], check=False, timeout=5)
                except:
                    pass
                    
            def signal_handler(signum, frame):
                cleanup_terminal()
                raise KeyboardInterrupt()
                
            # Set up signal handlers
            old_sigint = signal.signal(signal.SIGINT, signal_handler)
            old_sigterm = signal.signal(signal.SIGTERM, signal_handler)
            
            try:
                process = subprocess.Popen(
                    ['expect', expect_file],
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr
                )
                
                return_code = process.wait()
                return return_code == 0
                
            except KeyboardInterrupt:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                raise
                
            finally:
                signal.signal(signal.SIGINT, old_sigint)
                signal.signal(signal.SIGTERM, old_sigterm)
                cleanup_terminal()
                
        finally:
            try:
                os.unlink(expect_file)
            except:
                pass
    
    def _create_interactive_expect_script(self):
        """Create expect script for interactive session."""
        # Create temporary script for ProxyCommand if needed
        proxy_script_path = None
        
        if self.jump_host:
            # Create proxy script inline like JumpHostClient does
            proxy_script_content = f'''#!/bin/bash
ssh -o StrictHostKeyChecking=no \\
    -o UserKnownHostsFile=/dev/null \\
    -o LogLevel=ERROR \\
    -o ControlPath={self.jump_host.control_socket} \\
    -o ControlMaster=auto \\
    -o ControlPersist=600 \\
    {f'-o IdentityFile={self.jump_host.private_key_path}' if self.jump_host.private_key_path and self.jump_host.private_key_path.exists() else ''} \\
    -W "$1:$2" {self.jump_host.username}@{self.jump_host.hostname}
'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(proxy_script_content)
                proxy_script_path = f.name
            os.chmod(proxy_script_path, 0o755)
        
        # Build SSH command parts
        ssh_parts = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-o", "CheckHostIP=no",
            "-o", "GlobalKnownHostsFile=/dev/null",
            "-o", f"ControlPath={self.control_socket}",
            "-o", "ControlMaster=auto",
            "-o", "ControlPersist=600",
            "-p", str(self.port)
        ]
        
        if proxy_script_path:
            ssh_parts.extend(["-o", f"ProxyCommand={proxy_script_path} %h %p"])
            
        if self.use_password_auth:
            ssh_parts.extend([
                "-o", "PasswordAuthentication=yes",
                "-o", "PubkeyAuthentication=no",
                "-o", "PreferredAuthentications=password,keyboard-interactive"
            ])
        elif self.private_key_path and self.private_key_path.exists():
            ssh_parts.extend(["-o", f"IdentityFile={self.private_key_path}"])
            
        ssh_parts.append(f"{self.username}@{self.hostname}")
        
        # Join with proper escaping for expect script
        ssh_command = " ".join(f'"{part}"' if " " in part or "(" in part or ")" in part else part for part in ssh_parts)
        
        # Determine which password/passphrase to use and escape it for expect
        auth_password = self.password if self.use_password_auth else self.key_passphrase
        escaped_password = auth_password if auth_password else ""
        for char, escape in [('\\', '\\\\'), ('"', '\\"'), ('$', '\\$'), ('[', '\\['), (']', '\\]'), ('{', '\\{'), ('}', '\\}')]:
            escaped_password = escaped_password.replace(char, escape)
        
        cleanup_cmd = f"file delete {proxy_script_path}" if proxy_script_path else ""
        
        expect_script = f'''#!/usr/bin/expect -f
set timeout 30

# Enable terminal resizing support
trap {{
    set rows [stty rows]
    set cols [stty columns] 
    if {{[info exists spawn_out(slave,name)]}} {{
        stty rows $rows columns $cols < $spawn_out(slave,name)
    }}
}} WINCH

# Spawn the SSH command
spawn {ssh_command}

expect {{
    # Host key verification prompts
    "Are you sure you want to continue connecting (yes/no" {{
        send "yes\\r"
        exp_continue
    }}
    "Are you sure you want to continue connecting (yes/no/\\[fingerprint\\])" {{
        send "yes\\r" 
        exp_continue
    }}
    # Password prompts
    "password:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Password:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "*password*:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    # SSH key passphrase prompts
    "Enter passphrase for key*:" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    "Bad passphrase*" {{
        send "{escaped_password}\\r"
        exp_continue
    }}
    # Pagination handling during interactive session
    -re ".*--More--.*" {{
        send " "
        exp_continue
    }}
    -re "\\(Press.*to continue\\)" {{
        send " "
        exp_continue
    }}
    # Success - we got a shell prompt
    -re "\\$ |# |> " {{
        interact
        exit 0
    }}
    # Connection failures
    "Permission denied" {{
        send_user "\\nAuthentication failed\\n"
        exit 1
    }}
    "Connection refused" {{
        send_user "\\nConnection refused\\n"
        exit 1
    }}
    "No route to host" {{
        send_user "\\nNo route to host\\n"
        exit 1
    }}
    timeout {{
        send_user "\\nConnection timeout\\n"
        exit 1
    }}
    eof {{
        send_user "\\nConnection closed\\n"
        exit 0
    }}
}}

# Cleanup
{cleanup_cmd}
exit 0
'''
        return expect_script
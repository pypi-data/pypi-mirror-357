"""Utility functions for SSH operations."""

from pathlib import Path

def cleanup_ssh_sockets():
    """Clean up all SSH control sockets."""
    import subprocess
    import time
    
    print("Cleaning up SSH control sockets...")
    
    # Kill any existing SSH control masters
    try:
        subprocess.run(['pkill', '-f', 'ssh.*ControlMaster'], check=False, capture_output=True)
        time.sleep(1)
    except:
        pass
    
    # Remove socket files
    sockets_dir = Path.home() / '.ssh' / 'sockets'
    if sockets_dir.exists():
        for socket_file in sockets_dir.glob('*'):
            try:
                socket_file.unlink()
                print(f"  Removed: {socket_file.name}")
            except:
                pass
                
    print("SSH socket cleanup completed")

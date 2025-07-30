import os
import subprocess
import platform
from pathlib import Path
from .utils import run_command, print_info, print_warning, print_success

class SSHAgent:
    """Handle SSH agent operations across platforms"""
    
    def __init__(self):
        self.system = platform.system()
        self._setup_environment()
    
    def _setup_environment(self):
        """Setup SSH agent environment variables"""
        if self.system == "Linux":
            # Check for existing SSH agent
            ssh_auth_sock = os.environ.get('SSH_AUTH_SOCK')
            if not ssh_auth_sock:
                # Try to find it from common locations
                sock_locations = [
                    f"/run/user/{os.getuid()}/keyring/ssh",
                    f"/tmp/ssh-*/agent.*",
                ]
                for loc in sock_locations:
                    from glob import glob
                    matches = glob(loc)
                    if matches:
                        os.environ['SSH_AUTH_SOCK'] = matches[0]
                        break
    
    def is_running(self):
        """Check if SSH agent is running"""
        result = run_command(['ssh-add', '-l'], check=False)
        return result and result.returncode in [0, 1]
    
    def start(self):
        """Start SSH agent if not running"""
        if self.is_running():
            return True
        
        print_info("Starting SSH agent...")
        
        if self.system == "Windows":
            # Windows: Start ssh-agent service
            run_command(['powershell', '-Command', 'Start-Service', 'ssh-agent'], check=False)
            result = run_command(['ssh-agent'], check=False)
            if result and result.returncode == 0:
                self._parse_agent_output(result.stdout)
                return self.is_running()
        else:
            # Linux/macOS
            result = run_command(['ssh-agent', '-s'], check=False)
            if result and result.returncode == 0:
                self._parse_agent_output(result.stdout)
                return self.is_running()
        
        print_warning("Could not start SSH agent")
        return False
    
    def _parse_agent_output(self, output):
        """Parse ssh-agent output and set environment variables"""
        for line in output.splitlines():
            if 'SSH_AUTH_SOCK=' in line:
                sock = line.split('=')[1].split(';')[0]
                os.environ['SSH_AUTH_SOCK'] = sock
            elif 'SSH_AGENT_PID=' in line:
                pid = line.split('=')[1].split(';')[0]
                os.environ['SSH_AGENT_PID'] = pid
    
    def add_key(self, key_path, lifetime=3600):
        """Add SSH key to agent with specified lifetime"""
        key_path = Path(key_path).expanduser()
        
        if not key_path.exists():
            print_warning(f"SSH key not found: {key_path}")
            return False
        
        if self.is_key_loaded(key_path):
            print_success("SSH key already loaded in agent")
            return True
        
        print_info(f"Adding SSH key to agent: {key_path}")
        
        # Add key with lifetime to prevent asking for password repeatedly
        cmd = ['ssh-add']
        if self.system != "Windows":
            cmd.extend(['-t', str(lifetime)])
        cmd.append(str(key_path))
        
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print_success("SSH key added successfully")
            return True
        else:
            print_warning("Failed to add SSH key to agent")
            return False
    
    def is_key_loaded(self, key_path):
        """Check if a key is already loaded in the agent"""
        key_path = Path(key_path).expanduser()
        
        # Get key fingerprint
        result = run_command(['ssh-keygen', '-lf', str(key_path)], check=False)
        if not result or result.returncode != 0:
            # Try with .pub extension
            pub_path = key_path.with_suffix(key_path.suffix + '.pub')
            if pub_path.exists():
                result = run_command(['ssh-keygen', '-lf', str(pub_path)], check=False)
        
        if result and result.returncode == 0:
            fingerprint = result.stdout.split()[1]
            
            # Check loaded keys
            loaded = run_command(['ssh-add', '-l'], check=False)
            if loaded and loaded.returncode == 0:
                return fingerprint in loaded.stdout
        
        return False
    
    def list_keys(self):
        """List all loaded keys"""
        result = run_command(['ssh-add', '-l'], check=False)
        if result and result.returncode == 0:
            return result.stdout
        return "No keys loaded"
    
    def remove_all_keys(self):
        """Remove all keys from agent"""
        result = run_command(['ssh-add', '-D'], check=False)
        return result and result.returncode == 0
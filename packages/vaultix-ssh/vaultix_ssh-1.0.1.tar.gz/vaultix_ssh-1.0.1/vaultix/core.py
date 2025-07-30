import os
import json
import base64
from pathlib import Path
from typing import Dict, Optional, List, Any

class Connection:
    """Represents an SSH connection"""
    
    def __init__(self, name: str, host: str, user: str = None, port: int = 22,
                 key: str = None, password: str = None, options: List[str] = None,
                 description: str = ""):
        self.name = name
        self.host = host
        self.user = user or os.getenv("USER", "root")
        self.port = port
        self.key = key
        self.password = password
        self.options = options or []
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert connection to dictionary format"""
        return {
            "connection": {
                "host": self.host,
                "user": self.user,
                "port": self.port,
                "key": self.key,
                "password": self.password,
                "options": self.options
            },
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'Connection':
        """Create connection from dictionary"""
        conn = data.get('connection', {})
        return cls(
            name=name,
            host=conn.get('host'),
            user=conn.get('user'),
            port=conn.get('port', 22),
            key=conn.get('key'),
            password=conn.get('password'),
            options=conn.get('options', []),
            description=data.get('description', '')
        )
    
    def get_ssh_command(self, extra_args: List[str] = None) -> List[str]:
        """Build SSH command for this connection"""
        cmd = ['ssh']
        
        if self.key:
            cmd.extend(['-i', self.key])
        
        if self.options:
            cmd.extend(self.options)
        
        cmd.extend(['-p', str(self.port)])
        
        if extra_args:
            cmd.extend(extra_args)
        
        cmd.append(f"{self.user}@{self.host}")
        
        return cmd
    
    def get_scp_command(self, source: str, dest: str, download: bool = False,
                       recursive: bool = False) -> List[str]:
        """Build SCP command for this connection"""
        cmd = ['scp']
        
        if recursive:
            cmd.append('-r')
        
        if self.key:
            cmd.extend(['-i', self.key])
        
        cmd.extend(['-P', str(self.port)])
        
        if download:
            # Download: remote -> local
            remote_path = f"{self.user}@{self.host}:{source}"
            cmd.extend([remote_path, dest])
        else:
            # Upload: local -> remote
            remote_path = f"{self.user}@{self.host}:{dest}"
            cmd.extend([source, remote_path])
        
        return cmd
    
    def validate(self) -> List[str]:
        """Validate connection settings, return list of issues"""
        issues = []
        
        if not self.host:
            issues.append("Host is required")
        
        if self.port < 1 or self.port > 65535:
            issues.append("Port must be between 1 and 65535")
        
        if self.key:
            key_path = Path(self.key).expanduser()
            if not key_path.exists():
                issues.append(f"SSH key not found: {self.key}")
            elif not key_path.is_file():
                issues.append(f"SSH key is not a file: {self.key}")
        
        return issues


class ConnectionManager:
    """Manages SSH connections"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def get_all(self) -> Dict[str, Connection]:
        """Get all connections"""
        config = self.config_manager.load_config()
        connections = {}
        
        for name, data in config.items():
            connections[name] = Connection.from_dict(name, data)
        
        return connections
    
    def get(self, name: str) -> Optional[Connection]:
        """Get a specific connection"""
        config = self.config_manager.load_config()
        
        # Case-insensitive search
        for conn_name, data in config.items():
            if conn_name.lower() == name.lower():
                return Connection.from_dict(conn_name, data)
        
        return None
    
    def add(self, connection: Connection) -> None:
        """Add a new connection"""
        config = self.config_manager.load_config()
        
        # Check if already exists
        if self.get(connection.name):
            raise ValueError(f"Connection '{connection.name}' already exists")
        
        config[connection.name] = connection.to_dict()
        self.config_manager.save_config(config)
    
    def update(self, connection: Connection) -> None:
        """Update an existing connection"""
        config = self.config_manager.load_config()
        
        # Find existing connection (case-insensitive)
        existing_name = None
        for name in config:
            if name.lower() == connection.name.lower():
                existing_name = name
                break
        
        if not existing_name:
            raise ValueError(f"Connection '{connection.name}' not found")
        
        config[existing_name] = connection.to_dict()
        self.config_manager.save_config(config)
    
    def delete(self, name: str) -> None:
        """Delete a connection"""
        config = self.config_manager.load_config()
        
        # Find connection (case-insensitive)
        conn_name = None
        for existing_name in config:
            if existing_name.lower() == name.lower():
                conn_name = existing_name
                break
        
        if not conn_name:
            raise ValueError(f"Connection '{name}' not found")
        
        del config[conn_name]
        self.config_manager.save_config(config)
    
    def rename(self, old_name: str, new_name: str) -> None:
        """Rename a connection"""
        config = self.config_manager.load_config()
        
        # Check if new name already exists
        for name in config:
            if name.lower() == new_name.lower():
                raise ValueError(f"Connection '{new_name}' already exists")
        
        # Find old connection
        old_conn_name = None
        for name in config:
            if name.lower() == old_name.lower():
                old_conn_name = name
                break
        
        if not old_conn_name:
            raise ValueError(f"Connection '{old_name}' not found")
        
        # Rename
        config[new_name] = config[old_conn_name]
        del config[old_conn_name]
        self.config_manager.save_config(config)
    
    def search(self, query: str) -> Dict[str, Connection]:
        """Search connections by name, host, user, or description"""
        query = query.lower()
        connections = self.get_all()
        matches = {}
        
        for name, conn in connections.items():
            if (query in name.lower() or
                query in conn.host.lower() or
                query in conn.user.lower() or
                query in conn.description.lower()):
                matches[name] = conn
        
        return matches
    
    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all connections, return dict of issues per connection"""
        connections = self.get_all()
        all_issues = {}
        
        for name, conn in connections.items():
            issues = conn.validate()
            if issues:
                all_issues[name] = issues
        
        return all_issues

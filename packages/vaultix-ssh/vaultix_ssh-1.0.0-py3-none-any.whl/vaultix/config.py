import json
import base64
import os
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from .constants import CONFIG_DIR, CONFIG_FILE, ENCRYPTION_KEY_FILE
from .utils import print_error, print_success

class ConfigManager:
    """Manage vaultix configuration with optional encryption"""
    
    def __init__(self, use_encryption=True):
        self.use_encryption = use_encryption
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self._ensure_config_dir()
        self._init_encryption()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set proper permissions on Unix systems
        if hasattr(os, 'chmod'):
            import stat
            os.chmod(self.config_dir, stat.S_IRWXU)  # 700 permissions
    
    def _init_encryption(self):
        """Initialize encryption key"""
        if not self.use_encryption:
            return
        
        if not ENCRYPTION_KEY_FILE.exists():
            # Generate new encryption key
            salt = get_random_bytes(32)
            password = get_random_bytes(32)
            key = PBKDF2(password, salt, 32)
            
            key_data = {
                'salt': base64.b64encode(salt).decode(),
                'password': base64.b64encode(password).decode()
            }
            
            ENCRYPTION_KEY_FILE.write_text(json.dumps(key_data))
            
            # Set restrictive permissions
            if hasattr(os, 'chmod'):
                import stat
                os.chmod(ENCRYPTION_KEY_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 600
    
    def _get_cipher(self):
        """Get AES cipher for encryption/decryption"""
        key_data = json.loads(ENCRYPTION_KEY_FILE.read_text())
        salt = base64.b64decode(key_data['salt'])
        password = base64.b64decode(key_data['password'])
        key = PBKDF2(password, salt, 32)
        return AES.new(key, AES.MODE_EAX)
    
    def save_config(self, data):
        """Save configuration with optional encryption"""
        json_data = json.dumps(data, indent=2)
        
        if self.use_encryption:
            cipher = self._get_cipher()
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(json_data.encode())
            
            encrypted_data = {
                'nonce': base64.b64encode(nonce).decode(),
                'ciphertext': base64.b64encode(ciphertext).decode(),
                'tag': base64.b64encode(tag).decode()
            }
            
            self.config_file.write_text(json.dumps(encrypted_data))
        else:
            self.config_file.write_text(json_data)
    
    def load_config(self):
        """Load configuration with optional decryption"""
        if not self.config_file.exists():
            return {}
        
        raw_data = self.config_file.read_text()
        
        if self.use_encryption:
            encrypted_data = json.loads(raw_data)
            
            key_data = json.loads(ENCRYPTION_KEY_FILE.read_text())
            salt = base64.b64decode(key_data['salt'])
            password = base64.b64decode(key_data['password'])
            key = PBKDF2(password, salt, 32)
            
            nonce = base64.b64decode(encrypted_data['nonce'])
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            tag = base64.b64decode(encrypted_data['tag'])
            
            cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            
            return json.loads(data.decode())
        else:
            return json.loads(raw_data)
from vaultix.core import Connection, ConnectionManager
from vaultix.config import ConfigManager
from unittest.mock import MagicMock
import pytest

def dummy_connection():
    return Connection("test", host="localhost", user="root", port=22)

def test_connection_to_dict_from_dict():
    conn = dummy_connection()
    d = conn.to_dict()
    loaded = Connection.from_dict("test", d)
    assert loaded.host == conn.host
    assert loaded.user == conn.user

def test_connection_validate_missing_key(tmp_path):
    conn = Connection("bad", host="localhost", user="u", port=22, key="/invalid/path")
    issues = conn.validate()
    assert any("not found" in i for i in issues)

def test_get_ssh_command():
    conn = dummy_connection()
    cmd = conn.get_ssh_command()
    assert "ssh" in cmd[0]

def test_get_scp_command():
    conn = dummy_connection()
    scp_cmd = conn.get_scp_command("a", "b", download=False)
    assert scp_cmd[0] == "scp"

def test_connection_manager_add_get():
    cm = ConnectionManager(ConfigManager(use_encryption=False))
    cm.config_manager.save_config = MagicMock()
    cm.config_manager.load_config = MagicMock(return_value={})
    conn = dummy_connection()
    cm.add(conn)
    cm.config_manager.save_config.assert_called()

def test_connection_manager_delete():
    cm = ConnectionManager(ConfigManager(use_encryption=False))
    cm.config_manager.load_config = MagicMock(return_value={"test": dummy_connection().to_dict()})
    cm.config_manager.save_config = MagicMock()
    cm.delete("test")
    cm.config_manager.save_config.assert_called()
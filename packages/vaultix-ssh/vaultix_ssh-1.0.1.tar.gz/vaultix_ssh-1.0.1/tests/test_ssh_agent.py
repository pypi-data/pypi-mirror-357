from vaultix.ssh_agent import SSHAgent
from unittest.mock import patch, MagicMock

def test_is_running():
    agent = SSHAgent()
    with patch("vaultix.utils.run_command") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert agent.is_running() is True

def test_start_agent():
    agent = SSHAgent()
    with patch("vaultix.utils.run_command") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="SSH_AUTH_SOCK=/tmp/test.sock;\nSSH_AGENT_PID=1234;\n")
        assert agent.start() is True

def test_add_key_exists():
    agent = SSHAgent()
    with patch("vaultix.utils.run_command") as mock_run, patch("pathlib.Path.exists", return_value=True), patch.object(agent, "is_key_loaded", return_value=False):
        mock_run.return_value = MagicMock(returncode=0)
        assert agent.add_key("~/.ssh/id_rsa") is True

def test_remove_all_keys():
    agent = SSHAgent()
    with patch("vaultix.utils.run_command") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert agent.remove_all_keys() is True
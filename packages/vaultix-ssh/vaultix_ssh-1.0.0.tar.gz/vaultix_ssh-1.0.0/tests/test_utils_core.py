from vaultix.utils import prompt_with_default
from vaultix.core import Connection
from unittest.mock import patch

@patch("rich.prompt.Prompt.ask", return_value="default")
def test_prompt_with_default(mock_ask):
    result = prompt_with_default("Username", "default")
    assert result == "default"
    mock_ask.assert_called_once()

def test_connection_to_dict_and_back():
    conn = Connection("test", "127.0.0.1")
    d = conn.to_dict()
    conn2 = Connection.from_dict("test", d)
    assert conn2.host == "127.0.0.1"
    assert conn2.user == conn.user
from vaultix.utils import run_command, print_error, print_success, print_info, print_warning
import subprocess
from io import StringIO
from rich.console import Console
from unittest.mock import patch


@patch("subprocess.run")
def test_run_command_success(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=["echo"], returncode=0, stdout="ok\n")
    result = run_command(["echo", "ok"])
    assert result.stdout == "ok\n"

@patch("vaultix.utils.console", new_callable=lambda: Console(file=StringIO(), force_terminal=False))
def test_print_functions(mock_console):
    print_success("done")
    print_info("info")
    print_warning("warn")
    print_error("fail")

    output = mock_console.file.getvalue()
    assert "done" in output
    assert "info" in output
    assert "warn" in output
    assert "fail" in output
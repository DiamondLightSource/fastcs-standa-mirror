import subprocess
import sys

from fastcs_standa_mirror import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "fastcs_standa_mirror", "--version"]
    output = subprocess.check_output(cmd).decode()
    assert __version__ in output

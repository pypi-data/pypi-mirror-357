import subprocess

__version__ = "0.9.3"


def format_toml(unformatted: str, _info_str: str) -> str:
    # Note:
    # Taplo might not be in the PATH depending on the installation method, it should be in most cases,
    # so we'll worry about the edge cases if and when they happen.
    return subprocess.check_output(
        ["taplo", "format", "--colors", "never", "-"],
        input=unformatted.encode(),
        stderr=subprocess.DEVNULL,
    ).decode()

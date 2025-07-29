import subprocess

__version__ = "0.0.1"


def format_yaml(unformatted: str, _info_str: str) -> str:
    return subprocess.check_output(
        ["yamlfmt", "-"],
        input=unformatted.encode(),
        stderr=subprocess.DEVNULL,
    ).decode()

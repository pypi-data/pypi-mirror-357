import json
import subprocess
from pathlib import Path

from hausify.util.search import _find_closest_parent


def lsp_exec_flake8(
    flake8_cmd: Path,
    root: Path,
    filename: Path,
    contents: str,
) -> list[dict]:

    cmd = [
        str(flake8_cmd),
        "--format",
        "json",
    ]
    config = _find_config(root, filename)

    if config != root:
        cmd.extend(["--config", str(config)])

    cmd.append("-")

    try:
        subprocess.run(
            cmd,
            input=contents,
            capture_output=True,
            text=True,
            check=True,
        )
        return []
    except subprocess.CalledProcessError as e:
        if e.stdout is None:
            return []
        return_obj = json.loads(e.stdout)
        return return_obj["stdin"]


def _find_config(root: Path, filename: Path) -> Path:
    for c in [".flake8", "setup.cfg", "tox.ini"]:
        possible = _find_closest_parent(
            file=filename,
            config=c,
            root=root,
        )
        if possible != root:
            return possible
    return root

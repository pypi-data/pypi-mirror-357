import json
import logging
import subprocess
from pathlib import Path

from hausify.util.search import _find_closest_parent


def lsp_exec_mypy(
    mypy_cmd: Path,
    root: Path,
    filename: Path,
) -> list[dict]:
    cmd = [
        str(mypy_cmd),
        "--output",
        "json",
    ]
    config = _find_config(root, filename)

    if config != root:
        cmd.append("--config-file")
        cmd.append(str(config))

    cmd.append(str(filename))

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return []
    except subprocess.CalledProcessError as e:
        if e.stdout is None or e.stdout == "":
            return []

        results = []
        logging.info(f"{e.stdout}")
        for _ in e.stdout.split("\n"):
            if _ == "":
                continue
            results.append(json.loads(_))

        return results


def _find_config(root: Path, filename: Path) -> Path:
    for c in ["mypy.ini", ".mypy.ini", "pyproject.toml", "setup.cfg"]:
        possible = _find_closest_parent(
            file=filename,
            config=c,
            root=root,
        )
        if possible != root:
            return possible
    return root

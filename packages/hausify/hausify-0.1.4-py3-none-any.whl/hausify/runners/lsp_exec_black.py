import subprocess
from pathlib import Path

from hausify.util.python_import_finder import PythonImportFinder
from hausify.util.search import _find_closest_parent


def lsp_exec_black(
    black_cmd: Path,
    root: Path,
    filename: Path,
    contents: str,
) -> str:
    cmd = [
        str(black_cmd),
    ]

    config = _find_config(root, filename)

    if config != root:
        cmd.extend(["--config", str(config)])

    finder = PythonImportFinder()
    finder.load_source_string(contents)
    for start, end in finder.get_formatting_ranges():
        cmd.extend(["--line-ranges", f"{start}-{end}"])

    cmd.append("-")

    try:
        result = subprocess.run(
            cmd,
            input=contents,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout


def _find_config(root: Path, filename: Path) -> Path:
    for c in ["pyproject.toml"]:
        possible = _find_closest_parent(
            file=filename,
            config=c,
            root=root,
        )
        if possible != root:
            return possible
    return root

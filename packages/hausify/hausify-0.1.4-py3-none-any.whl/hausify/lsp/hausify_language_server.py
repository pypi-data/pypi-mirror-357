import sys
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Optional

from pygls.server import LanguageServer


class HausifyLanguageServer(LanguageServer):
    def __init__(self, *args: Any) -> None:
        self._hausify_rootdir: str = ""
        self._hausify_flake8_cmd: str = ""
        self._hausify_mypy_cmd: str = ""
        self._hausify_isort_cmd: str = ""
        self._hausify_docformatter_cmd: str = ""
        self._hausify_black_cmd: str = ""
        super().__init__(*args)
        self._hausify_find_tools()

    @property
    def hausify_root(self) -> str:
        return self._hausify_rootdir

    def set_hausify_root(self, root: str) -> None:
        self._hausify_rootdir = root

    @property
    def hausify_flake8(self) -> str:
        return self._hausify_flake8_cmd

    @property
    def hausify_mypy(self) -> str:
        return self._hausify_mypy_cmd

    @property
    def hausify_isort(self) -> str:
        return self._hausify_isort_cmd

    @property
    def hausify_docformatter(self) -> str:
        return self._hausify_docformatter_cmd

    @property
    def hausify_black(self) -> str:
        return self._hausify_black_cmd

    def set_handler(
        self,
        feature_name: str,
        handler: Callable,
        options: Optional[Any] = None,
    ) -> None:
        wrapper = self.feature(feature_name=feature_name, options=options)
        wrapper(handler)

    def _hausify_find_tools(self) -> None:
        python = Path(sys.executable)
        venv = python.parent

        flake8 = venv / "flake8"
        self._hausify_flake8_cmd = str(flake8)

        mypy = venv / "mypy"
        self._hausify_mypy_cmd = str(mypy)

        isort = venv / "isort"
        self._hausify_isort_cmd = str(isort)

        docformatter = venv / "docformatter"
        self._hausify_docformatter_cmd = str(docformatter)

        black = venv / "black"
        self._hausify_black_cmd = str(black)

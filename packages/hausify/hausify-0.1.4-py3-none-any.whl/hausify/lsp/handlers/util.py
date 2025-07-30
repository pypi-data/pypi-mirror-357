import logging
import re

from hausify.util.filesystem import _default_exclude_dirs

_all_skip_patterns = [re.compile(_) for _ in _default_exclude_dirs]


def skip_file(path: str) -> bool:
    for _ in _all_skip_patterns:
        if _.match(path):
            logging.info(f"skipping: {path}")
            return True
    return False

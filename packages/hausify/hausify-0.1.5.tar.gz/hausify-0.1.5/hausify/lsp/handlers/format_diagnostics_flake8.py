from pathlib import Path

from lsprotocol import types

from hausify.lsp.hausify_language_server import HausifyLanguageServer
from hausify.runners.lsp_exec_flake8 import lsp_exec_flake8


def format_diagnostics_flake8(
    h: HausifyLanguageServer,
    params_uri: str,
    params_contents: str,
) -> list[types.Diagnostic]:
    flake8 = Path(h.hausify_flake8)
    root = Path(h.hausify_root)
    filename = Path(params_uri.replace("file://", ""))

    result_obj = lsp_exec_flake8(
        flake8_cmd=flake8,
        root=root,
        filename=filename,
        contents=params_contents,
    )
    if len(result_obj) == 0:
        return []

    items: list[types.Diagnostic] = []
    for row in result_obj:
        diag = types.Diagnostic(
            range=types.Range(
                start=types.Position(
                    line=row["line_number"] - 1,
                    character=row["column_number"] - 1,
                ),
                end=types.Position(
                    line=row["line_number"] - 1,
                    character=row["column_number"] - 1,
                ),
            ),
            message=row["text"],
            severity=types.DiagnosticSeverity.Error,
            code=row["code"],
            source="hausify-flake8",
        )
        items.append(diag)

    return items

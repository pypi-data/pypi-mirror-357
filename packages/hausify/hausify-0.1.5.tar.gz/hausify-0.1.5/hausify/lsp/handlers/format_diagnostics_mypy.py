from pathlib import Path

from lsprotocol import types

from hausify.lsp.hausify_language_server import HausifyLanguageServer
from hausify.runners.lsp_exec_mypy import lsp_exec_mypy


def format_diagnostics_mypy(
    h: HausifyLanguageServer,
    params_uri: str,
) -> list[types.Diagnostic]:
    mypy = Path(h.hausify_mypy)
    root = Path(h.hausify_root)
    filename = Path(params_uri.replace("file://", ""))

    result_obj = lsp_exec_mypy(
        mypy_cmd=mypy,
        root=root,
        filename=filename,
    )

    if len(result_obj) == 0:
        return []

    items: list[types.Diagnostic] = []
    for row in result_obj:
        if not str(filename).endswith(row["file"]):
            continue
        diag = types.Diagnostic(
            range=types.Range(
                start=types.Position(
                    line=max(row["line"] - 1, 0),
                    character=max(row["column"] - 1, 0),
                ),
                end=types.Position(
                    line=max(row["line"] - 1, 0),
                    character=max(row["column"] - 1, 0),
                ),
            ),
            message=row["message"],
            severity=types.DiagnosticSeverity.Error,
            code=row["code"],
            source="hausify-mypy",
        )
        items.append(diag)
    return items

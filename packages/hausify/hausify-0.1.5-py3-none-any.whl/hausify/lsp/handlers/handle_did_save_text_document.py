from lsprotocol import types

from hausify.lsp.handlers.format_diagnostics_flake8 import format_diagnostics_flake8  # NOQA
from hausify.lsp.handlers.format_diagnostics_mypy import format_diagnostics_mypy  # NOQA
from hausify.lsp.handlers.util import skip_file
from hausify.lsp.hausify_language_server import HausifyLanguageServer


def handle_did_save_text_document(
    h: HausifyLanguageServer,
    params: types.DidSaveTextDocumentParams,
) -> None:
    if skip_file(params.text_document.uri.replace("file://", "")):
        return

    items: list[types.Diagnostic] = []
    items.extend(
        format_diagnostics_flake8(
            h,
            params.text_document.uri,
            params.text if params.text else "",
        )
    )
    items.extend(
        format_diagnostics_mypy(
            h,
            params.text_document.uri,
        )
    )

    h.publish_diagnostics(params.text_document.uri, items)

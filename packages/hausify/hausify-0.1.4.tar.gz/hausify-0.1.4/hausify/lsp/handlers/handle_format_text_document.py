import logging
from pathlib import Path

from lsprotocol import types

from hausify.lsp.handlers.util import skip_file
from hausify.lsp.hausify_language_server import HausifyLanguageServer
from hausify.runners.lsp_exec_black import lsp_exec_black
from hausify.runners.lsp_exec_docformatter import lsp_exec_docformatter
from hausify.runners.lsp_exec_isort import lsp_exec_isort


def handle_format_text_document(
    h: HausifyLanguageServer, params: types.DocumentFormattingParams
) -> list[types.TextEdit]:
    if skip_file(params.text_document.uri.replace("file://", "")):
        return []

    doc = h.workspace.get_text_document(params.text_document.uri)

    whole_doc_end = types.Position(
        line=len(doc.lines),
        character=0,
    )

    formatted = lsp_exec_isort(
        Path(h.hausify_isort),
        Path(h.hausify_root),
        Path(params.text_document.uri.replace("file://", "")),
        doc.source,
    )

    new_src = formatted if formatted != "" else doc.source

    formatted = lsp_exec_docformatter(
        Path(h.hausify_docformatter),
        Path(h.hausify_root),
        Path(params.text_document.uri.replace("file://", "")),
        new_src,
    )

    new_src = formatted if formatted != "" else new_src

    formatted = lsp_exec_black(
        Path(h.hausify_black),
        Path(h.hausify_root),
        Path(params.text_document.uri.replace("file://", "")),
        new_src,
    )

    new_src = formatted if formatted != "" else new_src

    if new_src == doc.source:
        logging.info("it matches...")
        return []

    return [
        types.TextEdit(
            range=types.Range(
                start=types.Position(line=0, character=0),
                end=whole_doc_end,
            ),
            new_text=new_src,
        )
    ]

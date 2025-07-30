import argparse
import logging
from pathlib import Path

from lsprotocol import types

from hausify.lsp.handlers import handle_did_open_text_document
from hausify.lsp.handlers import handle_did_save_text_document
from hausify.lsp.handlers import handle_format_text_document
from hausify.lsp.hausify_language_server import HausifyLanguageServer


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser("Hausify LSP")
    argparser.add_argument(
        "--root",
        help="root dir for this execution",
        type=str,
    )

    argparser.add_argument(
        "--log-path",
        help="Path for output logs",
        default="",
        type=str,
    )

    args = argparser.parse_args()
    return args


def run_server() -> None:
    """Here is a docstring."""
    args = parse_args()

    if args.log_path != "":
        logging.basicConfig(
            filename=Path(args.log_path).resolve(),
            filemode="w",
            level=logging.DEBUG,
        )

    server = HausifyLanguageServer("hausify", "v0.1")
    server.set_hausify_root(args.root)

    server.set_handler(
        types.TEXT_DOCUMENT_DID_OPEN,
        handle_did_open_text_document,
    )

    server.set_handler(
        types.TEXT_DOCUMENT_DID_SAVE,
        handle_did_save_text_document,
        types.SaveOptions(
            include_text=True,
        ),
    )

    server.set_handler(
        types.TEXT_DOCUMENT_FORMATTING,
        handle_format_text_document,
    )

    server.start_io()


if __name__ == "__main__":
    run_server()

"""AIWB Cli entry point."""

import logging

from rich.logging import RichHandler

from aiwb.cli import cli_group
from aiwb.utils.console import console

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(console=console, show_path=False)],
    )
    cli_group()
    
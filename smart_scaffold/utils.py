import functools
import logging
import os
import shutil
import subprocess
from enum import StrEnum

import click
import pandas as pd

logger = logging.getLogger(__name__)


def get_github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN")

    if token:
        logger.info("GitHub token fetched from GITHUB_TOKEN")
        return token

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info("GitHub token fetched from CLI")

        return result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise click.ClickException(
            "No GitHub token found. Set GITHUB_TOKEN or authenticate with `gh auth login`."
        ) from exc


def _max_col_width(data: pd.DataFrame, padding: int = 3) -> int:
    cols = len(data.columns)
    if cols == 0:
        return 10

    terminal_width = shutil.get_terminal_size((80, 20)).columns
    per_col = max((terminal_width - cols * padding) // cols, 10)
    return per_col


class OutputFormat(StrEnum):
    COMPACT = "compact"
    WIDE = "wide"
    JSON = "json"


def format_dataframe(
    data: pd.DataFrame,
    output_format: OutputFormat,
    wide_only_columns: list[str] | None = None,
) -> str:
    if data.empty:
        return ""

    if output_format == OutputFormat.JSON:
        return data.to_json(orient="records", indent=2)

    if output_format == OutputFormat.WIDE:
        return data.to_markdown(tablefmt="github", index=False)

    if output_format == OutputFormat.COMPACT and wide_only_columns:
        data = data.drop(columns=wide_only_columns, errors="ignore")
        return data.to_markdown(tablefmt="github", index=False)

    return data.to_markdown(tablefmt="github", index=False)


def format_option(f):
    @click.option(
        "--output",
        "-o",
        type=click.Choice(OutputFormat, case_sensitive=False),
        default=OutputFormat.COMPACT,
    )
    @functools.wraps(f)
    def wrapper_format_option(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper_format_option

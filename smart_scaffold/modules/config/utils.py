import json
from pathlib import Path

import click

_CONFIG_PATH = Path(click.get_app_dir("smart_scaffold")) / "config.json"


def _read_config() -> dict:
    if _CONFIG_PATH.exists():
        return json.loads(_CONFIG_PATH.read_text())
    return {}


def _set_config(data: dict) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(json.dumps(data, indent=2))


def set_config(key: str, value: str):
    data = _read_config()
    data[key] = value

    _set_config(data)


def get_config(key: str) -> str:
    value = _read_config().get(key)

    if not value:
        raise click.ClickException(
            f"Config key '{key}' is not set. Run: smart-scaffold config set {key} <value>"
        )

    return value

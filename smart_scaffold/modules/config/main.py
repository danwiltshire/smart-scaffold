import click

from smart_scaffold.modules.config.utils import _read_config, get_config, set_config


@click.group()
def config():
    """Manage configuration."""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
def set(key: str, value: str):  # noqa: A001
    """Set a configuration value."""
    set_config(key, value)

    click.echo(f"Set configuration key {key}")


@config.command("get")
@click.argument("key", required=False)
def get(key: str | None):
    """Get a configuration value."""
    if not key:
        click.echo(_read_config())

    else:
        value = get_config(key)
        click.echo(value)

import logging

import click

from smart_scaffold.modules.config.main import config
from smart_scaffold.modules.recipes.main import recipe

logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    """smart-scaffold — Context-aware project scaffolding."""
    pass


cli.add_command(config)
cli.add_command(recipe)


if __name__ == "__main__":
    cli()

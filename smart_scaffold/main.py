import click


@click.group()
def cli():
    """smart-scaffold — Context-aware project scaffolding."""
    pass


@cli.command()
def get_recipes():
    """Gets all available recipes."""
    pass


cli.add_command(get_recipes)


if __name__ == "__main__":
    cli()

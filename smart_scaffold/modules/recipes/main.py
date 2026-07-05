import asyncio

import click

from smart_scaffold.agents import apply_recipe
from smart_scaffold.modules.config.utils import get_config
from smart_scaffold.modules.recipes.prompts import apply_recipe_prompt
from smart_scaffold.modules.recipes.utils import get_recipes
from smart_scaffold.tui import select_from_dataframe
from smart_scaffold.utils import (
    OutputFormat,
    format_dataframe,
    format_option,
    get_github_token,
    validate_repository_name,
)


@click.group()
def recipe():
    """Manage recipes."""
    pass


@recipe.command()
@click.option("--repository", "-r", callback=validate_repository_name, required=True)
def apply(repository: str):
    recipe_repository = get_config("recipe-repository")
    github_token = get_github_token()

    recipes = get_recipes(recipe_repository, github_token)

    selected = select_from_dataframe(
        recipes, label_column="name", group_by="type", title="Select a recipe"
    )

    if selected is None:
        click.echo("No recipe selected.")
        return

    click.echo(f"Selected recipe: {selected['name']}")

    asyncio.run(
        apply_recipe(
            prompt=f"Apply the recipe {selected['name']} found in directory {selected['directory']} to repository {repository}.",  # noqa
            system_message=apply_recipe_prompt(recipe_repository),
            token=github_token,
        )
    )


@recipe.command()
@format_option
def get(output: OutputFormat):
    """Gets all recipes."""
    recipe_repository = get_config("recipe-repository")
    github_token = get_github_token()

    recipes = get_recipes(recipe_repository, github_token)

    click.echo(
        format_dataframe(
            recipes, output_format=output, wide_only_columns=["description", "directory"]
        )
    )

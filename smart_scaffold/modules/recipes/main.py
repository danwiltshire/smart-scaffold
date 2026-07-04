import click

from smart_scaffold.modules.config.utils import get_config
from smart_scaffold.modules.recipes.utils import get_recipes
from smart_scaffold.utils import OutputFormat, format_dataframe, format_option, get_github_token


@click.group()
def recipe():
    """Manage recipes."""
    pass


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

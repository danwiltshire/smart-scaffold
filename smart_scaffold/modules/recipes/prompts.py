def apply_recipe_prompt(recipe_repository: str):
    return f"""
    Your job is to apply recipes to repositories.

    A recipe is one or more files containing the minimum amount of code required
    to fulfil the recipe purpose.

    Recipes are stored in the repository {recipe_repository} and
    each recipe directory contains a recipe.json with metadata about the recipe
    such as its name, type, description and tags.

    The type of recipe should be used to determine how to contextually apply the
    recipe to an existing repository.

    How to handle each type is defined below:

    github-actions: Read existing GitHub Actions workflows in the destination
    repository and implement the recipe files, merging content when able.
    If workflow files don't already exist that match the naming convention of
    files in the recipe, create them.  If they do exist, or they have similar
    names e.g. pull-request-checks.yml and pull-request.yml, assume they are
    the same thing.  If the recipe contains code which needs values filled in,
    try and guess the values based on the destination repository contents,
    otherwise prompt for input.

    You should commit the changes to a new branch and create a pull request.

    Don't perform any tests or summarise what you have done, just return the
    pull request URL.
    """

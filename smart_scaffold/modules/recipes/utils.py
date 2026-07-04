import json
import logging

import pandas as pd
from github import Github

logger = logging.getLogger(__name__)


def get_recipes(recipe_repository, github_token, branch: str = "main"):
    gh = Github(github_token)
    repo = gh.get_repo(recipe_repository)

    tree = repo.get_git_tree(branch, recursive=True).tree

    recipe_files = [
        item for item in tree if item.type == "blob" and item.path.endswith("recipe.json")
    ]

    logger.info("Found %d recipe files", len(recipe_files))

    rows: list[dict] = []

    for item in recipe_files:
        path = item.path
        directory = "/".join(path.split("/")[:-1])

        file = repo.get_contents(path)

        if isinstance(file, list):
            # Should never happen for recipe.json, but safe to check
            raise RuntimeError(f"Unexpected directory for recipe path: {path}")

        parsed = json.loads(file.decoded_content.decode("utf-8"))

        rows.append(
            {
                "directory": directory,
                "name": parsed["name"],
                "description": parsed["description"],
                "type": parsed["type"],
                "tags": parsed["tags"],
            }
        )

    return pd.DataFrame(rows)

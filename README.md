# smart-scaffold

CLI-driven, context-aware project scaffolding powered by the GitHub Copilot SDK.

Pick a recipe from a shared repository, point smart-scaffold at a destination repository, and it applies the recipe: reading existing conventions, merging content where it can, and opening a pull request, all from the terminal.

Disclaimer - this is a hobby project, and I wouldn't recommend managing project
templating using this approach. It might be more suitable when LLM usage becomes
cheaper.

![Demo](./docs/demo.gif)

## Installation

⚠️ This package is not published to Pypi.

Requires Python 3.14+. Authenticate with GitHub before first use:

```bash
gh auth login
```

## Quick start

Point smart-scaffold at your recipe repository, then apply a recipe to a destination repository:

```bash
smart-scaffold config set recipe-repository owner/recipes-repo

smart-scaffold recipe apply --repository owner/destination-repo
```

You'll be shown an interactive menu grouped by recipe type. Pick one with the arrow keys and press Enter, and smart-scaffold applies it to the destination repository and opens a pull request.

## Commands

### `smart-scaffold recipe apply --repository <owner/repo>`

Select a recipe from an interactive menu and apply it to the destination repository. smart-scaffold reads the destination repository's existing content, merges the recipe in contextually, commits to a new branch, and opens a pull request.

```bash
smart-scaffold recipe apply --repository owner/destination-repo
```

### `smart-scaffold recipe get [--output compact|wide|json]`

List all recipes available in the configured recipe repository.

```bash
smart-scaffold recipe get --output wide
```

### `smart-scaffold config set <key> <value>` / `smart-scaffold config get [<key>]`

Read and write smart-scaffold configuration. Config is stored in the app's config directory as `config.json`.

```bash
smart-scaffold config set recipe-repository owner/recipes-repo
smart-scaffold config get recipe-repository
```

#### Configuration keys

| Key                 | Description                                                                               |
| ------------------- | ----------------------------------------------------------------------------------------- |
| `recipe-repository` | GitHub repository (`owner/repo`) where recipes are stored. Required by `recipe` commands. |

## Recipe repository structure

smart-scaffold expects each recipe to live in its own directory, containing a `recipe.json` plus any other files needed to fulfil the recipe:

```
{recipe}/
  recipe.json     ← metadata: name, type, description, tags
  ...             ← any other files the recipe needs to apply
```

`recipe.json` must conform to [`smart_scaffold/schemas/recipe.schema.json`](smart_scaffold/schemas/recipe.schema.json):

| Field         | Description                               |
| ------------- | ----------------------------------------- |
| `name`        | The recipe name                           |
| `type`        | The type of recipe, e.g. `github-actions` |
| `description` | What the recipe does                      |
| `tags`        | Tags for the recipe, used for searching   |

The `type` determines how the recipe is contextually applied to the destination repository (e.g. `github-actions` recipes are merged into existing workflow files where possible).

### Example `recipe.json`

See [smart-scaffold-recipes](https://github.com/danwiltshire/smart-scaffold-recipes) for complete examples.

```json
{
  "$schema": "https://raw.githubusercontent.com/danwiltshire/smart-scaffold/refs/heads/main/smart_scaffold/schemas/recipe.schema.json",
  "description": "Scans the repository for security vulnerabilities.",
  "name": "Security Scan",
  "type": "github-actions",
  "tags": ["security", "grype"]
}
```

## Authentication

smart-scaffold reads a GitHub token in the following order:

1. `GITHUB_TOKEN` environment variable
2. `gh auth token` (GitHub CLI)

The token must have permission to read the recipe repository and read/write the destination repository.

## Developing

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
uv sync
uv run pre-commit install
```

### Linting

[Ruff](https://docs.astral.sh/ruff/) is configured in `pyproject.toml`. Pre-commit runs it automatically on every commit.

To run manually:

```bash
uv run pre-commit run --all-files
```

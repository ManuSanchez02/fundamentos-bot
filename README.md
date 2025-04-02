# Fundamentos de la Programación - Discord Bot

This is a Discord bot for the "Fundamentos de la Programación" course at the Universidad de Buenos Aires.

## Installation

To run this bot, you will need to have `uv` installed.

Once you have `uv` installed, you can run the bot using the following command to install the required dependencies:

```bash
uv sync
```

### Pre-commit hook
To install the pre-commit hook, run the following command:

```bash
uv run pre-commit install
```

This will install the pre-commit hook in your local repository. The pre-commit hook will automatically run the linters and formatters on your code before each commit. This will help you maintain a consistent code style and catch any errors before they are committed to the repository.

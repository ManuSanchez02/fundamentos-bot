# Fundamentos de la Programación - Discord Bot

This is a Discord bot for the "Fundamentos de la Programación" course at the Universidad de Buenos Aires.

## Installation

To run this bot, you will need to have `uv` installed.

Once you have `uv` installed, you can run the bot using the following command to install the required dependencies:

```bash
uv sync
```

**Note**: You should set the interpreter of your IDE to the one you are using in your virtual environment. In VSCode, you can do this by pressing `Ctrl + Shift + P` to open the command palette and selecting `Python: Select Interpreter`. Then, select the interpreter that corresponds to your virtual environment.

### Pre-commit hook

To install the pre-commit hook, run the following command:

```bash
uv run pre-commit install
```

This will install the pre-commit hook in your local repository. The pre-commit hook will automatically run the linters and formatters on your code before each commit. This will help you maintain a consistent code style and catch any errors before they are committed to the repository.

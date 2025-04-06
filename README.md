# Fundamentos de la Programación - Discord Bot

This is a Discord bot for the "Fundamentos de la Programación" course at the Universidad de Buenos Aires.

## Installation

Make sure you follow the instructions below to set up the bot correctly.

### Requirements

- [uv](https://docs.astral.sh/uv/) - A Python package manager that allows you to create and manage virtual environments. This is a requirement for running the bot locally.
- [Docker](https://www.docker.com/) - In case you want to run the bot in a container. Check out the [Docker section](#docker) for more information.

### Environment variables and GCP credentials

Firstly, you need to clone the `.env.EXAMPLE` file and rename it to `.env`. This file contains the environment variables needed to run the bot. You can find the `.env` file in the root directory of the project. After renaming it, you need to fill in the required values. The following environment variables are required:

```env
DISCORD_TOKEN=<your_discord_token>
SPREADSHEET_ID=<your_spreadsheet_id>
```

You can obtain a Discord token in the [Discord Developer Portal](https://discord.com/developers/applications), or asking for the token in Slack!

The rest of the environment variables are optional and can be left as is. Here is a list of the optional environment variables:

```env
DISCORD_GUILD_ID=<your_discord_guild_id> # The ID of the Discord server (guild) where the bot will be running, mainly used for dev purposes to register and refresh the slash commands.
LOG_LEVEL=<log_level> # The log level for the bot. Can be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL. Default is INFO.
```

In order to use the Google Cloud Platform APIs, you will need to set up your credentials. To do so, you can either create a service account in the Google Cloud Console and download the JSON key file, or ask for the credentials through Slack. Once you have the key file, you should rename it to `gcp_credentials.json` and place it in the root directory of the project. The bot will automatically load the credentials from this file when it starts up.

Once you have set up all the required environment variables, you can follow the instructions below to finish get the bot up and running.

### Local installation

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

## Usage

There are two ways to run the bot: locally or using Docker. You can choose the one that best suits your needs.

### Running locally

To run the bot locally, you should have the required dependencies installed and the environment variables set up (see the [Installation](#installation) section). Once you have everything set up, you can run the bot using the following command:

```bash
uv run bot
```

This will start the bot and it will connect to your Discord server. You should see a message in the console indicating that the bot is online.

### Running with Docker

If you prefer to run the bot using Docker, you can do so by using the provided `docker-compose.yml` file. This file contains the configuration for running the bot in a Docker container.

To run the bot using Docker, you need to have Docker installed and running on your machine. Once you have Docker installed, you can run the following command in the root directory of the project:

```bash
./run_docker.sh
```

This will build the Docker image and start the bot in a container. You should see a message in the console indicating that the bot is online.

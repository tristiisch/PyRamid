# PyRamid

[![GitHub Actions Status](https://github.com/tristiisch/PyRamid/actions/workflows/compile.yml/badge.svg?branch=main)](https://github.com/tristiisch/PyRamid/actions)
[![Docker Image](https://img.shields.io/docker/v/tristiisch/pyramid/latest?label=Docker%20Hub)](https://hub.docker.com/r/tristiisch/pyramid)

This Python-built Discord bot empowers users to download music via the Deezer API. It enables seamless song, artist, or album searches and direct downloads from Deezer. By incorporating the Spotify API, it enhances search capabilities.

Since direct music retrieval from Spotify is not feasible, the bot relies on Deezer.

It's designed for use within Discord guilds and isn't compatible with private Discord conversations.

Upon integration, the bot unlocks a range of commands. Simply type /help to access a list of all available commands.

The original GitHub repository can be accessed [here](https://github.com/tristiisch/PyRamid).

## Usage

Add this bot discord to your guild [here](https://discord.com/api/oauth2/authorize?client_id=1162155331124736101&permissions=380174863936&scope=bot).

For self-hosted usage, please refer to the "Docker images" and "Configuration" sections.

## Docker Image

Docker images for PyRamid are available on Docker Hub. You can find the images at the following repository:

[Docker Hub - PyRamid](https://hub.docker.com/repository/docker/tristiisch/pyramid)

The available tags are as follows:

- `latest`: The latest stable release.
- `pre-prod`: The version that is currently under development and is considered unstable.
- `X.X.X`: The stable version with the specific version number.
- `X.X.X-<git_commit>`: The version linked to a specific git commit, which can be either unstable or stable depending on the context.

Feel free to pull the appropriate Docker image based on your requirements.

## Configuration

The default configuration file for PyRamid is [config.example.yml](https://github.com/tristiisch/PyRamid/blob/main/config.exemple.yml), which should be renamed and modified to `config.yml`. Ensure you replace the placeholder values in `config.yml` with your specific configuration details.

Alternatively, you can utilize environment variables to define the configuration. The keys remain the same, separated by underscores. For example, the Discord token would be set as follows: `DISCORD_TOKEN: <your_discord_bot_token>`.

Keep in mind that the configuration file takes precedence over environment variables. In other words, if a configuration value is defined both in the file and as an environment variable, the value from the file will be used. Ensure your configuration is appropriately set in either the file or as environment variables, depending on your preferred method of configuration.

## Contributions & Forks

Feel free to fork the project while adhering to the license and acknowledging the original work.

For seamless integration of your modifications, submitting pull requests to the original bot version is recommended.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Author

Tristiisch

# PyRamid

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

The default configuration file for PyRamid is `config.example.yml`, which needs to be renamed and modified to `config.yml` with the following structure:

```yaml
discord:
  # To create your Discord bot, visit: https://discord.com/developers/applications
  #
  # CRUCIAL: Activate the MESSAGE CONTENT INTENT, which is located in the Privileged Gateway Intents tab under the Privileged Gateway Intents section.
  # For adding your bot to a guild with the appropriate permissions, replace the client_id with your own: https://discord.com/api/oauth2/authorize?client_id=1162155331124736101&permissions=380174863936&scope=bot
  # Then, locate the token in the Bot tab and click on the "Reset Token" button.
  # You must enter this token below to utilize the newly created bot.
  token: <token bot discord>

  # You must install the ffmpeg software, as it enables the playback of audio files.
  # On a Linux kernel, once installed, you can typically locate this file at /usr/bin/ffmpeg.
  # If this isn't the case, run `which ffmpeg` to identify the binary file's location.
  #
  # For Windows, you'll need to install the program and link it to the .exe file.
  # Many applications utilize this utility, which means it might already be installed.
  # Please search your computer for further verification.
  ffmpeg: <path to ffmpeg.exe>


deezer:
  # The directory housing the downloaded music.
  folder: ./songs

  # You need an "ARL" from a deezer account to download music
  # You can find documentation on https://github.com/nathom/streamrip/wiki/Finding-Your-Deezer-ARL-Cookie
  # While there is no strict limitation, it's advisable to set up a dedicated account specifically for this task using private browsing mode.
  # This prevents accidental usage of Deezer's "disconnect" button, which alters the ARL (Authentication Request Link).
  arl: <deezer arl of an account>


# You need to create a spotify application to make spotify search
# Documentation is available at https://developer.spotify.com/documentation/web-api/concepts/apps
spotify:
  client_id: <client id of your spotify application>
  client_secret: <client secret of your spotify application>

# Available value: production, pre-production, development
# Change message level in logs
mode: production

# Please refrain from making any changes to this.
# This represents the formatted version of the configuration.
# If the version isn't up to date, it suggests that the file might have been altered to ensure compatibility with the latest version.
# The program will make every effort to handle these adjustments without requiring human intervention.
version: 0.1
```

Make sure to replace the placeholder values with your actual configuration details.

## Contributions & Forks

Feel free to fork the project while adhering to the license and acknowledging the original work.

For seamless integration of your modifications, submitting pull requests to the original bot version is recommended.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Author

Tristiisch

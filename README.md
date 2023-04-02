# Machi-bot
Bot for posting videos (webm) to twitter.

## Setup (Windows)
### Python
You need atleast python 3 (tested on 3.11.0). Make sure to add python to path.

It's recommended to use python virtual environments. Create one in the project root.

https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment

```
py -m venv env
```

Activate the environment.

```
.\env\Scripts\activate
```

Install requirements

```
py -m pip install -r requirements.txt
```

### Twitter app credentials
You need to create an application in twitter developer portal.

https://developer.twitter.com/

The application needs the following permissions and settings.

- App permissions
    - Read and write
- Type of App
    - Web App, Automated App or Bot
- App info
    - Callback URI / Redirect URL
        - https://localhost
    - Website URL
        - http://example.org

Generate your application keys on the 'Keys and Tokens' page and add them to a .env file in your project root.

For now you need both the v1 and v2 API keys and secrets.

```
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
```

### Config
Create config.json in the project root.

You'll need ffmpeg to convert videos to twitter approved mp4.

https://ffmpeg.org/download.html#build-windows

Add path to your ffmpeg and media folder to config.json. Media folder is scanned recursively.
You'll also need to add the appdata folder where you want your database to be.

```JSON
{
    "ffmpeg-location": "C:/ffmpeg/bin/ffmpeg.exe",
    "media-location": "C:/Users/Machi/Videos",
    "appdata": "D:/personal_projects/machi-bot"
}
```

You can optionally specify if you want to print ffmpeg output, post link of the tweet to discord webhook or exclude paths from media scan.
```JSON
{
    "ffmpeg-output": true,
    "discord-webhook-url": "",
    "exclude-folders": ["lewd", "tmp/foobar"]
}
```

Excluded paths are read starting from media-location. For example with `"media-location": "C:/Users/Machi/Videos"` and `"exclude-folders": ["tmp/foobar"]`, `C:/Users/Machi/Videos/tmp/foobar` is skipped but everything in `C:/Users/Machi/Videos/tmp` is read.

## Running
```
py -m machi_bot --help
```

When posting you need to authorize the app on behalf of your twitter account. Make sure you're logged on the account you want the bot to tweet as.

Follow the authorization links on the terminal. By our default configuration twitter will redirect to localhost. Just paste the whole url in terminal.


## Docker
Requires authenticating with the normal app and copying token_v1.json and token_v2.json to the appdata folder you're mounting to docker.
### Docker-compose
Set EXCLUDE_FOLDERS as a comma separated string

```YAML
---
services:
  machi_bot:
    image: docker.io/feddle/machi-bot:latest
    init: true
    container_name: machi_bot
    environment:
      - EXCLUDE_FOLDERS=tmp/foobar,work,lewd
      - DISCORD_WEBHOOK_URL=
      - TWITTER_API_KEY=
      - TWITTER_API_SECRET=
      - TWITTER_BEARER_TOKEN=
      - TWITTER_CLIENT_ID=
      - TWITTER_CLIENT_SECRET=
      - TWITTER_V1_ACCESS_TOKEN=
      - TWITTER_V1_SECRET=
    volumes:
      - <path_to_videos>:/media
      - <path_to_tokens_and_db>:/appdata
```



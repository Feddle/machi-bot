# Machi-bot
Bot for posting videos to twitter.

## Setup
### Python
You need atleast python 3 (tested on 3.11.0). Make sure to add python to path.

It's recommended to use python virtual environments. Create one in the project root.

https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment

`py -m venv env`

Activate the environment.

`.\env\Scripts\activate`

Install requirements

`py -m pip install -r requirements.txt`

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

If the video files you want to tweet are not in mp4 you'll need ffmpeg.

https://ffmpeg.org/download.html#build-windows

Add path to your ffmpeg in to the config.json.

```JSON
{
    "ffmpeg-location": "C:/ffmpeg/bin/ffmpeg.exe"
}

```

## Running
`py -m machi-bot`




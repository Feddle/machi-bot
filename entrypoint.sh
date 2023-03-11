#!/bin/sh

cp /appdata/token_v1.json /app/machi-bot
cp /appdata/token_v2.json /app/machi-bot

cat << EOF > config.json
{
    "ffmpeg-location": "ffmpeg",
    "media-location": "/media",
    "appdata": "/appdata",
    "exclude-folders": "$EXCLUDE_FOLDERS",
    "ffmpeg-output": false,
    "discord-webhook-url": "$DISCORD_WEBHOOK_URL"
}
EOF

cat << EOF > .env
TWITTER_API_KEY=$TWITTER_API_KEY
TWITTER_API_SECRET=$TWITTER_API_SECRET
TWITTER_BEARER_TOKEN=$TWITTER_BEARER_TOKEN
TWITTER_CLIENT_ID=$TWITTER_CLIENT_ID
TWITTER_CLIENT_SECRET=$TWITTER_CLIENT_SECRET
TWITTER_V1_ACCESS_TOKEN=$TWITTER_V1_ACCESS_TOKEN
TWITTER_V1_SECRET=$TWITTER_V1_SECRET
EOF

env >> /etc/environment
crond -f -l 2
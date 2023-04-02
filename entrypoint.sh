#!/bin/sh

cp /appdata/token_v1.json /app/machi-bot
cp /appdata/token_v2.json /app/machi-bot

# Get the value of the EXCLUDE_FOLDERS environment variable
exclude_folders=$EXCLUDE_FOLDERS

# Convert the comma-separated list to a JSON array of strings
exclude_folders_array=$(echo "$exclude_folders" | jq -R 'split(",")')

# Create the JSON object with the desired keys and values
json_object=$(echo '{}' | jq \
    --arg ffmpeg_location "ffmpeg" \
    --arg media_location "/media" \
    --arg appdata "/appdata" \
    --argjson exclude_folders "$exclude_folders_array" \
    --argjson ffmpeg_output false \
    --arg discord_webhook_url "$DISCORD_WEBHOOK_URL" \
    '. +
    {
        "ffmpeg-location": $ffmpeg_location,
        "media-location": $media_location,
        "appdata": $appdata,
        "exclude-folders": $exclude_folders,
        "ffmpeg-output": $ffmpeg_output,
        "discord-webhook-url": $discord_webhook_url
    }'
)

# Write the JSON object to a file
echo "$json_object" > config.json

cat << EOF > .env
TWITTER_API_KEY=$TWITTER_API_KEY
TWITTER_API_SECRET=$TWITTER_API_SECRET
TWITTER_BEARER_TOKEN=$TWITTER_BEARER_TOKEN
TWITTER_CLIENT_ID=$TWITTER_CLIENT_ID
TWITTER_CLIENT_SECRET=$TWITTER_CLIENT_SECRET
TWITTER_V1_ACCESS_TOKEN=$TWITTER_V1_ACCESS_TOKEN
TWITTER_V1_SECRET=$TWITTER_V1_SECRET
EOF

python3 -m machi_bot -p
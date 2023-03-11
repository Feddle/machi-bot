# Build from latest alpine linux
FROM python:3.12.0a6-alpine3.17

# Make a directory for the app
RUN mkdir -p /app/machi-bot

COPY . /app/machi-bot

# Set working directory context
WORKDIR /app/machi-bot

# Install dependencies
RUN \
    apk add --no-cache ffmpeg git && \
    pip install -U --no-cache-dir -r requirements.txt
#   git clone -b main --single-branch https://github.com/Feddle/machi-bot.git /app/machi-bot

# Cleanup: cron confs
RUN rm -rf /etc/periodic

# Copy crontab schedule
COPY crontab /var/spool/cron/crontabs/root

VOLUME [ "/media", "/appdata"]

# Command for container to execute
ENTRYPOINT [ "/bin/sh" ]
CMD [ "./entrypoint.sh" ]
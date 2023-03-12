# Build from latest python alpine linux
FROM python:3.12.0a6-alpine

# Make a directory for the app
RUN mkdir -p /app/machi-bot

# Copy source
COPY . /app/machi-bot

# Set working directory context
WORKDIR /app/machi-bot

# Install dependencies
RUN \
    apk add --no-cache ffmpeg && \
    pip install -U --no-cache-dir -r requirements.txt && \
    chmod +x /app/machi-bot/entrypoint.sh

VOLUME [ "/media", "/appdata"]

# Command for container to execute
ENTRYPOINT [ "./entrypoint.sh" ]
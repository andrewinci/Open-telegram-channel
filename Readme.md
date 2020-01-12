# Telegram channel for Open online 

Telegram channel for Open news.

## How to use

- Create a telegram channel
- Create a telegram bot
- Run the container

## Test with docker

Replace `<@channel>` with the actual telegram channel and `<bot_key>` with the bot key from botfather.

```bash
docker build . -t open
docker run --name open -e TGCHANNELID=<@channel> -e TGBOTKEY=<bot_key> -d open
```

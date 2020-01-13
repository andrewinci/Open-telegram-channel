# Telegram channel for Open online

Telegram channel for Open news.

## How to use

- Create a telegram channel
- Create a telegram bot with BotFather
- Deploy to AWS or use the container for testing

## Deployment to AWS

Use `build.sh` to build the lambda zip. (Requires docker).

```bash
chmod +x build.sh
./build.sh
```

Use terraform in order to deploy the infrastracture + the code to AWS.

```bash
export TF_VAR_telegram_bot_key=<bot_key>
export TF_VAR_telegram_channel_id=<@channel>
terraform init
terraform apply -auto-approve
```

## Test with docker

Replace `<@channel>` with the actual telegram channel and `<bot_key>` with the bot key from botfather.

```bash
docker build . -t open
docker run --name open -e TGCHANNELID=<@channel> -e TGBOTKEY=<bot_key> -d open
```

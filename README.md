# Telegram custom news aggregator
## version 1.0
Provides the headlines or digests of chosen telegram channels for the period of time.

## Bot in action
To check how it works just try it yourself https://t.me/news_custom_aggregator_bot
- Press start or send a message `/start`
- Use the buttons or keyboard to get news or digests from different sources.

## How to start
- Create and fill in `.env` in the root folder of the project (folder with `main.py` and `.env.example`).
- Create `user_settings.json` in the `users` folder. It is advised to just rename the `users_settings.json.example`.
- Run main.py
- Terminal will ask you for bot token and phone number. Provide this information. For details see "Sessions" below.

**Important**. Telegram custom news aggregator uses "Bot API" and "Telegram API", bot and userbot accordingly. Which means you need to have a bot and a telegram account.

## Sessions
In order to use a bot you need to provide some credentials. Pyrogram uses session files for this purpose. Below are the actions to create these files.
- Start the bot locally (run main.py).
- Provide necessary data in terminal for bot session (bot token).
- Stop the bot.
- Launch bot again.
- Ask bot for digest or headers.
- Enter phone and confirmation code for userbot.
- If you use remote server: copy my_bot.session and my_userbot.session into the folder of your project on the remote server (for example: scp my_bot.session username@111.111.111.111:~/tg_news_aggregator)

How to obtain api_id: https://core.telegram.org/api/obtaining_api_id \
How to obtain bot token: https://core.telegram.org/bots/tutorial#obtain-your-bot-token

## .env file
- `API_ID` - get it using the guide https://core.telegram.org/api/obtaining_api_id \
- `API_HASH` - get it using the guide https://core.telegram.org/api/obtaining_api_id \
- `BOT_TOKEN` - get it using the guide https://core.telegram.org/bots/tutorial#obtain-your-bot-token \
- `CHANNELS` - channels which will be parsed to get news; at the moment `username` of the channel is used, NOT `id`; in the current version 1.0 the channels are hardcoded, so use the value provided in `.env.example`
- `TIME_PERIOD_MINUTES` - get news for this period, default value is 720 (hint: 720 is 12 hours, 1440 is 24 hours).
- `MAX_MESSAGE_LENGTH` - maximus length of message in telegram, used to split too long messages; default value is 4096, higher values will cause error.
- `MESSAGES_PER_CHANNEL_LIMIT` - amount of messages which userbot will read from one telegram channel; recommended values are from 50 to 100.
- `ADMIN_CHAT_ID` - optional, sends the message to the according chat if there is some error or other administrative issue; default value is empty (literally, nothing after `=`).
- `DEBUG` - used in code to trigger debug mode; default value is False.


## Users settings
Each user may subscribe or unsubscribe from any channel available in the `.env` file (field `CHANNELS`).
All subscriptions are stored in the `users\user_settings.json`. The file has the following structure:
```
[
    {
        "id": "0000000",  # telegram id of the user
        "channels": [     # subscriptions of the user
            "bbcrussian",
            "fontankaspb"
        ]
    },
    {
        "id": "1111111",
        "channels": [
            "fontankaspb"
        ]
    },
]
```

## GitHub Workflow
Workflow checks that code is formatted according to the black standard. Remove job 'linter' from the workflow if you use another standard.\
Be aware, that workflow launches `docker system prune -f` after deployment. You may consider to remove this line.
# Darth Vader chatbot

This repository contains the code needed to chat with your own Darth Vader
using telegram.

## How to run

Put your OpenAI API key and Telegram Bot Token in `deploy/tgbot.env` file.
If you wish, you can modify default postgres username, password and database
name in files `deploy/postgres.env` and `deploy/tgbot.env`, make sure they
match (I'm not sure why I didn't put that in one file).

After that build the needed images using

```bash
docker-compose -f deploy/docker-compose.yaml build
```

and then start your service using

```bash
docker-compose -f deploy/docker-compose.yaml up
```

The postgres data will be stored in the `data` volume. I guess I should have
made another volume for tgbot logs, oh well.

## Approach description

For each user, I store each their exchange with the AI in the database, so I
can get all the dialogue history. When the bot receives a new message I
aggregate all the history for this user, prepend the prompt describing the AI's
task of being Darth Vader and how it should answer. After that, I make a request
to openai API for text completion. All the configuration parameters lie in the
`configs/config.toml` file, so we can easily modify the AI's behavior.

This should be able to support multiple users and live through restarts due to
data persistency in the docker volume :D

I could've added logging of each message, the time it took to answer it and 
other things, but decided not to due to the prototype nature of the project.

# EuphoriaBot

Welcome to **EuphoriaBot**! Outlined below are the procedures for installation/maintaining a clone of the bot, as well as the features the bot has.

## Setup

### Setting up a Discord Application

Head to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application. Give it a fun name, something like EuphoriaClone.
![Application page](https://i.imgur.com/MUvtCSD.png)
Make a note of the Client ID. This along, with a token for your bot and your own Discord ID, will go into a configuration file used to connect to the Discord API.
Next, go to the Bot tab of the Developer Portal and select "Add Bot." Give it a name and optionally upload a profile picture (the included nbheart.png, perhaps?). Under the "Token" section, make note also of the token for your bot. This is all the setup you need on Discord's end of things.
![Bot tab](https://i.imgur.com/xPnm9C6.png)

### Setting up your bot's environment
This guide assumes your system has Python installed, at least version 3.6.9.

First, install all of the bot's dependencies. Navigate to the directory where the bot will be running and run
`pip3 install -r requirements.txt` (or `pip install -r requirements.txt`, depending on system Python installation)

As provided in the repository, the bot requires very minor tweaks in order to get it up and running. All you have to do is go into the `.env` file and change the three environment variables to the proper values.
- DISCORD_TOKEN will be the token you copy from the Bot tab of the Developer portal.
- CREATORID will be your own Discord ID. You can acquire this following [This guide](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-).
- BOTID will be the Client ID you copy from the General Information tab of the Developer Portal.

You should now invite the bot to a server. You can generate a link to invite the bot to a server very easily; simply use this template:
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID_HERE&permissions=805644288&scope=bot
and replace "CLIENT_ID_HERE" with the same value you placed in the BOTID field of the `.env` file.

Once the bot is in the server(s) you want it in, you can start the bot!
Ideally, this is run as a background service (I personally run it as a service on an Ubuntu server), but what also works is to simply run `bot.py` with Python. With that, you're good to go! You can make finer changes by modifying the `bot.py` file or add custom resources to be used by `!resources` by modifying the `resources.json` file.

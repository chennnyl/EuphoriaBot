# EuphoriaBot

Welcome to **EuphoriaBot**! Outlined below are the procedures for installation/maintaining a clone of the bot, as well as the features the bot has.

##### Table of Contents
1. [Features](#features)
    + [General features](#general)
        + [Trying names and pronouns](#try)
            + [User-set names](#names)
        + [Serving categorized resources](#resources)
        + [Allow suggestions](#suggestions)
        + [Plural systems](#plural)
    + [Administrative features](#admin)
        + [Purge channels](#purge)
        + [Give users roles via reactable messages](#roles)
        
2. [Setup](#setup)
    + [A quick note](#aquicknote)
    + [Setting up a Discord Application](#discordapp)
    + [Setting up your bot's environment](#envsetup)
    + [Setting up bot as a background service (Any Linux server using `systemd`)](#backserv)

<a name="features"/>

## Features

<a name="general" />

### General features

<a name="try"/>

#### Trying names and pronouns

<a name="names"/>

##### User-set names

<a name="resources"/>

#### Serving categorized resources

<a name="suggestions"/>

#### Allow suggestions

<a name="plural"/>

#### Plural systems

<a name="admin"/>

### Administrative features

<a name="purge"/>

#### Purge channels

<a name="roles"/>

#### Give users roles via reactable messages

<a name="setup"/>

## Setup

<a name="aquicknote"/>

### A quick note
Before beginning, if you'd like to follow the steps listed in **Setting up bot as a background service**, make sure you're installing EuphoriaBot on a Linux server where you have administrative privileges.

<a name="discordapp"/>

### Setting up a Discord Application

Head to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application. Give it a fun name, something like EuphoriaClone.
![Application page](https://i.imgur.com/MUvtCSD.png)
Make a note of the Client ID. This along, with a token for your bot and your own Discord ID, will go into a configuration file used to connect to the Discord API.
Next, go to the Bot tab of the Developer Portal and select "Add Bot." Give it a name and optionally upload a profile picture (the included nbheart.png, perhaps?). Under the "Token" section, make note also of the token for your bot. This is all the setup you need on Discord's end of things.
![Bot tab](https://i.imgur.com/xPnm9C6.png)

<a name="envsetup"/>

### Setting up your bot's environment
This guide assumes your system has Python installed, at least version 3.6.9.

First, install all of the bot's dependencies. Navigate to the directory where the bot will be running and run
`pip3 install -r requirements.txt` (or `pip install -r requirements.txt`, depending on system Python installation)

As provided in the repository, the bot requires very minor tweaks in order to get it up and running. All you have to do is go into the `.env` file and change the three environment variables to the proper values.
+ DISCORD_TOKEN will be the token you copy from the Bot tab of the Developer portal.
+ CREATORID will be your own Discord ID. You can acquire this following [this guide](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-).
+ BOTID will be the Client ID you copy from the General Information tab of the Developer Portal.

You should now invite the bot to a server. You can generate a link to invite the bot to a server very easily; simply use this template:
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID_HERE&permissions=805644288&scope=bot
and replace "CLIENT_ID_HERE" with the same value you placed in the BOTID field of the `.env` file.

Once the bot is in the server(s) you want it in, you can start the bot!
Ideally, this is run as a background service (I personally run it as a service on an Ubuntu server), but what also works is to simply run `bot.py` with Python. With that, you're good to go! You can make finer changes by modifying the `bot.py` file or add custom resources to be used by `!resources` by modifying the `resources.json` file.

<a name="backserv"/>

### Setting up bot as a background service (Any Linux server using `systemd`)
This section of the guide is optional -- running the bot as a background service, however, is a great asset if you're able to run a Linux server and can save a great deal of headache. Begin by creating the service file:

`$ sudo nano /etc/systemd/system/dbot.service`
And paste in the following code:
`[Unit]
Description=EuphoriaBot Discord bot
After=multi-user.target
[Service]
WorkingDirectory=BOT_DIRECTORY
User=YOUR_USERNAME
Group=YOUR_USERNAME
ExecStart=/usr/bin/python3 BOT_DIRECTORY/bot.py
Type=idle
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target`
Make sure you replace BOT_DIRECTORY and YOUR_USERNAME with the directory where the bot files are contained and your username, respectively. Save the file, and execute the following two commands:
`$ sudo systemctl enable dbot.service`
`$ sudo systemctl start dbot.service`
At any time, you can check the status of the bot with
`$ systemctl status dbot.service` or read its log with `$ journalctl -u dbot.service` (make sure to scroll to the bottom by pressing `End`)

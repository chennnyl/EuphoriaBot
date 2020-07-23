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
            + [Automatic purges](#autopurge)
        + [Give users roles via reactable messages](#roles)
        + [Server-wide settings](#settings)
        
2. [Setup](#setup)
    + [A quick note](#aquicknote)
    + [Setting up a Discord Application](#discordapp)
    + [Setting up your bot's environment](#envsetup)
    + [Setting up bot as a background service (Any Linux server using `systemd`)](#backserv)

<a name="features"/>

## Features

This section of the guide will outline the various commands of EuphoriaBot as well as their mechanisms of action, if pertinent to explain. A more concise version of this section may be obtained via the `!help` command. Example calls and output of each message will be provided as well.

<a name="general" />

### General features

This section describes the commands and features available to all users.
<a name="try"/>

#### Trying names and pronouns

The chief reason EuphoriaBot was constructed was the ability for users to request the bot call them by a chosen name and set of pronouns. The command users may use to interface with the bot in this manner is `!np`, whose syntax is outlined here:
```
!np "<pronoun set 1 [-p]> [pronoun set 2 [-p]] [pronoun set 3 [-p]]..." ["<name 1> [name 2]..."]
```
The command is blocked out by `!np`, `"pronouns"`, and `"names"`, with the latter two blocks being separately quoted. Each set of pronouns must be in the format of `nominative case/objective case/genitive case`, such as `he/him/his` or `they/them/their`. Some sets of pronouns (such as `they/them/their`) are grammatically plural -- in these cases, the optional flag `-p` is added to the end of the set of pronouns. Some examples of pronoun sets are illustrated below:

| Pronoun set/common usage | Nom | Obj  | Gen   | `!np` usage                |
| ------------------------ | --- | ---- | ----- | -------------------------- | 
| he/him/his               | he  | him  | his   | `!np "he/him/his"`         |
| she/her/hers             | she | her  | her   | `!np "she/her/her"`        | 
| they/them/theirs         | they| them | their | `!np "they/them/their -p"` |

Note that the -s on the end of genitive pronouns such as "hers" and "theirs" is omitted when using `!np`. For proper display, it's important users are made aware of this, either by advising them to carefully read the output of `!help np` or by simply reminding them of this fact.

A set of names delineated by spaces is also entirely optional -- if it is not provided, the bot will first check `usernames.json` to see if the user has registered a name/set of names (see below), and if they have not, it will use their display name/server nickname.

The sentences the bot will send are randomly picked from `sentences.txt`, which can be extended or modified according to server needs. Each is provided as an f-string kept on its own line. Note the formatting used in each: method calls to `nick()`, `nom()`, `obj()`, `gen()`, and `nom_verb()` are made. `nom_verb()` may be passed a *simple* verb as a string, and the bot will append an 's' if the appropriate pronoun is singular, and omit it otherwise.

![!np call](https://imgur.com/9qcCyEX.png)

<a name="names"/>

##### User-set names

Users may also register a custom name/set of names using the `!name` command, whose syntax is simple, almost a subset of that of `!np`:
```
!name "[name 1] [name 2]..."
```
The name parameters are optional -- if omitted, the bot will fetch the user's stored name(s) from `usernames.json` and display them to the user. Otherwise, it will update the user's value in `usernames.json` to match the name(s) provided as parameters.

![!name call](https://imgur.com/0CFCh18.png)

<a name="resources"/>

#### Serving categorized resources

The default function of `!resources` is to serve users links and phone numbers for organizations and services catered to members of the LGBTQ+ community. The syntax of the command is as follows:
```
!resources [category]
```
If the `category` parameter is omitted, a list of categories (the keys in `resources.json`) will be provided to the user.
It should be noted that the functionality of this command is fully malleable: The resources to be served to the user are stored in `resources.json` as key:value pairs corresponding to `category:string`. Thus, any feasible combination of resources may be placed in `resources.json`. It is important to note, however, that if you choose to diverge from the default set of resources, the help string for the command and its description provided by `!help` should be modified in turn.

![!resources call](https://imgur.com/rPQe650.png)

<a name="suggestions"/>

#### Allow suggestions

The `!suggest` command is very simple, as is its syntax.
```
!suggest "<suggestion>"
```
The suggestion must consist of at least two words and be more than 15 characters in length. The content of the message, as well as the user who called it, will be sent via DM to the user whose ID is specified by the CREATORID environment variable (see [Setting up your bot's environment](#envsetup)). To suppress this functionality, set the CREATORID environment variable to an arbitrary number (try `100000000000000000`)

![!suggest call](https://imgur.com/AI65Bsk.png)

<a name="plural"/>

#### Plural systems

This is the most complex feature EuphoriaBot has to offer. If you are looking for a more robust, ergonomic, and overall *better* implementation of this functionality, I advise you to look towards the bot [PluralKit](pluralkit.me). If you would rather stick to a simpler implementation or simply would rather not have too many bots on your server, feel free to continue.
This feature of EuphoriaBot implements an automatic message proxying system for users possessing or in want of a *system*, a term used in classifying [disassociative identity disorder](https://en.wikipedia.org/wiki/Disassociative_identity_disorder), but whose implementation has uses for others, such as roleplayers and cosplayers. Essentially, users are able to create one or more additional identities under which to send messages while remaining under only one account; these identities can have unique profile pictures and usernames, and are activated when the bot identifies user-defined prefixes/postfixes in a message sent to a channel. This functionality in EuphoriaBot is accessed via the `!plural` command, which has several subcommands, whose various syntaxes are listed below.

`!plural add "<name>"`: Add a new member (also called an alter) to the user's system, with the default pre/postfixes "{" and "}"
`!plural delete "<name>"`: Remove a member from the user's system
`!plural list`: List the members in a user's system
`!plural edit "<name>" <name|prefix|postfix|avatar> "<value>"`: Edit an attribute of a system's member. `avatar` refers to a URL leading to an image to be used as the member's profile picture
Plurals for each user are stored in `plurals.json` in a fairly self-explanatory format.

The plural system works by creating a webhook for the channel in which a member is invoked, echoing the queried message (sans pre/postfixes) under the banner of the member by making a POST request to the webhook, and deleting the original message.

![!plural calls](https://imgur.com/hrWpz7o.png)

![Making a webhook query](https://imgur.com/4Aq4chW.png)

The top message is deleted once the bot sends its message, but is included for illustrative purposes.

<a name="admin"/>

### Administrative features

These are features available only to users with pertinent permissions (insofar as managing messages or roles).

<a name="purge"/>

#### Purge channels

This is arguably the simplest command EuphoriaBot has to offer. Simply invoke the command `!purge` like so:
```
!purge
```
All messages in the channel will be deleted. This behavior can, at times, be quite slow and buggy, despite making only one API call: use with caution.

<a name="autopurge"/>

##### Automatic purges

You can set up automatic purges of channels equally simply: simply use the `!addpurge` command:
```
!addpurge [days]
```
Where `[days]` is a number of days after which the channel will automatically clear itself; decimal values may also be input. You may check the remaining time until a channel purges in seconds via `!purget`:

![!purget call](https://i.imgur.com/k4xXHI5.png)

<a name="roles"/>

#### Give users roles via reactable messages

Oftentimes it is useful for users to be able to assign themselves certain vanity roles by simply reacting to a message. This functionality is possible via the twin commands `!rrole` and `!r`. `!rrole` serves to make associations between server roles and the emoji reactions used to assign them. Its syntax is as follows:
```
!rrole [<<emoji> "<role>"> [<emoji> "<role>"]...]
```
Where an indefinite number of pairs of emoji and roles may be provided. If that number is zero, a list of the current associations (stored in `roles.json`) will be displayed. Once the entirety of the associations are made, you may then call `!r`, whose syntax is as follows:
```
!r "<message>"
```
This message must contain, somewhere, the word "react" so the bot may detect reactions added/removed to it. This message should contain a list of the roles users can obtain and the appropriate reactions in order to be useful. If the list of associations is at any point modified, it is wise to call `!r` again, as the message is immutable once sent. Once called, the bot will remove the message used to call it for display purposes.

![!r and !rrole calls](https://imgur.com/g6Mj3im.png)

Note that the `!r` call was automatically deleted by the bot.

<a name="settings"/>

#### Server-wide settings

You may set global settings for your server via the `!setting` command. As of now, the available settings are expressed in the syntax as follows:
```
!setting [joinRestrict|joinMessage] [value]
```
| Setting        | Acceptable values             | Role                                              |
| -------------- | ----------------------------- | ------------------------------------------------- |
| *joinRestrict* | TRUE, FALSE                   | Assign a role upon members joining\*              |
| *joinMessage*  | Any string <= 2000 characters | Send a message to new members upon joining via DM |

\* As of now, this setting requires very specific input and circumstances and is yet to be reworked. Refrain from using.

![!setting example](https://i.imgur.com/9wNsnCw.png)

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
and paste in the following code:
```
[Unit]
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
WantedBy=multi-user.target
```
Make sure you replace BOT_DIRECTORY and YOUR_USERNAME with the directory where the bot files are contained and your username, respectively. Save the file, and execute the following two commands:
`$ sudo systemctl enable dbot.service`
`$ sudo systemctl start dbot.service`
At any time, you can check the status of the bot with
`$ systemctl status dbot.service` or read its log with `$ journalctl -u dbot.service` (make sure to scroll to the bottom by pressing `End`)

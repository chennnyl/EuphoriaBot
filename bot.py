import os
from dotenv import load_dotenv #Store token in .env file

import discord
from discord.ext import commands

import aiohttp
import json

import random
import re
	

def random_message(nicklist,plist,i=-1): #extract random message given pronouns + name
    noml = [a[0] for a in plist]
    objl = [a[1] for a in plist]
    genl = [a[2] for a in plist]
    verbl = [a[3] for a in plist]
    def nick():
    	return random.choice(nicklist)
    def nom():
        return random.choice(noml)
    def obj():
        return random.choice(objl)
    def gen():
        return random.choice(genl)


    def nom_verb(v=""):
        ind = random.randrange(len(noml))
        if v == "":
            return f"{noml[ind]} {verbl[ind]}"
        elif verbl[ind] == "are":
            return f"{noml[ind]} {v}"
        else:
            return f"{noml[ind]} {v}s"

    pot = [] #potential sentences
    with open("sentences.txt") as f:
        pot = f.read().split("\n")[:-1]

    if i == -1:
        uncompiled_fstring = random.choice(pot)
    else:
        uncompiled_fstring = pot[i]

    compiled_fstring = compile(uncompiled_fstring, "sentences", "eval") #make sure you vet f-strings! they shouldn't be able to execute arbitrary code


    return eval(compiled_fstring)




load_dotenv() #adds DISCORD_TOKEN and CREATORID to os environment variables

TOKEN = os.getenv('DISCORD_TOKEN')
CREATORID = int(os.getenv('CREATORID'))
BOTID = int(os.getenv('BOTID'))

bot = commands.Bot(command_prefix="!")
bot.remove_command("help") #redefines help variable from default

@bot.command(name="np") #try name/pronouns
async def try_multiple_pronouns(ctx, pronouns, name = ""):
	if name == "":
		nick = ""
		with open("usernames.json") as usernames: #extract names by ID from usernames.json
			userdat = json.load(usernames)
			if str(ctx.author.id) in userdat:
				nick = userdat[ctx.author.id].split(" ")
		if nick == "":
			nick = [ctx.author.display_name]
        	
	else:
		nick = name.split(" ")

	regMatch = re.findall("((\w+\/\w+\/\w+)( -\w+)*)+",pronouns) #split pronouns + flags
	pr = [a[1] for a in regMatch]
	pros = []
	for a in pr:
		try:
			split = a.split("/")
			pros.append(split)
			assert(len(split) == 3)
		except:
			await ctx.send("I had difficulty parsing those pronouns. Try again?")
			return

	fs = [a[2][2:] if a[2] else "" for a in regMatch]

	for i in range(len(fs)):
		a = fs[i]
		if "p" in a: #plural flag
			pros[i].append("are")
		else:
			pros[i].append("is")

	await ctx.send(random_message(nick,pros))

@bot.command(name="example", help="...not very helpful, for testing only") #output all sentences with example name + pronouns
@commands.has_permissions(manage_messages=True)
async def example_with_many_pronouns(ctx):
	ex_pros = [["he","him","his","is"],["she","her","her","is"],["they","them","their","are"],["xe","xem","xyr","is"],["per","per","pers","is"]]
	string = ""
	leng = 0
	with open("sentences.txt") as f:
		leng = len(f.read().split("\n")[:-1])
		for i in range(leng-1):
			string += random_message(["Example"],ex_pros,i)
			string += "\n"
	for i in range(len(string)//2000): #accommodate 2000 char limit
		await ctx.send(string[2000*i:2000*(i+1)])
	await ctx.send(string[2000*(len(string)//2000):])

@bot.command(name="resources") #list resources for users
async def resources(ctx,category=""):
	with open("resources.json") as resj:
		resources = json.load(resj) #place custom categories/resources in resources.json
	
	if category == "":
		await ctx.send(f"""I have a handful of resource categories to choose from. They are:
**{", ".join([a for a in resources])}**
Enter ```!resources [category]```to see the appropriate listing!

This list is by no means exhaustive: use !suggest if there are any resources you'd like to see added, within or outside of these categories!""")
	elif category not in resources:
		await ctx.send("I'm sorry, I don't have that category in my resources. Try again?")
	else:
		await ctx.send(resources[category])


@bot.command(name="suggest") #allow users to make suggestions directly to maintainer
async def send_suggestion(ctx,sugg=""):
	lynne = bot.get_user(CREATORID)

	if sugg == "":
		await ctx.send("You must include a suggestion to send!")
	elif " " not in sugg or len(sugg) < 15:
		await ctx.send("That seems awfully short... Make sure you put your suggestion in quotes!")
	else:
		await lynne.send(f"<@{ctx.author.id}>: {sugg}")
		await ctx.send("Your feedback has been sent!")

@bot.command(name="name") #set custom name for !np
async def name_user(ctx,name=""):
	with open("usernames.json","r+") as usernames:
		userdat = json.load(usernames)
		if name == "" and str(ctx.author.id) in userdat:
			await ctx.send(f"I have your name(s) as {', '.join(userdat[str(ctx.author.id)].split(' '))}.")
		elif name == "":
			await ctx.send("I don't have a name for you yet; set it with ```!name \"<your-name>\"```")
		else:
			if name == "delete":
				userdat.pop(str(ctx.author.id),None)
				await ctx.send(f"Okay, I've deleted my current name for you!")
			else:
				userdat[str(ctx.author.id)] = name
				await ctx.send(f"Okay, I've set your name(s) as {', '.join(name.split(' '))}!")
			usernames.seek(0)
			json.dump(userdat,usernames)
			usernames.truncate()
		
@bot.command(name="purge") #clear a channel; slow and buggy sometimes
@commands.has_permissions(manage_messages=True)
async def purge_chat(ctx):
	await ctx.channel.purge(limit=None)

@purge_chat.error #permissions error
async def purgeerror(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You don't have sufficient permissions to do that!")


@bot.command(name="plural") #just see the help command i'm sorry
async def pluraltree(ctx, comm, *sub):
	with open("plurals.json","r+") as plurals:
		data = json.load(plurals)
		if comm == "add": #add a member
			if len(sub) == 0:
				await ctx.send("You need to supply the display name of the member to add!")
			else:
				if str(ctx.author.id) in data:
					if sub[0] in [a["name"] for a in data[str(ctx.author.id)]]:
						await ctx.send(f"You already have a member named {sub[0]}!")
						return
				data[str(ctx.author.id)].append({"name":sub[0],"avatar":None,"prefix":"{","postfix":"}"})
				await ctx.send(f"Created a new member named {sub[0]} with default format of {{Message}}")
		elif comm == "delete": #delete a member
			if len(sub) == 0:
				await ctx.send("You need to supply the display name of the member to delete!")
			elif str(ctx.author.id) not in data:
				await ctx.send("You don't have any members in your system!")
			elif sub[0] not in [a["name"] for a in data[str(ctx.author.id)]]:
				await ctx.send(f"{sub[0]} isn't a member of your system!")
			else:
				index = [i for i in range(len(data[str(ctx.author.id)])) if data[str(ctx.author.id)][i]["name"] == sub[0]][0]
				del data[str(ctx.author.id)][index]
				await ctx.send(f"Deleted {sub[0]} from your system!")
		elif comm == "edit": #edit attribute of member
			if str(ctx.author.id) in data:
				if len(sub) > 2 or (sub[1] == "avatar"):
					if sub[0] not in [a["name"] for a in data[str(ctx.author.id)]]:
						await ctx.send(f"{sub[0]} isn't a member of your system!")
					elif sub[1] not in ["name","avatar","prefix","postfix"]:
						await ctx.send(f"I don't recognize the attribute {sub[1]}")
					else:
						index = [i for i in range(len(data[str(ctx.author.id)])) if data[str(ctx.author.id)][i]["name"] == sub[0]][0]
						if sub[1] == "avatar" and len(sub) == 2: #allow blank avatar for default Discord avatar
							data[str(ctx.author.id)][index]["avatar"] = None
						elif sub[1] == "prefix" and sub[2][0] == "!":
							await ctx.send(f"You can't use ! to start your proxy format!")
							return
						else:
							data[str(ctx.author.id)][index][sub[1]] = sub[2]
						await ctx.send(f"{sub[0]} modified successfully!")
				else:
					await ctx.send("You have to supply a member and attribute to edit as well as the new value!")
			else:
				await ctx.send("You don't have any members to edit!")
		elif comm == "list": #list all members
			if data[str(ctx.author.id)]:
				auth_plurals = data[str(ctx.author.id)]
				embed = discord.Embed(
					title=f"{ctx.author.display_name}'s System",
					color=ctx.author.color,
				)
				for i in auth_plurals:
					embed.add_field(
						name=i["name"],
						value=f"{i['prefix']}Message{i['postfix']}\n[Avatar]({i['avatar']})"
					)
				await ctx.send(embed=embed)
				
			else:
				await ctx.send("You don't have a system set up!")
		plurals.seek(0)
		json.dump(data,plurals)
		plurals.truncate()

@bot.command(name="rrole") #manage emoji/role pairings for !r message
@commands.has_permissions(manage_roles=True)
async def manage_reactions_for_roles(ctx, *emroles):
	if len(emroles) == 0:
		with open("roles.json","r+") as rolesjson:
			roledat = json.load(rolesjson)
			if str(ctx.guild.id) not in roledat:
				await ctx.send("This server doesn't have any assigned reactions!")
			elif len(roledat[str(ctx.guild.id)]) == 0:
				await ctx.send("This server doesn't have any assigned reactions!")
			else:
				await ctx.send("Current role pairs:\n" + "\n".join([f"{a}: {roledat[str(ctx.guild.id)][a]}" for a in roledat[str(ctx.guild.id)]])) #haha im so sorry
	elif len(emroles)%2 == 0:
		froles = []
		for r in emroles[1::2]:
			try:
				if r != "":
					froles.append(discord.utils.get(ctx.guild.roles, name=r)) 
					assert(froles[-1] is not None) #discord is too damn accomodating and i have to MAKE exceptions
			except:
				await ctx.send(f"Unrecognized role {r}!")
				return
		pairs = list(zip(emroles[0::2], emroles[1::2]))
		with open("roles.json","r+") as rolesjson:
			roledat = json.load(rolesjson)
			if str(ctx.guild.id) not in roledat:
				roledat[str(ctx.guild.id)] = {}
			for n in pairs:
				if n[1] == "":
					roledat[str(ctx.guild.id)].pop(n[0],None)
				else:
					roledat[str(ctx.guild.id)][n[0]] = n[1]
			rolesjson.seek(0)
			json.dump(roledat,rolesjson)
			rolesjson.truncate()
				
	else:
		await ctx.send("You need to have both an emoji and a role name each time!")


@manage_reactions_for_roles.error #permissions error
async def rolem_error(ctx, error):	
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You don't have sufficient privileges to do that!")
		
@bot.command(name="r") #create reactable message to assign roles
async def tempcommandlol(ctx,mess=""):
	if mess == "":
		await ctx.send("react")
	elif "REACT" not in mess.upper():
		await ctx.send("react")
	else:
		await ctx.send(mess)
		await ctx.message.delete()


@bot.command(name="help") #yeah
async def command_not_found(ctx,param=""): #these are hardcoded, don't feel like moving them to a json
	commlist = "\n**Available to all**```css\n[!help]: General help page\n[!name]: View and set a custom name the bot uses\n[!np]: Try out names/pronouns\n[!plural]: Modify members of a plural system (see help page)\n[!resources]: List various LGBTQ+ resources\n[!suggest]: Make suggestions to improve the bot```**Moderator Only**```css\n[!purge]: Clear the messages from a channel\n[!r]: Have the bot create a message users can react to to get roles\n[!rrole]: Manage emoji/role associations for !r```"
	helpstr = f"""Hi! I'm EuphoriaBot, a bot written by user Lynne designed to help users try new names and pronouns, as well as other functions! Here's a brief rundown of how to use me!
**Usage**
My commands are: {commlist} You can find out more by typing ```!help <command>```or simply ```!help``` to display this screen. Good luck, and remember, **you are valid!** <:enbyheart:685168658582077471> :heart: 

*P.S.: I'm always looking for improvement, please use !suggest if there's anything you'd like to see added!*"""
	namestr = """**!name Usage**```!name```to display your current name (if applicable) or ```!name delete``` to delete the current name entry or ```!name <your-name>```to set your name; you can set multiple names by quoting everything and putting spaces between each name; e.x. ```!name \"Lynne Ema\"```"""
	npstr = """**!np Usage:**```!np "<pronouns>" "[name]"```where a set of pronouns in quotes is required, while a name is optional (it'll use the name(s) set with !name, if it applicable, if not it'll use your server nick); if using multiple names, quotes are also required. Pronouns *must* include a set of three words like so:
```!np "he/him/his"``` or ```!np "she/her/her"```Pronouns that are grammatically plural, like they/them/their, can be indicated by putting "-p" at the end of the pronouns, like so:
```!np "they/them/their -p" Lynne```
You can try out several sets of pronouns or names at once!```!np "they/them/their -p she/her/her" "Lynne Ema"``` Finally, *make sure you omit the -s* in possessive pronouns that have it; e.x. "they/them/*their* -p" instead of "they/them/*theirs* -p"
And that's all there is to it! Good luck, and remember, **you are valid!** <:enbyheart:685168658582077471> :heart:
"""
	pluralstr = """**!plural Usage:**```!plural <add|delete|edit|list> <arguments>```Welcome to the **most complex command in the bot**! This allows you to interface with EuphoriaBot in order to automatically send your messages under several different names. The group of names you can send messages under is known as your **system**, and an individual name is known as a **member**. The first argument of !plural is the *subcommand* you want to use: each has its own special syntax, outlined below.```!plural add <name>```This command adds a member to your system with default specifications.```!plural delete <name>```This command removes a member from your system.```!plural edit <name> <name|avatar|prefix|postfix> <value>```This command lets you change the various attributes of a member of your system. **name** is the display name of the member, **avatar** is a URL to an image the member uses as its profile picture (you can leave blank for the default Discord profile picture), **prefix** is the string placed *before* a message to indicate the member, and **postfix** is the string placed *after* a message to inficate the member. It is recommended that the value (and the name, if longer than one word) is placed in quotes, like so:```!plural edit LynneA name "Lynne's First"``````!plural list```This is the simplest command -- it provides a card that lists the current members of your system, their message formats, and the links to their profile pictures."""
	suggeststr = """**!suggest Usage:**```!suggest "<suggestion>"```Your feedback will be sent via DM to creator Lynne!"""

	resourcestr = """**!resources Usage:**```!resources```for a list of categories and```!resources [category]```for the appropriate category. This command displays some links and resources for LGBTQ youth."""
	
	purgestr = """**!purge Usage:**```!purge```to clear the messages from a channel. Must be an Admin or Discord Moderator to use."""
	
	rrolestr = """**!rrole Usage:**```!rrole <emoji> \"role\" <emoji> \"role\"...<emoji> \"role\"```to tell the bot which emoji correspond to which roles when creating a message users can react to with !r```!rrole```to see the current emoji/role pairs the bot has registered"""
	
	rstr = """**!r Usage:**```!r \"string\"```to specify a string users can react to in order to get roles -- this string must somewhere contain the word \"react!\""""
	if param == "":
		await ctx.send(helpstr)
	elif param == "name":
		await ctx.send(namestr)
	elif param == "np":
		await ctx.send(npstr)
	elif param == "plural":
		await ctx.send(pluralstr)
	elif param == "resources":
		await ctx.send(resourcestr)
	elif param == "suggest":
		await ctx.send(suggeststr)
	elif param == "purge":
		await ctx.send(purgestr)
	elif param == "rrole":
		await ctx.send(rrolestr)
	elif param == "r":
		await ctx.send(rstr)
		


@bot.event #process proxy/members
async def on_message(msg):
	#read prefix, go through json file + extract name/avatar
	async def runHook(): #treated as separate command so we can break from if statement
		mess = msg.content
		with open("plurals.json") as plurals:
			plural_dat = json.load(plurals)
		try:
			user_plurals = plural_dat[str(msg.author.id)]
			match = [a for a in user_plurals if re.fullmatch(f"{re.escape(a['prefix'])}.+{re.escape(a['postfix'])}",mess)][0]
			tosend = re.match(f"{re.escape(match['prefix'])}(.+){re.escape(match['postfix'])}",mess)[1]
		except:
			return
		
		#make webhook requests
		head = {
			'Authorization': "Bot " + TOKEN,
			'Content-Type': 'application/json'
		}
		dat = json.dumps({
			"name":"EuphoriaHook",
			"avatar":None,
		})
		async with aiohttp.ClientSession() as session:
			channel_webhooks = {}
			async with session.get(f"https://discord.com/api/channels/{msg.channel.id}/webhooks",headers={'Authorization': "Bot " + TOKEN}) as web:
				channel_webhooks = await web.json()
			euphoriaHook = None
			if "EuphoriaHook" not in [a["name"] for a in channel_webhooks]: #create webhook
				async with session.post(f"https://discord.com/api/channels/{msg.channel.id}/webhooks",data=dat,headers=head) as resp:
					euphoriaHook = await resp.json()
			else: #use preexisting webhook
				async with session.get(f"https://discord.com/api/webhooks/{[a['id'] for a in channel_webhooks if a['name']=='EuphoriaHook'][0]}",headers={'Authorization': "Bot " + TOKEN}) as resp:
					euphoriaHook = await resp.json()
			

			hookID = euphoriaHook["id"]
			hookToken = euphoriaHook["token"]
				
				
			msgdata = json.dumps({
				"content":tosend,
				"username":match["name"],
				"avatar_url":match["avatar"],
				})
			posted = await session.post(f"https://discord.com/api/webhooks/{hookID}/{hookToken}",data=msgdata,headers=head) #post to webhook
			await msg.delete()
	await runHook()	
	await bot.process_commands(msg)


@bot.event
async def on_raw_reaction_add(payload): #process emoji 
	emoji, guildid = payload.emoji, payload.guild_id
	user, message =  bot.get_guild(guildid).get_member(payload.user_id), await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
	if message.author.id == BOTID and "REACT" in message.content.upper():
		with open("roles.json") as roles:
			roledat = json.load(roles)
			if str(guildid) in roledat:
				if str(emoji) in roledat[str(guildid)]:
					await user.add_roles(discord.utils.get(bot.get_guild(guildid).roles, name=roledat[str(guildid)][str(emoji)])) 

@bot.event
async def on_raw_reaction_remove(payload): #process emoji
	emoji, guildid = payload.emoji, payload.guild_id
	user, message =  bot.get_guild(guildid).get_member(payload.user_id), await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
	if message.author.id == BOTID and "REACT" in message.content.upper():
		with open("roles.json") as roles:
			roledat = json.load(roles)
			if str(guildid) in roledat:
				if str(emoji) in roledat[str(guildid)]:
					await user.remove_roles(discord.utils.get(bot.get_guild(guildid).roles, name=roledat[str(guildid)][str(emoji)])) 


	
bot.run(TOKEN)

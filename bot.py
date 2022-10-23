import os #Used with dotenv
from dotenv import load_dotenv #Store token in .env file

import discord #guess what this is used for i dare you
from discord.ext import commands

import aiohttp #make async requests 
import asyncio #also make async requests
import json #load from files in cfg

import random #get random message
import re #parse pronoun commands

import time #store purge times

gContext = None

def getlang(ident,context=gContext): #get string stored in lang.json
	with open("cfg/lang.json") as langf:
		dat = json.load(langf)
		if context:
			with open("cfg/userlang.json") as userlang:
				udat = json.load(userlang)
			
			if str(context.author.id) in udat:
				lang = udat[str(context.author.id)]
			else:
				lang = "en"
		else:
			lang = "en"
		
		toget = dat
		for i in ident.split("."): #navigate down lang string (e.g., "success.setting.settingreq.joinMessage")
			toget = toget[i]
		if lang in toget:
			toget = toget[lang]
		else:
			toget = toget["en"]
			
		return eval(compile(toget, "langfile", "eval"))
	

def random_message(nicklist,plist,i=-1): #extract random message given pronouns (list of 4-item lists) + names (list of strings)
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

@bot.event
async def on_ready():
	try:
		version = getlang('version')
	except:
		version = "(pre-1.2.1)"
	await bot.change_presence(activity=discord.Game(f"EuphoriaBot {version}"))
	print("Connected to Discord!")


@bot.command(name="np") #try name/pronouns
async def try_multiple_pronouns(ctx, pronouns, name = ""):
	if name == "":
		nick = ""
		with open("cfg/usernames.json") as usernames: #extract names by ID from usernames.json
			userdat = json.load(usernames)
			if str(ctx.author.id) in userdat:
				nick = userdat[str(ctx.author.id)].split(" ")
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
			await ctx.send(getlang("error.np.pronounparse",ctx))
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
	with open("cfg/resources.json") as resj:
		resources = json.load(resj) #place custom categories/resources in resources.json
	
	if category == "":
		await ctx.send(getlang("success.resource.catlisting",ctx) + f"**{', '.join([a for a in resources])}**")
	elif category not in resources:
		await ctx.send(getlang("error.resource.noresource",ctx))
	else:
		await ctx.send(resources[category])


@bot.command(name="suggest") #allow users to make suggestions directly to maintainer
async def send_suggestion(ctx,sugg=""):
	lynne = bot.get_user(CREATORID)

	if sugg == "":
		await ctx.send(getlang("error.suggest.nosuggestion",ctx))
	elif " " not in sugg or len(sugg) < 15:
		await ctx.send(getlang("error.suggest.length",ctx))
	else:
		await lynne.send(f"<@{ctx.author.id}>: {sugg}")
		await ctx.send(getlang("success.suggest.sent",ctx))

@bot.command(name="name") #set custom name for !np
async def name_user(ctx,name=""):
	with open("cfg/usernames.json","r+") as usernames:
		userdat = json.load(usernames)
		if name == "" and str(ctx.author.id) in userdat:
			await ctx.send(getlang("success.name.current",ctx) + ', '.join(userdat[str(ctx.author.id)].split(' ')))
		elif name == "":
			await ctx.send(getlang("error.name.noname",ctx))
		else:
			if name == "delete":
				userdat.pop(str(ctx.author.id),None)
				await ctx.send(getlang("success.name.delete", ctx))
			else:
				userdat[str(ctx.author.id)] = name
				await ctx.send(getlang("success.name.set",ctx) + ', '.join(name.split(' ')))
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
		await ctx.send(getlang("error.priv",ctx))
		
@bot.command(name="addpurge") #add automatic purge to a channel specified in days
@commands.has_permissions(manage_messages=True)
async def addpurge(ctx, interval=0):
	fullInt = 86400 * float(interval)
	with open("cfg/purge.json","r+") as purgeFile:
		purgeDat = json.load(purgeFile)
		if interval == 0:
			purgeDat.pop(str(ctx.channel.id), None)
		else:
			purgeDat[str(ctx.channel.id)] = {"interval":fullInt, "start":time.time()}
		purgeFile.seek(0)
		json.dump(purgeDat, purgeFile)
		purgeFile.truncate()
	
@addpurge.error
async def addpurgeerror(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(getlang("error.priv",ctx))


async def purgeAutomatedChannels(bot): #purge channels with an automatic set
	await bot.wait_until_ready()

	
	async def purgeChannel(channel):
		with open("cfg/purge.json") as purgeFile:
			purgeDat = json.load(purgeFile)
			interval = int(purgeDat[str(channel.id)]["interval"])
			begin = int(purgeDat[str(channel.id)]["start"])

			if int(time.time() - begin)%interval == 0: #check current time against set time and interval
				await channel.purge(limit=None)
	while not bot.is_closed(): #perform every second
		with open("cfg/purge.json") as purgeFile:
			purgeDat = json.load(purgeFile)
			

			toPurge = [bot.get_channel(int(a)) for a in purgeDat]
			
			for channel in toPurge:
				if channel is not None: await purgeChannel(channel)
		await asyncio.sleep(1)
			
@bot.command(name="purget") #check time left in purge
async def purgetimercheck(ctx):
	with open("cfg/purge.json") as purgeFile:
		purgeDat = json.load(purgeFile)
		try:
			interval = int(purgeDat[str(ctx.channel.id)]["interval"])
		except KeyError:
			await ctx.send(getlang("error.purget.notfound",ctx))
			return
		begin = int(purgeDat[str(ctx.channel.id)]["start"])
		await ctx.send(interval - (int(time.time() - begin)%interval))
		


@bot.command(name="plural") #just see the help command i'm sorry; better yet, uninstall the bot and find something better
async def pluraltree(ctx, comm, *sub):
	with open("cfg/plurals.json","r+") as plurals:
		data = json.load(plurals)
		if comm == "add": #add a member
			if len(sub) == 0:
				await ctx.send(getlang("error.plural.add.display",ctx))
			else:
				if str(ctx.author.id) in data:
					if sub[0] in [a["name"] for a in data[str(ctx.author.id)]]:
						await ctx.send(getlang("error.plural.add.existingmember",ctx))
						return
				else:
					data[str(ctx.author.id)] = []
				
				data[str(ctx.author.id)].append({"name":sub[0],"avatar":None,"prefix":"{","postfix":"}"})
				await ctx.send(getlang("success.plural.add",ctx))
		elif comm == "delete": #delete a member
			if len(sub) == 0:
				await ctx.send(getlang("error.plural.delete.display",ctx))
			elif str(ctx.author.id) not in data:
				await ctx.send(getlang("error.plural.delete.nomember",ctx))
			elif sub[0] not in [a["name"] for a in data[str(ctx.author.id)]]:
				await ctx.send(getlang("error.plural.delete.badmember",ctx))
			else:
				index = [i for i in range(len(data[str(ctx.author.id)])) if data[str(ctx.author.id)][i]["name"] == sub[0]][0]
				del data[str(ctx.author.id)][index]
				await ctx.send(getlang("success.plural.delete",ctx))
		elif comm == "edit": #edit attribute of member
			if str(ctx.author.id) in data:
				if len(sub) > 2 or (sub[1] == "avatar"):
					if sub[0] not in [a["name"] for a in data[str(ctx.author.id)]]:
						await ctx.send(getlang("error.plural.delete.badmember",ctx))
					elif sub[1] not in ["name","avatar","prefix","postfix"]:
						await ctx.send(getlang("error.plural.edit.badattribute",ctx))
					else:
						index = [i for i in range(len(data[str(ctx.author.id)])) if data[str(ctx.author.id)][i]["name"] == sub[0]][0]
						if sub[1] == "avatar" and len(sub) == 2: #allow blank avatar for default Discord avatar
							data[str(ctx.author.id)][index]["avatar"] = None
						elif sub[1] == "prefix" and sub[2][0] == "!":
							await ctx.send(getlang("error.plural.edit.badprefix",ctx))
							return
						else:
							data[str(ctx.author.id)][index][sub[1]] = sub[2]
						await ctx.send(getlang("success.plural.edit",ctx))
				else:
					await ctx.send(getlang("error.plural.edit.malformed",ctx))
			else:
				await ctx.send(getlang("error.plural.edit.nomember",ctx))
		elif comm == "list": #list all members
			if data[str(ctx.author.id)]:
				auth_plurals = data[str(ctx.author.id)]
				embed = discord.Embed(
					title=getlang("success.plural.list.title",ctx),
					color=ctx.author.color,
				)
				for i in auth_plurals:
					embed.add_field(
						name=i["name"],
						value=f"{i['prefix']}Message{i['postfix']}\n[Avatar]({i['avatar']})"
					)
				await ctx.send(embed=embed)
				
			else:
				await ctx.send(getlang("error.plural.list.nosystem",ctx))
		plurals.seek(0)
		json.dump(data,plurals)
		plurals.truncate()

@bot.command(name="rrole") #manage emoji/role pairings for !r message
@commands.has_permissions(manage_roles=True)
async def manage_reactions_for_roles(ctx, *emroles):
	if len(emroles) == 0:
		with open("cfg/roles.json","r+") as rolesjson:
			roledat = json.load(rolesjson)
			if str(ctx.guild.id) not in roledat:
				await ctx.send(getlang("error.rrole.noreaction",ctx))
			elif len(roledat[str(ctx.guild.id)]) == 0:
				await ctx.send(getlang("error.rrole.noreaction",ctx))
			else:
				await ctx.send(getlang("success.rrole.pairs",ctx) + "\n".join([f"{a}: {roledat[str(ctx.guild.id)][a]}" for a in roledat[str(ctx.guild.id)]])) #haha im so sorry
	elif len(emroles)%2 == 0:
		froles = []
		for r in emroles[1::2]:
			try:
				if r != "":
					froles.append(discord.utils.get(ctx.guild.roles, name=r)) 
					assert(froles[-1] is not None) #discord is too damn accomodating and i have to MAKE exceptions
			except:
				await ctx.send(getlang("error.rrole.badrole",ctx) +f"{r}!")
				return
		pairs = list(zip(emroles[0::2], emroles[1::2]))
		with open("cfg/roles.json","r+") as rolesjson:
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
		await ctx.send(getlang("error.rrole.malformed",ctx))


@manage_reactions_for_roles.error #permissions error
async def rolem_error(ctx, error):	
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(getlang("error.priv",ctx))
		
@bot.command(name="r") #create reactable message to assign roles
@commands.has_permissions(manage_messages=True)
async def tempcommandlol(ctx,mess=""):
	if mess == "" or "REACT" not in mess.upper():
		await ctx.send(getlang("error.r.malformed"))
	else:
		await ctx.send(mess)
		await ctx.message.delete()

@tempcommandlol.error
async def rerror(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(getlang("error.priv",ctx))

@bot.command(name="setting") #change global variables
@commands.has_permissions(administrator=True)
async def settingsMod(ctx, setting, value=""):
	settings = ["joinRestrict","joinMessage","reset"]
	if setting not in settings:
		await ctx.send(getlang("error.setting.nosetting",ctx))
		return
	with open("cfg/settings.json","r+") as settingf:
		dat = json.load(settingf)
		if str(ctx.guild.id) not in dat:
			dat[str(ctx.guild.id)] = {"joinRestrict":"FALSE", "joinMessage":""}
		if value == "":
			await ctx.send(getlang("success.setting.currentval",ctx) + dat[str(ctx.guild.id)][setting])
		else:
			if setting == "joinRestrict": #add NEWBIE role to joining users
				if value.upper() not in ["TRUE","FALSE"]:
					await ctx.send(getlang("error.setting.badvalue",ctx))
					return
				else:
					if value.upper() == "TRUE": #TODO: rework this to allow custom new role and remove landing zone restriction
						if discord.utils.get(ctx.guild.channels, name="landing-zone") == None or discord.utils.get(ctx.guild.roles, name="Newbie") == None:
							await ctx.send(getlang("error.setting.settingreq.joinRestrict",ctx))
							return
					dat[str(ctx.guild.id)]["joinRestrict"] = value.upper()
					await ctx.send(":white_check_mark: " + getlang("success.setting.currentval",ctx) + dat[str(ctx.guild.id)]["joinRestrict"])
			elif setting == "joinMessage": #send message to all joining users
				if value.strip() == "":
					dat[str(ctx.guild.id)]["joinMessage"] = ""
				else:
					if len(value) > 2000:
						await ctx.send(getlang("error.setting.settingreq.joinMessage",ctx))
						return
					dat[str(ctx.guild.id)]["joinMessage"] = value
				await ctx.send(getlang("success.setting.short",ctx))

			elif setting == "reset": #set a setting to its default value
				if value not in settings:
					await ctx.send(getlang("error.setting.nosetting",ctx))
				else:
					defaults = {
						"joinRestrict": "FALSE",
						"joinMessage": ""
					}

					dat[str(ctx.guild.id)][value] = defaults[value]

		settingf.seek(0)
		json.dump(dat,settingf)
		settingf.truncate()

@settingsMod.error
async def settingerror(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(getlang("error.priv",ctx))


@bot.command(name="lang") #set user language
async def langset(ctx,lang):
	with open("cfg/userlang.json","r+") as langf:
		dat = json.load(langf)
		if lang in ["es","de","en"]:
			dat[str(ctx.author.id)] = lang
			langf.seek(0)
			json.dump(dat,langf)
			langf.truncate()
			await ctx.send(getlang("success.lang",ctx))
		else:
			await ctx.send(getlang("error.missinglang"))


@bot.command(name="help") #take a guess what it does i dare you
async def command_not_found(ctx,param=""):

	if param == "":
		gContext = ctx
		await ctx.send(getlang("help.help",ctx))
		gContext = None
	elif param == "lang":
		await ctx.send(getlang("help.lang",ctx))
	elif param == "name":
		await ctx.send(getlang("help.name",ctx))
	elif param == "np":
		await ctx.send(getlang("help.np",ctx))
	elif param == "plural":
		await ctx.send(getlang("help.plural",ctx))
	elif param == "resources":
		await ctx.send(getlang("help.resource",ctx))
	elif param == "suggest":
		await ctx.send(getlang("help.suggest",ctx))
	elif param == "addpurge":
		await ctx.send(getlang("help.addpurge", ctx))
	elif param == "purge":
		await ctx.send(getlang("help.purge",ctx))
	elif param == "purget":
		await ctx.send(getlang("help.purget", ctx))
	elif param == "rrole":
		await ctx.send(getlang("help.rrole",ctx))
	elif param == "r":
		await ctx.send(getlang("help.r",ctx))
	elif param == "setting":
		await ctx.send(getlang("help.setting",ctx))
		


@bot.event #process proxy/members
async def on_message(msg):
	#read prefix, go through json file + extract name/avatar
	async def runHook(): #treated as separate command so we can break from if statement
		mess = msg.content
		with open("cfg/plurals.json") as plurals:
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
	if message.author.id == BOTID and "REACT" in message.content.upper() and message.content != "Bad message format! Include the word 'react!'" and message.content[-1] != "'":
		with open("cfg/roles.json") as roles:
			roledat = json.load(roles)
			if str(guildid) in roledat:
				if str(emoji) in roledat[str(guildid)]:
					await user.add_roles(discord.utils.get(bot.get_guild(guildid).roles, name=roledat[str(guildid)][str(emoji)])) 

@bot.event
async def on_raw_reaction_remove(payload): #process emoji
	emoji, guildid = payload.emoji, payload.guild_id
	user, message =  bot.get_guild(guildid).get_member(payload.user_id), await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
	if message.author.id == BOTID and "REACT" in message.content.upper() and message.content != "Bad message format! Include the word 'react!'" and message.content[-1] != "'":
		with open("cfg/roles.json") as roles:
			roledat = json.load(roles)
			if str(guildid) in roledat:
				if str(emoji) in roledat[str(guildid)]:
					await user.remove_roles(discord.utils.get(bot.get_guild(guildid).roles, name=roledat[str(guildid)][str(emoji)])) 

@bot.event #assign role, send message to new users
async def on_member_join(member):
	with open("cfg/settings.json") as settingf:
		dat = json.load(settingf)

		if str(member.guild.id) not in dat or dat[str(member.guild.id)]["joinRestrict"] == "FALSE":
			return
		else:
			await member.add_roles(discord.utils.get(bot.get_guild(member.guild.id).roles, name="Newbie")) 
		
		if len(dat[str(member.guild.id)]["joinMessage"]) > 0:
			await member.send(dat[str(member.guild.id)]["joinMessage"])

		

bot.loop.create_task(purgeAutomatedChannels(bot))
bot.run(TOKEN)
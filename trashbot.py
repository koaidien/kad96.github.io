# Work with Python 3.6 
# This bot work for only ONE server per run even if it can do in mutiple servers

from discord.ext import commands
import discord
import datetime, time
import json, configparser
import aiohttp, asyncio
import random, schedule
import sqlite3

BOT_PREFIX = ("?", "!")
CONFIGFILE = "bot.ini"
TIMEDELTA = datetime.timedelta(hours=7)

TOKEN = 'NTY1OTUwOTgxODk2OTI5Mjgw.XK95nA.ItJ0LfvdaUt1kBIsOXOLFZBwUSE'
ALERT_CHANNEL = None
GUILD = None
TODAY = None

TODAY_ACTIVATED = []

DOW_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DOW_vi = ["thứ hai", "thứ ba", "thứ tư", "thứ năm", "thứ sáu", "thứ bảy", "chủ nhật"]
DOW_e = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
NUMBERS_emo =  ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
NUMBERS_vi =  ['không','một','hai','ba','bốn','năm','sáu','bảy','tám','chín','mười']

client = commands.Bot(command_prefix=BOT_PREFIX)
config = configparser.RawConfigParser()

async def wait_for(dt):
    # sleep until the specified datetime
    while True:
        now = datetime.datetime.now()
        remaining = (dt - now).total_seconds()
        if remaining < 86400:
            break
        # asyncio.sleep doesn't like long sleeps, so don't sleep more
        # than a day at a time
        await asyncio.sleep(86400)
    await asyncio.sleep(remaining)


async def run_at(dt, coro):
    await wait_for(dt)
    return await coro


async def checker():
	await client.wait_until_ready()
	global GUILD, TODAY_ACTIVATED, TODAY
	conn = sqlite3.connect('checker.db')
	c = conn.cursor()
	if TODAY_ACTIVATED != []:
		c.executemany("UPDATE Users SET last_active=? WHERE id=?",TODAY_ACTIVATED)
	conn.commit()
	print("Updated today data.")
	# not sayin anythin
	mentions = ""
	users = c.execute("SELECT * FROM Users WHERE last_active is NULL").fetchall()
	for user in users:
		mentions += client.get_user(user[0]).mention
	await ALERT_CHANNEL.send("Nói gì đi các người, tôi có công việc phải làm đấy.\n"+mentions)
	# not around for 3 days
	mentions = ""
	users = c.execute("SELECT * FROM Users WHERE last_active AND DATEDIFF(day,last_active,?)=3",TODAY).fetchall()
	for user in users:
		mentions += client.get_user(user[0]).mention
	await ALERT_CHANNEL.send("Đã 3 ngày rồi đó, các cậu đâu rồi? :frowning2:\n"+mentions)
	# not around for 7 days
	mentions = ""
	users = c.execute("SELECT * FROM Users WHERE last_active AND DATEDIFF(day,last_active,?)=7",TODAY).fetchall()
	for user in users:
		mentions += client.get_user(user[0]).mention
	await ALERT_CHANNEL.send("Đã một tuần tớ không thấy các cậu trả lời. Vậy đành thôi tình ta chia xa :cry:\n"+mentions)
	# ban them here
	
	conn.close()
	TODAY = datetime.datetime.combine(datetime.datetime.now(), datetime.datetime.min.time())
	client.loop.create_task(run_at(TODAY+datetime.timedelta(days=1),checker()))
	
	
@client.command(pass_context=True)
async def bắt_đầu_kiểm_soát(ctx):
	await client.wait_until_ready()
	global GUILD, TODAY
	conn = sqlite3.connect('checker_%d.db'%GUILD.id)
	print("Connected to checker_%d.db"%GUILD.id)
	c = conn.cursor()
	try:
		# Create table
		c.execute('''CREATE TABLE Users (
			id          BIGINT   NOT NULL PRIMARY KEY,
			name        STRING   NOT NULL,
			last_active DATETIME DEFAULT NULL);''')
		conn.commit()
		print("Users table created!")
	except: pass
	for u in GUILD.members:
		try:
			c.execute("INSERT INTO Users VALUES (?,?,NULL)",(u.id,u.name))
			print("Assigned "+u.name)
		except: pass
	conn.commit()
	conn.close()
	await ALERT_CHANNEL.send("@everyone: Bot kiểm duyệt nội dung đã đi vào hoạt động!")
	client.loop.create_task(run_at(TODAY+datetime.timedelta(days=1),checker()))
	
@client.event
async def on_ready():
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='the World Burn!'))
	print("Call me trashtalker 8-}")
	global TODAY, ALERT_CHANNEL,GUILD
	TODAY = datetime.datetime.combine(datetime.datetime.now(), datetime.datetime.min.time())
	if config.read(CONFIGFILE) != []:
		cfg = config[config.sections()[0]]
		GUILD = client.get_guild(int(cfg.get('GUILD_ID')))
		ALERT_CHANNEL = GUILD.get_channel(int(cfg.get('ALERT_CHANNEL_ID')))

@client.command(pass_context=True)
async def đặt_kênh_thông_báo(ctx):
	global ALERT_CHANNEL,GUILD
	GUILD = ctx.guild
	ALERT_CHANNEL = ctx.message.channel
	if not config.has_section(GUILD.name): config.add_section(GUILD.name)
	config[GUILD.name]['GUILD_ID'] = str(GUILD.id)
	config[GUILD.name]['ALERT_CHANNEL_ID'] = str(ctx.message.channel.id)
	config.write(open(CONFIGFILE,'w'))
	await ALERT_CHANNEL.send("Đã đăng ký kênh thông báo!")

@client.event
async def on_message(message):
	global TODAY_ACTIVATED
	if message.author.id not in TODAY_ACTIVATED:
		TODAY_ACTIVATED += [[TODAY, message.author.id]]
	if "Hello" == message.content.lower():
		await message.channel.send("lô lô con c*c")
	if "a lô" == message.content.lower():
		await message.channel.send("Dcmm thích cà khịa không?")
	await client.process_commands(message)
	
client.run(TOKEN)

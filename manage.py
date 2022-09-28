import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import utils

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="?help"), case_insensitive = True)

@client.event
async def on_ready():
    print('Bot Deployed!')

@client.command()
async def ping(ctx):
    await ctx.send('Pong!')

# FETCHLDAP
@client.command()
async def fetchldap(ctx):
    msg = await ctx.reply('_Fetching LDAP Data:_ **0%**')
    await utils.fetch_ldap(msg)



load_dotenv()
client.run(os.getenv('BOT_TOKEN'))
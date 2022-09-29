import discord
from discord.ext import commands
import datetime, os
from dotenv import load_dotenv
import utils

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="?help"), case_insensitive = True)

@client.event
async def on_ready():
    print('Bot Deployed!')

@client.event
async def on_member_join(member):
    if member.guild.id == 871982588422656031:
        channel = client.get_channel(871983126488948767)
        bot_commands = client.get_channel(872364635637035028)
        await channel.send(f'Hey {member.mention}, welcome to **{member.guild.name}**! Please go to {bot_commands.mention} and use `?set <kerberos>` to get your roles!')

@client.event
async def on_member_remove(member):
    if member.guild.id == 871982588422656031:
        channel = client.get_channel(871983126488948767)
        await channel.send(f'**{member.name}#{member.discriminator}** just left the server')

@client.event
async def on_message_delete(message):
    if message.author.bot:
        return
    if message.guild.id == 871982588422656031:
        async for entry in message.guild.audit_logs(limit=1,action=discord.AuditLogAction.message_delete):
            deleter = entry.user
        if deleter.bot:
            return
        channel = client.get_channel(1025001667734818916)
        embed = discord.Embed( 
            description=f"**Message sent by {message.author.mention} deleted in {message.channel.mention}** \n {message.content}", 
            color=0xFE4712,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=f"{deleter.name}#{deleter.discriminator}", icon_url=deleter.avatar)
        embed.set_footer(text=f"Author: {message.author.id} | Message ID: {message.id}")
        await channel.send(embed=embed)

@client.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    if before.guild.id == 871982588422656031:
        channel = client.get_channel(1025001667734818916)
        embed = discord.Embed(
            description=f"**Message edited in {before.channel.mention}** [Jump to Message]({before.jump_url})",
            color=0x3480D5,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        embed.set_author(name=f"{before.author.name}#{before.author.discriminator}", icon_url=before.author.avatar)
        embed.set_footer(text=f"User ID: {before.author.id}")
        await channel.send(embed=embed)

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
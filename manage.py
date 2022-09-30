import discord
from discord.ext import commands
import datetime, json, os
from dotenv import load_dotenv
import mess_management, kerberos_management, utils

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
        if not member.bot:
            await channel.send(f'Hey {member.mention}, welcome to **{member.guild.name}**! Please go to {bot_commands.mention} and use `?set <kerberos>` to get your roles!')
        channel = client.get_channel(1025010614948606073)
        embed = discord.Embed(
            description=f"{member.mention} {member.name}#{member.discriminator}",
            color=0x42B582,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=f"Member Joined")
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)


@client.event
async def on_member_remove(member):
    if member.guild.id == 871982588422656031:
        channel = client.get_channel(871983126488948767)
        if not member.bot:
            await channel.send(f'**{member.name}#{member.discriminator}** just left the server')
        channel = client.get_channel(1025010614948606073)
        embed = discord.Embed(
            description=f"{member.mention} {member.name}#{member.discriminator}",
            color=0xFE4712,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=f"Member Left")
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

@client.event
async def on_member_update(before, after):
    if before.guild.id == 871982588422656031:
        channel = client.get_channel(1025010614948606073)
        if len(before.roles) != len(after.roles):
            async for entry in before.guild.audit_logs(limit=1,action=discord.AuditLogAction.member_role_update):
                editor = entry.user
            embed = discord.Embed(
                color=0x3480D5,
                timestamp=datetime.datetime.now()
            )
            embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.avatar)
            embed.set_footer(text=f"ID: {before.id}")
            if len(before.roles) < len(after.roles):
                if editor == client.user:
                    return
                new_role = next(role for role in after.roles if role not in before.roles)
                embed.description = f"**{before.mention} was given the `{new_role.name}` role**"
            else:
                old_role = next(role for role in before.roles if role not in after.roles)
                embed.description = f"**{before.mention} was removed from the `{old_role.name}` role**"
        elif before.nick != after.nick:
            embed = discord.Embed(
                description=f"**{before.mention} nickname changed**",
                color=0x3480D5,
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Before", value=before.nick, inline=False)
            embed.add_field(name="After", value=after.nick, inline=False)
            embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.avatar)
            embed.set_footer(text=f"ID: {before.id}")
        await channel.send(embed=embed)

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
        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar)
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

# Kerberos Related Commands

@client.command()
async def set(ctx, kerberos):
    if not ctx.guild:
        guild = client.get_guild(871982588422656031)
        await ctx.reply(f"Please set your kerberos in **{guild.name}** \nhttps://discord.gg/SaAKrjCCMq")
        return
    if ctx.guild.id == 871982588422656031:
        if len(kerberos) == 11:
            kerberos = kerberos[4:7] + kerberos[2:4] + kerberos[7:]
            print(kerberos)
        kerberos = kerberos.lower()
        if kerberos in utils.kerberos:
            msg = await ctx.reply("Setting your kerberos...")
            await kerberos_management.set(ctx, kerberos, client, msg, ctx.message.author)
        else:
            await ctx.reply('The Kerberos ID you entered is invalid. Please try again.')
    else:
        guild = client.get_guild(871982588422656031)
        await ctx.reply(f"Please set your kerberos in **{guild.name}** \nhttps://discord.gg/SaAKrjCCMq")

@client.command()
async def mess(ctx, *args):
    discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
    if str(ctx.message.author.id) not in discord_ids:
        await ctx.reply("Please set your kerberos using `?set <kerberos>` command before using this command!")
        return
    await mess_management.send_menu(ctx, client, args)



@client.command()
@commands.has_role(872326201132339210)
async def edit(ctx, user: discord.Member, kerberos):
    if not ctx.guild:
        guild = client.get_guild(871982588422656031)
        await ctx.reply(f"Please edit kerberos in **{guild.name}** \nhttps://discord.gg/SaAKrjCCMq")
        return
    if ctx.guild.id == 871982588422656031:
        if len(kerberos) == 11:
            kerberos = kerberos[4:7] + kerberos[2:4] + kerberos[7:]
            print(kerberos)
        kerberos = kerberos.lower()
        if kerberos in utils.kerberos:
            msg = await ctx.reply(f"Updating kerberos for {user.name}#{user.discriminator}")
            await kerberos_management.set(ctx, kerberos, client, msg, user)
        else:
            await ctx.reply('The Kerberos ID you entered is invalid. Please try again.')
    else:
        guild = client.get_guild(871982588422656031)
        await ctx.reply(f"Please edit kerberos in **{guild.name}** \nhttps://discord.gg/SaAKrjCCMq")



# Mess Managers

@client.command()
@commands.has_any_role(872326201132339210, 872381019553153077, 1025315061427867738)
async def updatemenu(ctx, hostel, day, meal, *, menu):
    if not ctx.guild:
        guild = client.get_guild(871982588422656031)
        await ctx.reply(f"Please update mess menu in **{guild.name}** \nhttps://discord.gg/SaAKrjCCMq")
        return
    if ctx.guild.id == 871982588422656031:
        if hostel.title() in utils.hostels:
            hostel_role = discord.utils.get(ctx.guild.roles, name=hostel.title())
            manager_role = discord.utils.get(ctx.guild.roles, id=872326201132339210)
            admin_role = discord.utils.get(ctx.guild.roles, id=872381019553153077)
            if hostel_role not in ctx.author.roles and manager_role not in ctx.author.roles and admin_role not in ctx.author.roles:
                await ctx.reply("You don't belong to this hostel.")
                return
            if day[:3].lower() in utils.days:
                if meal.lower() in utils.meals:
                    await mess_management.update_menu(ctx, client, hostel.title(), day[:3].title(), meal.title(), menu)
                else:
                    await ctx.reply(f"Invalid meal. Please enter one of the following: **{', '.join(utils.meals)}**")
            else:
                await ctx.reply(f"Invalid day. Please enter one of the following: **{', '.join(utils.days)}**")
        else:
            await ctx.reply(f"Invalid hostel")
    else:
        guild = client.get_guild(871982588422656031)
        await ctx.reply(f"Please update mess menu in **{guild.name}** \nhttps://discord.gg/SaAKrjCCMq")

@client.command()
@commands.has_any_role(872326201132339210, 872381019553153077, 1025315061427867738)
async def updatetime(ctx, hostel, day, meal, *, time):
    if not ctx.guild:
        guild = client.get_guild(871982588422656031)
        await ctx.reply(f"Please update mess menu in **{guild.name}** \nhttps://discord.gg/SaAKrjCCMq")
        return
    if ctx.guild.id == 871982588422656031:
        if hostel.title() in utils.hostels:
            hostel_role = discord.utils.get(ctx.guild.roles, name=hostel.title())
            manager_role = discord.utils.get(ctx.guild.roles, id=872326201132339210)
            admin_role = discord.utils.get(ctx.guild.roles, id=872381019553153077)
            if hostel_role not in ctx.author.roles and manager_role not in ctx.author.roles and admin_role not in ctx.author.roles:
                await ctx.reply("You don't belong to this hostel.")
                return
            if day[:3].lower() in utils.days:
                if meal.lower() in utils.meals:
                    await mess_management.update_time(ctx, client, hostel.title(), day[:3].title(), meal.title(), time)
                else:
                    await ctx.reply(f"Invalid meal. Please enter one of the following: **{', '.join(utils.meals)}**")
            else:
                await ctx.reply(f"Invalid day. Please enter one of the following: **{', '.join(utils.days)}**")
        else:
            await ctx.reply(f"Invalid hostel")
    else:
        guild = client.get_guild(871982588422656031)
        await ctx.reply(f"Please update mess menu in **{guild.name}** \nhttps://discord.gg/SaAKrjCCMq")

# FETCHLDAP
@client.command()
async def fetchldap(ctx):
    msg = await ctx.reply('_Fetching LDAP Data:_ **0%**')
    await utils.fetch_ldap(msg)


utils.reload()
load_dotenv()
client.run(os.getenv('BOT_TOKEN'))
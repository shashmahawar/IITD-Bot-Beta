import discord
from discord.ext import commands
import asyncio, datetime, json, os, typing
from dotenv import load_dotenv
import course_management, mess_management, moderation, kerberos_management, utils

intents = discord.Intents.all()
client = commands.Bot(command_prefix='?', intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="?help"), case_insensitive = True)
client.remove_command('help')

log = []

@client.event
async def on_ready():
    print('Bot Deployed!')

async def checkspam(message):
    if isinstance(message.channel, discord.channel.DMChannel):
        return False
    if discord.utils.get(message.guild.roles, id=958004057623126066) in message.author.roles:
        return False
    if message.content == "" or message.author.bot:
        return False
    log.append(message)
    if len(log) > 25:
        log.pop(0)
    same = []
    for l in log:
        if l.author == message.author and l.content == message.content:
            same.append(l)
    if len(same) > 3:
        for m in same:
            try:
                print(f"!ALERT!{message.guild}!{message.channel}!{message.author}!")
                with open("spam.txt", "a") as messages:
                    messages.write(f"{m}\n")
                await m.reply("`[REDACTED]`")
                await m.delete()
            except:
                print("[ERROR] couldn't delete")
        return True
    return False

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
            timestamp=datetime.datetime.utcnow()
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
            timestamp=datetime.datetime.utcnow()
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
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.avatar_url)
            embed.set_footer(text=f"ID: {before.id}")
            if len(before.roles) < len(after.roles):
                if editor == client.user:
                    return
                new_role = next(role for role in after.roles if role not in before.roles)
                embed.description = f"**{before.mention} was given the `{new_role.name}` role**"
            else:
                old_role = next(role for role in before.roles if role not in after.roles)
                embed.description = f"**{before.mention} was removed from the `{old_role.name}` role**"
            await channel.send(embed=embed)
        elif before.nick != after.nick:
            embed = discord.Embed(
                description=f"**{before.mention} nickname changed**",
                color=0x3480D5,
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Before", value=before.nick, inline=False)
            embed.add_field(name="After", value=after.nick, inline=False)
            embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.avatar_url)
            embed.set_footer(text=f"ID: {before.id}")
            await channel.send(embed=embed)

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.author.id in []:
        await message.reply("You have been banned from using this bot. If you think it's a mistake, please contact support.")
        return
    if await checkspam(message):
        return
    await client.process_commands(message)

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
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar_url)
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
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        embed.set_author(name=f"{before.author.name}#{before.author.discriminator}", icon_url=before.author.avatar_url)
        embed.set_footer(text=f"User ID: {before.author.id}")
        await channel.send(embed=embed)

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
async def mess(ctx, *args: typing.Union[discord.Member, str]):
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

@client.command()
@commands.has_any_role(872326201132339210, 872381019553153077)
async def update(ctx):
    fname = f"logs/log-{datetime.datetime.utcnow().isoformat()}.txt"
    await kerberos_management.update(ctx, client, open(fname, "w"))
    log_channel = client.get_channel(1025769912645451908)
    await log_channel.send(file=discord.File(fname), content=ctx.author.mention)

# Course Related Commands

@client.command(aliases=['tt'])
async def timetable(ctx, *args: typing.Union[discord.Member, str]):
    discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
    if str(ctx.message.author.id) not in discord_ids:
        await ctx.reply("Please set your kerberos using `?set <kerberos>` command before using this command!")
        return
    await ctx.reply("This command has been deprecated. For creating your timetable, use ClassGrid at https://classgrid.devclub.in.") ; return
    await course_management.send_timetable(ctx, client, args)

@client.command()
async def courses(ctx, *args: typing.Union[discord.Member, str]):
    discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
    if str(ctx.message.author.id) not in discord_ids:
        await ctx.reply("Please set your kerberos using `?set <kerberos>` command before using this command!")
        return
    await ctx.reply("This command has been deprecated. For creating your timetable, use ClassGrid at https://classgrid.devclub.in.") ; return
    await course_management.send_courses(ctx, client, args)

@client.command()
async def slot(ctx, *args):
    discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
    if str(ctx.message.author.id) not in discord_ids:
        await ctx.reply("Please set your kerberos using `?set <kerberos>` command before using this command!")
        return
    await ctx.reply("This command has been deprecated.") ; return
    await course_management.send_slots(ctx, client, args)

@client.command()
async def info(ctx, *args):
    discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
    if str(ctx.message.author.id) not in discord_ids:
        await ctx.reply("Please set your kerberos using `?set <kerberos>` command before using this command!")
        return
    await course_management.send_info(ctx, client, args)

@client.command(aliases=['major', 'minors', 'minor'])
async def majors(ctx, *args: typing.Union[discord.Member, str]):
    discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
    if str(ctx.message.author.id) not in discord_ids:
        await ctx.reply("Please set your kerberos using `?set <kerberos>` command before using this command!")
        return
    await ctx.reply("This command has been deprecated. For checking your examination schedule, please visit https://exam.iitd.ac.in (accessible via IITD intranet only)") ; return
    await course_management.majors(ctx, client, args)

@client.command()
async def count(ctx, course: str):
    discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
    if str(ctx.message.author.id) not in discord_ids:
        await ctx.reply("Please set your kerberos using `?set <kerberos>` command before using this command!")
        return
    await ctx.reply("This command has been deprecated.") ; return
    await course_management.count(ctx, client, course)

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

# Fun Commands

@client.command(aliases=['av'])
async def avatar(ctx, user: discord.Member = None):
    if not user:
        user = ctx.author
    embed = discord.Embed(title=f"Avatar", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
    embed.set_image(url=user.avatar_url)
    embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.reply(embed=embed)


# FETCHLDAP
@client.command()
async def fetchldap(ctx):
    msg = await ctx.reply('_Fetching LDAP Data:_ **0%**')
    await utils.fetch_ldap(msg)

@client.command()
async def ping(ctx):
    await ctx.reply(f"`{round(client.latency * 1000)}ms`")

@client.command()
async def help(ctx):
    embed = discord.Embed(title="IITD-Bot Help Menu", color=0x1ABC9C, timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(url=client.user.avatar_url)
    embed.add_field(name="General Commands", value="`?help` - Shows this message\n`?ping` - Shows bot latency\n`?set <kerberos>` - Sets your kerberos for using other commands\n`?courses` - Shows all the courses you are enrolled in\n`?timetable` - Shows your timetable\n`?slot <course_code>` - Shows all the slots of the given course code\n`?mess` - Shows the mess menu for your hostel for the present day", inline=False)
    embed.add_field(name="Manager Commands", value="`?updatemenu <hostel> <day> <meal> <menu>` - Updates the mess menu for the given hostel, day and meal\n`?updatetime <hostel> <day> <meal> <time>` - Updates the mess time for the given hostel, day and meal\n`?fetchldap` - Fetches course data from IITD Servers\n`?edit` - Set kerberos for another user\n`?purge <amount>` - Delete specified number of messages from a channel.\n`?update` - Updates the roles and names for everyone in the server.", inline=False)
    embed.add_field(name="Bot Details", value="Curious how this works? Check out the source code at https://github.com/as1605/IITD-Bot and leave a :star: if you like it!", inline=False)
    embed.set_footer(text=f"Requested by: {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.reply(embed=embed)

@client.command()
@commands.has_any_role(872326201132339210, 872381019553153077, 872375255795114005)
async def start(ctx):
    if ctx.guild.id == 871982588422656031:
        while True:
            members = len(ctx.guild.members)
            online = sum(member.status!=discord.Status.offline and not member.bot for member in ctx.guild.members)
            members_channel = client.get_channel(1025465969004523570)
            online_channel = client.get_channel(1025793822405427251)
            await members_channel.edit(name=f"Members: {members}")
            await online_channel.edit(name=f"Online Now: {online}")
            await asyncio.sleep(600)

@client.command()
@commands.has_any_role(872326201132339210, 872381019553153077, 872375255795114005)
async def purge(ctx, amount=100):
    await moderation.purge(ctx, client, amount)

utils.reload()
load_dotenv()
client.run(os.getenv('BOT_TOKEN'))
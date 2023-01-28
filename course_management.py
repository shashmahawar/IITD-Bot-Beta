import discord
import utils
import datetime, json

async def send_timetable(ctx, client, args):
    users = []
    if not args:
        discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
        users.append(discord_ids[str(ctx.author.id)]['kerberos'])
    else:
        for arg in args:
            if type(arg) == discord.member.Member:
                discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
                try:
                    users.append(discord_ids[str(arg.id)]['kerberos'])
                except:
                    pass
            else:
                users.append(arg)
    ctr = 0
    for user in users:
        timetable = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}
        courses = await utils.get_courses(user)
        if not courses:
            return
        for course in courses:
            if course in utils.course_slots and utils.course_slots[course] in utils.slots:
                slot = utils.course_slots[course]
                slot_details = utils.slots[slot]
                for day in slot_details:
                    timetable[day].append(f"{course}: {slot_details[day]}")
        embed = discord.Embed(title=f"Timetable for {user}", color=0x3480D5, timestamp=datetime.datetime.utcnow())
        for day in timetable:
            embed.add_field(name=day, value="```"+ "\n".join(timetable[day]) + "```", inline=False)
        embed.set_footer(text=f"Requested by: {ctx.author.name}#{ctx.author.discriminator}")
        if ctr == 0:
            await ctx.reply(embed=embed)
            ctr = 1
        else:
            await ctx.send(embed=embed)

async def send_courses(ctx, client, args):
    users = []
    if not args:
        discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
        users.append(discord_ids[str(ctx.author.id)]['kerberos'])
    else:
        for arg in args:
            if type(arg) == discord.member.Member:
                discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
                try:
                    users.append(discord_ids[str(arg.id)]['kerberos'])
                except:
                    pass
            else:
                users.append(arg)
    ctr = 0
    for user in users:
        courses = await utils.get_courses(user)
        if not courses:
            return
        reply = ""
        for course in courses:
            reply += f"`{course}` "
        embed = discord.Embed(title=f"Courses for {user}", description=reply,color=0x3480D5, timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"Requested by: {ctx.author.name}#{ctx.author.discriminator}")
        if ctr == 0:
            await ctx.reply(embed=embed)
            ctr = 1
        else:
            await ctx.send(embed=embed)

async def send_slots(ctx, client, args):
    embed = discord.Embed(title=f"Course Slots", color=0x3480D5, timestamp=datetime.datetime.utcnow())
    for arg in args:
        if arg.upper() in utils.course_slots:
            embed.add_field(name=arg.upper(), value=f"`{utils.course_slots[arg.upper()]}`")
    embed.set_footer(text=f"Requested by: {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.reply(embed=embed)

async def send_info(ctx, client, args):
    ctr = 0
    for arg in args:
        arg = arg.upper()
        if arg in utils.courseinfo:
            info = utils.course_info(arg)
            if not info:
                continue
            embed = discord.Embed(title = f"{info['code']} - {info['name']}", color=discord.Color.gold())
            embed.add_field(name='Credits', value = f"`{info['credits']}`")
            embed.add_field(name='Credit Structure', value = f"`{info['credit-structure']}`")
            embed.add_field(name='Pre-requisites', value = f"`{info['pre-requisites']}`")
            embed.add_field(name='Dependencies', value = '\t'.join(f"`{c}`" for c in info['dependencies']))
            embed.add_field(name='Overlap', value = f"`{info['overlap']}`")
            embed.add_field(name='Description', value = info['description'][:1024], inline=False)
            if ctr == 0:
                ctr = 1
                await ctx.reply(embed=embed)
            else:
                await ctx.send(embed=embed)

async def minors(ctx, client, args):
    kerberos = []
    if not args:
        discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
        kerberos.append(discord_ids[str(ctx.author.id)]['kerberos'])
    else:
        for arg in args:
            if type(arg) == discord.member.Member:
                discord_ids = json.load(open("datafiles/discord_ids.json", "r"))
                try:
                    kerberos.append(discord_ids[str(arg.id)]['kerberos'])
                except:
                    pass
            else:
                kerberos.append(arg)
    if len(kerberos) == 0:
        return
    ctr = 0
    for user in kerberos:
        embed = discord.Embed(title=f"Minor Schedule for {user}", color=discord.Color.green())
        for minor in utils.get_minors(user):
            embed.add_field(name=f"{minor['Day']} February", value=f"`{minor['Course']}`: **{minor['Time']}** ({'/'.join(minor['Venues'])})", inline=False)
        if ctr == 0:
            await ctx.reply(embed=embed)
            ctr = 1
        else:
            await ctx.send(embed=embed)
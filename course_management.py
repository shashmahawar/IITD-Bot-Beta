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
        embed = discord.Embed(title=f"Timetable for {user}", color=0x3480D5, timestamp=datetime.datetime.now())
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
        embed = discord.Embed(title=f"Courses for {user}", description=reply,color=0x3480D5, timestamp=datetime.datetime.now())
        embed.set_footer(text=f"Requested by: {ctx.author.name}#{ctx.author.discriminator}")
        if ctr == 0:
            await ctx.reply(embed=embed)
            ctr = 1
        else:
            await ctx.send(embed=embed)

async def send_slots(ctx, client, args):
    embed = discord.Embed(title=f"Course Slots", color=0x3480D5, timestamp=datetime.datetime.now())
    for arg in args:
        if arg.upper() in utils.course_slots:
            embed.add_field(name=arg.upper(), value=f"`{utils.course_slots[arg.upper()]}`")
    embed.set_footer(text=f"Requested by: {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.reply(embed=embed)
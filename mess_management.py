import discord
import calendar, datetime, json
import utils

async def send_menu(ctx, client, args):
    hostels = []
    days = []
    ck = 0
    for arg in args:
        if type(args) == discord.member.Member:
            try:
                kerberos = json.load(open("datafiles/discord_ids.json"))[str(args.id)]["kerberos"]
                hostels.append(utils.kerberos[kerberos]["hostel"])
            except:
                pass
        else:
            arg = arg.title()
            if arg in utils.hostels:
                hostels.append(arg)
            elif arg.lower() == '-all':
                days = [day.title() for day in utils.days]
                ck = 1
            elif arg[0] == '-' and ck == 0:
                for d in utils.days:
                    if arg[1:4].lower() == d.lower():
                        days.append(d.title())
    if len(days) == 0:
        days.append(calendar.day_abbr[datetime.datetime.now().weekday()])
    if len(hostels) == 0:
        kerberos = json.load(open("datafiles/discord_ids.json"))[str(ctx.message.author.id)]["kerberos"]
        hostel = utils.kerberos[kerberos]["hostel"]
        if len(hostel) > 1:
            hostels.append(hostel)
        else:
            await ctx.reply("Please provide a hostel for which you want to see the menu")
    if len(hostels)*len(days) > 7:
        await ctx.reply("Maximum 7 operations are allowed. Please try again with fewer arguments!")
        return
    ctr = 0
    for hostel in hostels:
        with open("datafiles/mess.json", "r") as f:
            menu = json.load(f)
            menu = menu[hostel]
        for day in days:
            today = menu[day]
            embed = discord.Embed(title=f'{day}\'s Mess Menu for {hostel}', color=discord.Color.blue())
            for meal in today:
                embed.add_field(name=f"**{meal}** ({today[meal]['time']})", value=f"{today[meal]['menu']}", inline=False)
            if ctr == 0:
                ctr = 1
                await ctx.reply(embed=embed)
            else:
                await ctx.send(embed=embed)

async def update_menu(ctx, client, hostel, day, meal, menu):
    with open("datafiles/mess.json", "r") as f:
        data = json.load(f)
    last_menu = data[hostel][day][meal]['menu']
    data[hostel][day][meal]['menu'] = menu
    with open("datafiles/mess.json", "w") as f:
        json.dump(data, f)
    await ctx.reply("Updated the menu successfully!")
    mess_channel = client.get_channel(1025322494606983188)
    embed = discord.Embed(
        description=f"**{meal} menu for {hostel} hostel was updated by {ctx.message.author.mention}**",
        color=0x3480D5,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Previous Menu", value=last_menu, inline=False)
    embed.add_field(name="New Menu", value=menu, inline=False)
    embed.set_author(name=f"{ctx.message.author.name}#{ctx.message.author.discriminator}", icon_url=ctx.message.author.avatar)
    embed.set_footer(text=f"ID: {ctx.message.author.id}")
    await mess_channel.send(embed=embed)

async def update_time(ctx, client, hostel, day, meal, time):
    with open("datafiles/mess.json", "r") as f:
        data = json.load(f)
    last_time = data[hostel][day][meal]['time']
    data[hostel][day][meal]['time'] = time
    with open("datafiles/mess.json", "w") as f:
        json.dump(data, f)
    await ctx.reply("Updated the timing successfully!")
    mess_channel = client.get_channel(1025322494606983188)
    embed = discord.Embed(
        description=f"**{meal} timing for {hostel} hostel was updated by {ctx.message.author.mention}**",
        color=0x3480D5,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Previous Timing", value=last_time, inline=False)
    embed.add_field(name="New Timing", value=time, inline=False)
    embed.set_author(name=f"{ctx.message.author.name}#{ctx.message.author.discriminator}", icon_url=ctx.message.author.avatar)
    embed.set_footer(text=f"ID: {ctx.message.author.id}")
    await mess_channel.send(embed=embed)

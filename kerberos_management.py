import discord
import utils
import datetime, json

async def set(ctx, kerberos, client, msg, user):
    user_details = utils.kerberos[kerberos]
    user_name = user_details['name']
    user_hostel = user_details['hostel']
    update_channel = client.get_channel(1025058604488851536)

    with open("datafiles/discord_ids.json", 'r') as f:
        data = json.load(f)
        if str(user.id) in data:
            method = 'UPDATE'
        else:
            method = 'INSERT'
        for i in data:
            if data[i]['kerberos'] == kerberos:
                clash = True
                clashed_user = await client.fetch_user(i)
                break
        else:
            clash = False

    if method == 'UPDATE':
        last_kerberos = data[str(user.id)]['kerberos']
        if last_kerberos == kerberos:
            await msg.edit(content=f"Account already linked to `{kerberos}`")
            return
        await msg.edit(content=f"Account was previously linked to `{last_kerberos}`")

    with open("datafiles/discord_ids.json", 'w') as f:
        data[str(user.id)] = {'kerberos': kerberos, 'name': user_name, 'hostel': user_hostel}
        json.dump(data, f)

    for role in user.roles:
        if role.name in utils.branches:
            await user.remove_roles(role)
        elif role.name in utils.hostels:
            await user.remove_roles(role)
        elif role.name in utils.years:
            await user.remove_roles(role)

    branch_role = discord.utils.get(ctx.guild.roles, name=kerberos[:3].upper())
    if not branch_role:
        await ctx.guild.create_role(name=kerberos[:3].upper())
    await user.add_roles(discord.utils.get(ctx.guild.roles, name=kerberos[:3].upper()))

    hostel_role = discord.utils.get(ctx.guild.roles, name=user_hostel)
    if not hostel_role:
        await ctx.guild.create_role(name=user_hostel)
    await user.add_roles(discord.utils.get(ctx.guild.roles, name=user_hostel))

    year_role = discord.utils.get(ctx.guild.roles, name=f"20{kerberos[3:5]}")
    if not year_role:
        await ctx.guild.create_role(name=f"20{kerberos[3:5]}")
    await user.add_roles(discord.utils.get(ctx.guild.roles, name=f"20{kerberos[3:5]}"))

    try:
        await user.edit(nick=user_name)
    except:
        pass
    
    if method == 'UPDATE':
        embed = discord.Embed(description=f"**{user.mention} kerberos updated.**", color=0x3480D5, timestamp=datetime.datetime.now())
        embed.add_field(name="Previous Kerberos", value=last_kerberos, inline=False)
        embed.add_field(name="New Kerberos", value=kerberos, inline=False)
        embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar)
        embed.set_footer(text=f"ID: {user.id}")
        await update_channel.send(embed=embed)
    else:
        embed = discord.Embed(description=f"**{user.mention} kerberos set.**", color=0x3480D5, timestamp=datetime.datetime.now())
        embed.add_field(name="Kerberos", value=kerberos, inline=False)
        embed.add_field(name="Name", value=user_name, inline=False)
        embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar)
        embed.set_footer(text=f"ID: {user.id}")
        await update_channel.send(embed=embed)

    if clash:
        embed = discord.Embed(title="**Kerberos Clash**", description=f"Kerberos Clash has been identified between {user.mention} and {clashed_user.mention}.",color=0xFE4712, timestamp=datetime.datetime.now())
        embed.add_field(name="Kerberos", value=kerberos, inline=True)
        embed.add_field(name="Name", value=user_name, inline=True)
        embed.set_footer(text=f"ID: {user.id}")
        message = await update_channel.send(embed=embed)
        admin_channel = client.get_channel(871983551749451867)
        await admin_channel.send(f"Kerberos Clash Detected. Check here \n{message.jump_url}")
    
    await msg.edit(content=f"Account has been linked to `{kerberos}`")

    member_channel = client.get_channel(1025010614948606073)
    embed = discord.Embed(
        description=f"**{user.mention} was given the `{kerberos[:3].upper()}`, `{user_hostel}` and `20{kerberos[3:5]}` roles**",
        color=0x3480D5,
        timestamp=datetime.datetime.now()
    )
    embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar)
    embed.set_footer(text=f"ID: {user.id}")
    await member_channel.send(embed=embed)

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
        data[str(user.id)] = {'kerberos': kerberos, 'name': user_name}
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
        embed = discord.Embed(description=f"**{user.mention} kerberos updated.**", color=0x3480D5, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Previous Kerberos", value=last_kerberos, inline=False)
        embed.add_field(name="New Kerberos", value=kerberos, inline=False)
        embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar_url)
        embed.set_footer(text=f"ID: {user.id}")
        await update_channel.send(embed=embed)
    else:
        embed = discord.Embed(description=f"**{user.mention} kerberos set.**", color=0x3480D5, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Kerberos", value=kerberos, inline=False)
        embed.add_field(name="Name", value=user_name, inline=False)
        embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar_url)
        embed.set_footer(text=f"ID: {user.id}")
        await update_channel.send(embed=embed)

    if clash:
        embed = discord.Embed(title="**Kerberos Clash**", description=f"Kerberos Clash has been identified between {user.mention} and {clashed_user.mention}.",color=0xFE4712, timestamp=datetime.datetime.utcnow())
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
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar_url)
    embed.set_footer(text=f"ID: {user.id}")
    await member_channel.send(embed=embed)

async def update(ctx, client, log):
    discord_ids = json.load(open("datafiles/discord_ids.json", 'r'))
    kerb_id = {}
    channel = client.get_channel(1063136411244564633)
    bot_commands = client.get_channel(872364635637035028)

    async for user in ctx.guild.fetch_members(limit=None):
        id = str(user.id)
        if id not in discord_ids:
            if not user.bot:
                log.write(f"ERROR: Did not find `{user.name}#{user.discriminator}` in discord_ids"+'\n')
                await channel.send(f"{user.mention} Please set your kerberos in {bot_commands.mention} channel or you will be removed from this server.")
            continue
    
        kerberos = str(discord_ids[id]['kerberos'])
        if kerberos in kerb_id:
            clashed_user = await client.fetch_user(int(kerb_id[kerberos]))
            log.write(f"WARNING: DUPLICATE key `{kerberos}` for `{user.name}#{user.discriminator}` and `{clashed_user.name}#{clashed_user.discriminator}`\n")
            await channel.send(f"{user.mention} and {clashed_user.mention} have same kerberos registered with their accounts.")
        else:
            kerb_id[kerberos] = id

        if kerberos in utils.kerberos:
            name = str(utils.kerberos[kerberos]["name"])
            if name != user.nick and name != user.name:
                try:
                    await user.edit(nick=name)
                    log.write(f"ACTION: NICK for `{user.name}#{user.discriminator}` changed to `{name}`\n")
                except:
                    log.write(f"WARNING: NICK cannot be changed for `{user.name}#{user.discriminator}`. Expected: `{name}`\n")
                    await channel.send(f"{user.mention} Please change your name to `{name}`")
                    pass

            year = "20"+str(kerberos[3:5])
            for y in utils.years:
                if y != year and discord.utils.get(ctx.guild.roles, name = y) in user.roles:
                    await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name = y))
                    log.write(f"ACTION: Removed role `{y}` for `{user.name}#{user.discriminator}`\n")
            if discord.utils.get(ctx.message.guild.roles, name = year) not in user.roles:
                try:
                    await user.add_roles(discord.utils.get(ctx.message.guild.roles, name = year))
                    log.write(f"ACTION: Added role `{year}` for `{user.name}#{user.discriminator}`\n")
                except:
                    log.write(f"WARNING: ROLE not found `{year}`\n")

            hostel = str(utils.kerberos[kerberos]["hostel"])
            for h in utils.hostels:
                if h != hostel and discord.utils.get(ctx.guild.roles, name = h) in user.roles:
                    await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name = h))
                    log.write(f"ACTION: Removed role `{h}` for `{user.name}#{user.discriminator}`\n")
            if discord.utils.get(ctx.guild.roles, name = hostel) not in user.roles:
                try:
                    await user.add_roles(discord.utils.get(ctx.message.guild.roles, name = hostel))
                    log.write(f"ACTION: Added role `{hostel}` for `{user.name}#{user.discriminator}`\n")
                except:
                    log.write(f"WARNING: ROLE not found `{hostel}`\n")

            branch = str(kerberos[:3]).upper()
            for b in utils.branches:
                if b.upper() != branch and discord.utils.get(ctx.guild.roles, name = b.upper()) in user.roles:
                    await user.remove_roles(discord.utils.get(ctx.guild.roles, name = b.upper()))
                    log.write(f"ACTION: Removed role `{b.upper()}` for `{user.name}#{user.discriminator}`\n")
            if discord.utils.get(ctx.guild.roles, name = branch) not in user.roles:
                try:
                    await user.add_roles(discord.utils.get(ctx.ssage.guild.roles, name = branch))
                    log.write(f"ACTION: Added role `{branch}` for `{user.name}#{user.discriminator}`\n")
                except:
                    log.write(f"WARNING: ROLE not found `{branch}`"+'\n')
        else:
            log.write(f"WARNING: Could not find `{kerberos}` in kerberos database"+'\n')
            await channel.send(f"Kerberos linked with {user.mention}, i.e. `{kerberos}` could not be found in the kerberos database.")
        log.flush()
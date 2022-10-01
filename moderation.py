import discord
import datetime

async def purge(ctx, client, amount):
    await ctx.channel.purge(limit=amount+1)
    await ctx.channel.send(f"{ctx.author.mention} {amount} messages were deleted.", delete_after=5)
    channel = client.get_channel(1025785970693525675)
    embed = discord.Embed(description=f"{ctx.author.mention} purged {amount} messages in {ctx.channel.mention}", color=0x3480D5, timestamp=datetime.datetime.now())
    embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar)
    embed.set_footer(text=f"ID: {ctx.author.id}")
    await channel.send(embed=embed)
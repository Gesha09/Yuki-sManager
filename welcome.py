import discord

from config import (
    Welcome_Channel,
    Role_Assignment_Channel,
)

def find_text_channel(guild,channel_name):
    for channel in guild.text_channels:
        if channel.name == channel_name:
            return channel
    return None

async def send_welcome(member):

    channel = find_text_channel(member.guild, Welcome_Channel)

    if channel is None:
        print(
            f"⚠️ Welcome channel '{Welcome_Channel}' "
            f"not found in '{member.guild.name}'."
        )
        return

    embed = discord.Embed(
        title="🎉 Welcome to The Judgement of Abyssal Tides!",
        description=(
            f"Welcome, {member.mention}! ⚔️\n\n"
            "We're glad to have you here!\n\n"
            "🟨 **Judgement**\n"
            "🟪 **Abyssal Tide**\n\n"
            f"Head over to the **#{Role_Assignment_Channel}** channel "
            "and select the alliance you belong to.\n\n"
            "Choose your alliance, get your role, "
            "and enjoy your time here!\n\n"
            "**Good luck and have fun! ⚔️🌊**"
        ),
        color=discord.Color.gold()
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="The Judgement of Abyssal Tides")

    await channel.send(embed=embed)


async def send_goodbye(member):

    channel = find_text_channel(member.guild, Welcome_Channel)

    if channel is None:
        print(
            f"⚠️ Welcome channel '{Welcome_Channel}' "
            f"not found in '{member.guild.name}'."
        )
        return

    embed = discord.Embed(
        title="👋 A member has left",
        description=(
            f"**{member.display_name}** has left the server.\n\n"
            "We wish you the best on your journey. ⚔️"
        ),
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="The Judgement of Abyssal Tides")

    await channel.send(embed=embed)
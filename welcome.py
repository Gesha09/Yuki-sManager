import discord
from config import Welcome_Channel, Role_Assignment_Channel
from alliance_manager import AllianceManager

alliance_manager = AllianceManager()


def find_text_channel(guild, channel_name):
    for channel in guild.text_channels:
        if channel.name == channel_name:
            return channel
    return None


async def send_welcome(member):
    alliance_manager.load_settings()
    channel = find_text_channel(member.guild, Welcome_Channel)
    if channel is None:
        print(f"⚠️ Welcome channel '{Welcome_Channel}' not found in '{member.guild.name}'.")
        return

    server_name = alliance_manager.get_server_name(member.guild)
    alliances = alliance_manager.get_alliances(member.guild.id)

    if alliances:
        alliance_list = "\n".join([f"{a['emoji']} **{a['name']}**" for a in alliances])
    else:
        alliance_list = "⚠️ No alliances configured yet. Please contact an admin."

    embed = discord.Embed(
        title=f"🎉 Welcome to {server_name}!",
        description=(
            f"Welcome, {member.mention}! ⚔️\n\n"
            "We're glad to have you here!\n\n"
            f"**Our Allied Alliances:**\n{alliance_list}\n\n"
            f"Head over to **#{Role_Assignment_Channel}** and select your alliance.\n\n"
            "Choose your alliance, get your role, and enjoy your time here!\n\n"
            "**Good luck and have fun! ⚔️🌊**"
        ),
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=server_name)
    await channel.send(embed=embed)


async def send_goodbye(member):
    alliance_manager.load_settings()
    channel = find_text_channel(member.guild, Welcome_Channel)
    if channel is None:
        print(f"⚠️ Welcome channel '{Welcome_Channel}' not found in '{member.guild.name}'.")
        return

    server_name = alliance_manager.get_server_name(member.guild)

    embed = discord.Embed(
        title="👋 A member has left",
        description=(
            f"**{member.display_name}** has left **{server_name}**.\n\n"
            "We wish you the best on your journey. ⚔️"
        ),
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=server_name)
    await channel.send(embed=embed)
import os
import discord
from discord.ext import commands,tasks
from discord import ui
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

#Discord roles name
Judgement_role_name = "Judgement"
Abbysal_role_name = "Abyssal Tides"

#Discord channel name
Role_Assignment_Channel = "role-assignment"
Role_Log_Channel = "role-log"
Welcome_Channel = "welcome-log"

#how often bot checks the channel in minutes
Pannel_Checks = 10

#Confirm Join
class ConfirmJoinView(ui.View):
    def __init__(self, role_name, emoji):
        super().__init__(timeout=60)
        self.role_name = role_name
        self.emoji = emoji

    @ui.button(label="Confirm",emoji="✅", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if role == None:
            await interaction.edit_original_response(content=f"❌ Role '{self.role_name}' not found.", view=None)
            return
        if role in interaction.user.roles:
            await interaction.edit_original_response(content=f"❌ You already have the {self.role_name} Role!", view=None)
            return
        try:
            await interaction.user.add_roles(role)
        except:
            await interaction.edit_original_response(content=("❌ couldn't assign role:\n\n make sure bot role is above alliance role"),view=None)
            return
        await interaction.edit_original_response(content=f"✅ You have the {self.role_name} Role! {self.emoji}", view=None)
        await write_join_log(interaction.guild, interaction.user, self.role_name, self.emoji)
        
        
    @ui.button(label="Cancel",emoji="❌", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.edit_original_response(content="❌ Role assignment cancelled.", view=None)

#Confirm Leave
class ConfirmLeaveView(ui.View):
    def __init__(self,role_name,emoji):
        super().__init__(timeout=60)
        self.role_name = role_name
        self.emoji = emoji
    @ui.button(label="Yes Leave ", emoji="✅", style=discord.ButtonStyle.danger)
    async def confirm_leave(
        self,
        interaction: discord.Interaction,
        button: ui.Button
    ):
        await interaction.response.defer(ephemeral=True)
        role = discord.utils.get(interaction.guild.roles,name=self.role_name)

        if role == None:
            await interaction.edit_original_response(content=f"❌ Role **{self.role_name}** was not found.",view=None)
            return
        if role not in interaction.user.roles:
            await interaction.edit_original_response(content=f"❌ you dont currently have the **{self.role_name}** Alliance role",view=None)
            return
        try:
            await interaction.user.remove_roles(role)
        except discord.Forbidden:
            await interaction.edit_original_response(content="❌ couldn't remove that role.\n\n please make sure bot role is above alliance role!",view=None)
            return
        await interaction.edit_original_response(content=f"✅ You have left the **{self.role_name}** Alliance role! {self.emoji}",view=None)
        await write_leave_log(interaction.guild,interaction.user,self.role_name,self.emoji)
    @ui.button(label="Cancel",emoji="❌",style=discord.ButtonStyle.danger)
    async def cancel_leaave(
        self,
        interaction: discord.Interaction,
        button: ui.Button
    ):
        await interaction.response.edit_message(content="❌ Leaving the alliance role was Canceled",view=None)
            
class LeaveAllianceView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)
    @ui.button(label="Leave Judgement ",emoji="🟨",style=discord.ButtonStyle.danger)
    async def leave_judgement(
        self,
        interaction: discord.Interaction,
        button: ui.Button
    ):
        await interaction.response.edit_message(content="⚠️ **Are you Sure!?** \n\n you are about to leave **Judgement** alliance role \n\n you can join later.",view=ConfirmLeaveView(Judgement_role_name," 🟨"))
    @ui.button(label="Leave Abyssal Tides",emoji="🟪",style=discord.ButtonStyle.danger)
    async def leave_abyssal_tides(
            self,
            interaction: discord.Interaction,
            button: ui.Button
        ):
            await interaction.response.edit_message(content="⚠️ **Are you Sure!?** \n\n you are about to leave **Abyssal Tides** alliance role \n\n you can join later.",view=ConfirmLeaveView(Abbysal_role_name," 🟪"))
    @ui.button(label="Cancel",emoji="❌",style=discord.ButtonStyle.secondary)
    async def cancel_leave(
        self,
        interaction: discord.Interaction,
        button: ui.Button
    ):
        interaction.response.edit_message(content="❌ Cancelled!!",view=None)

class AllianceView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Join Judgement", emoji="🟨", style=discord.ButtonStyle.primary, custom_id="join_judgement")
    async def join_judgement(self, interaction: discord.Interaction, button: ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=Judgement_role_name)
        if role:
            await interaction.response.send_message(f"✅ You have the {Judgement_role_name} Role! 🟨",view=ConfirmJoinView(Judgement_role_name,"🟨"), ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Role '{Judgement_role_name}' not found.", ephemeral=True)

    @ui.button(label="Join Abyssal Tides", emoji="🟪", style=discord.ButtonStyle.primary, custom_id="join_abyssal_tides")
    async def join_abyssal_tides(self, interaction: discord.Interaction, button: ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=Abbysal_role_name)
        if role:
            await interaction.response.send_message(f"✅ You have the {Abbysal_role_name} Role! 🟪",view=ConfirmJoinView(Abbysal_role_name,"🟪"), ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Role '{Abbysal_role_name}' not found.", ephemeral=True)
    @ui.button(label="Leave a role", emoji="❌", style=discord.ButtonStyle.primary,custom_id="Leave_role")
    async def leave_alliance_role(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(("❌ **Leave an alliance Role?** which alliance role would you like to leave?"),view=LeaveAllianceView(),ephemeral=True)


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
            "Head over to the **#role-assignment** channel "
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

async def write_join_log(guild, user, role_name, emoji):
    log_channel = find_text_channel(guild, Role_Log_Channel)
    if log_channel == None:
        print(f"Log channel '{Role_Log_Channel}' not found in guild '{guild.name}'.")
        return
    embed = discord.Embed(
        title="Role Assignment",
        description=f"{user.mention} has been assigned the role **{role_name}** {emoji}.",
        color=discord.Color.green()
    )
    embed.set_thumbnail(
        url = user.display_avatar.url
    )
    embed.set_footer(text=f"User ID: {user.id}")
    await log_channel.send(embed = embed)

async def write_leave_log(guild, user, role_name, emoji):
    log_channel = find_text_channel(guild, Role_Log_Channel)
    if log_channel == None:
        print(f"Log channel '{Role_Log_Channel}' not found in guild '{guild.name}'.")
        return
    embed = discord.Embed(
        title="Role Assignment",
        description=f"{user.mention}'s role **{role_name}** {emoji} has been DeAssigned.",
        color=discord.Color.red()
    )
    embed.set_thumbnail(
        url = user.display_avatar.url
    )
    embed.set_footer(text=f"User ID: {user.id}")
    await log_channel.send(embed = embed)

async def create_alliance_panel(channel):
    embed = discord.Embed(
        title="⚔️ Alliance Selection/Registration!",
        description=" Welcome To our Allied Community\n\n" \
        "Our Server consists of two allied Alliance -- Choose the alliance you belong to by clicking the buttons below.\n\n" \
        "**🟨 Judgement**\n" \
        "Members of Judgement Alliance\n\n" \
        "**🟪 Abyssal Tides**\n" \
        "Members of Abyssal Tides\n\n" \
        "**please select your alliance below.**",
        color=discord.Color.from_rgb(150,150,150)
    )
    embed.set_footer(text="Select your alliance to get the role!(if u have multiple ids in both alli you may select both as well).")
    view = AllianceView()
    await channel.send(embed=embed, view=view)

async def ensure_alliance_panel(guild):
    channel = find_text_channel(guild,Role_Assignment_Channel)

    if channel is None:
        print(f"⚠️ warning! '{Role_Assignment_Channel}' was not found!")
        return
    async for message in channel.history(limit = 50):
        if message.author != bot.user:
            continue
        if not message.embeds:
            continue
        embed = message.embeds[0]
        if embed.title == "⚔️ Alliance Selection/Registration!":
            print("alliance panel already exists!")
            return
    await create_alliance_panel(channel)

class AllianceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(AllianceView())  # Register the view to persist across bot restarts
        self.check_alliance_panel.start()
    
    async def on_ready(self):
        print(f"Loggedin as user {self.user.name} (ID: {self.user.id})")
        print(f"Connected to {len(self.guilds)} server(s)")
        for guild in self.guilds:
            await ensure_alliance_panel(guild)
    
    async def on_member_join(self, member):
        await send_welcome(member)

    async def on_member_remove(self, member):
        await send_goodbye(member)

    @tasks.loop(minutes=Pannel_Checks)
    async def check_alliance_panel(self):
        for guild in self.guilds:
            await ensure_alliance_panel(guild)

    @check_alliance_panel.before_loop 
    async def before_panel_check(self):
        await self.wait_until_ready()

bot = AllianceBot()

bot.run(TOKEN)
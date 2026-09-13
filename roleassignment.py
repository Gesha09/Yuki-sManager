import discord
from discord import ui

from config import (
    Judgement_role_name,
    Abbysal_role_name,
    Role_Assignment_Channel,
    Role_Log_Channel,
    Pannel_Checks
)
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
        if message.author.id != guild.me.id:
            continue
        if not message.embeds:
            continue
        embed = message.embeds[0]
        if embed.title == "⚔️ Alliance Selection/Registration!":
            print("alliance panel already exists!")
            return
    await create_alliance_panel(channel)

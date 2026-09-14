import asyncio
import discord
from discord import ui
from config import Role_Assignment_Channel, Role_Log_Channel
from alliance_manager import AllianceManager

alliance_manager = AllianceManager()


class ConfirmJoinView(ui.View):
    def __init__(self, alliance_name, alliance_emoji, role_id):
        super().__init__(timeout=60)
        self.alliance_name = alliance_name
        self.alliance_emoji = alliance_emoji
        self.role_id = role_id

    @ui.button(label="Confirm", emoji="✅", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        role = interaction.guild.get_role(self.role_id)

        if role is None:
            await interaction.edit_original_response(
                content="❌ Role not found.", view=None
            )
            return

        if role in interaction.user.roles:
            await interaction.edit_original_response(
                content=f"❌ You already have the {self.alliance_name} role!", view=None
            )
            return

        try:
            await interaction.user.add_roles(role)
        except discord.Forbidden:
            await interaction.edit_original_response(
                content="❌ Couldn't assign role. Bot role must be above alliance role.", view=None
            )
            return

        await interaction.edit_original_response(
            content=f"✅ You now have the {self.alliance_emoji} **{self.alliance_name}** role!", view=None
        )
        await write_join_log(interaction.guild, interaction.user, self.alliance_name, self.alliance_emoji)

    @ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(content="❌ Cancelled.", view=None)


class ConfirmLeaveView(ui.View):
    def __init__(self, alliance_name, alliance_emoji, role_id):
        super().__init__(timeout=60)
        self.alliance_name = alliance_name
        self.alliance_emoji = alliance_emoji
        self.role_id = role_id

    @ui.button(label="Yes, Leave", emoji="✅", style=discord.ButtonStyle.danger)
    async def confirm_leave(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        role = interaction.guild.get_role(self.role_id)

        if role is None:
            await interaction.edit_original_response(
                content="❌ Role not found.", view=None
            )
            return

        if role not in interaction.user.roles:
            await interaction.edit_original_response(
                content=f"❌ You don't have the **{self.alliance_name}** role.", view=None
            )
            return

        try:
            await interaction.user.remove_roles(role)
        except discord.Forbidden:
            await interaction.edit_original_response(
                content="❌ Couldn't remove role. Bot role must be above alliance role.", view=None
            )
            return

        await interaction.edit_original_response(
            content=f"✅ You left the {self.alliance_emoji} **{self.alliance_name}** role!", view=None
        )
        await write_leave_log(interaction.guild, interaction.user, self.alliance_name, self.alliance_emoji)

    @ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.secondary)
    async def cancel_leave(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(content="❌ Cancelled.", view=None)


class LeaveAllianceView(ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=60)
        alliances = alliance_manager.get_alliances(guild_id)

        for alliance in alliances:
            if alliance.get("role_id"):
                btn = ui.Button(
                    label=f"Leave {alliance['name']}",
                    emoji=alliance["emoji"],
                    style=discord.ButtonStyle.danger
                )
                btn.callback = self._make_leave_cb(alliance)
                self.add_item(btn)

        cancel_btn = ui.Button(label="Cancel", emoji="❌", style=discord.ButtonStyle.secondary)
        cancel_btn.callback = self._cancel_cb
        self.add_item(cancel_btn)

    def _make_leave_cb(self, alliance):
        async def cb(interaction: discord.Interaction):
            view = ConfirmLeaveView(alliance["name"], alliance["emoji"], alliance["role_id"])
            await interaction.response.edit_message(
                content=f"⚠️ Are you sure you want to leave **{alliance['name']}**?",
                view=view
            )
        return cb

    async def _cancel_cb(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="❌ Cancelled.", view=None)


class DynamicAllianceView(ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        alliances = alliance_manager.get_alliances(guild_id)

        for alliance in alliances:
            if alliance.get("role_id"):
                btn = ui.Button(
                    label=f"Join {alliance['name']}",
                    emoji=alliance["emoji"],
                    style=discord.ButtonStyle.primary,
                    custom_id=f"join_{alliance['name'].lower().replace(' ', '_')}"
                )
                btn.callback = self._make_join_cb(alliance)
                self.add_item(btn)

        if alliances:
            leave_btn = ui.Button(
                label="Leave a role",
                emoji="❌",
                style=discord.ButtonStyle.secondary,
                custom_id="leave_role"
            )
            leave_btn.callback = self._leave_cb
            self.add_item(leave_btn)

    def _make_join_cb(self, alliance):
        async def cb(interaction: discord.Interaction):
            view = ConfirmJoinView(alliance["name"], alliance["emoji"], alliance["role_id"])
            await interaction.response.send_message(
                f"Confirm joining **{alliance['emoji']} {alliance['name']}**?",
                view=view,
                ephemeral=True
            )
        return cb

    async def _leave_cb(self, interaction: discord.Interaction):
        view = LeaveAllianceView(interaction.guild.id)
        await interaction.response.send_message(
            "Which alliance role would you like to leave?",
            view=view,
            ephemeral=True
        )


def find_text_channel(guild, channel_name):
    for channel in guild.text_channels:
        if channel.name == channel_name:
            return channel
    return None


async def write_join_log(guild, user, role_name, emoji):
    log_channel = find_text_channel(guild, Role_Log_Channel)
    if log_channel is None:
        return
    embed = discord.Embed(
        title="Role Assigned",
        description=f"{user.mention} joined {emoji} **{role_name}**",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text=f"User ID: {user.id}")
    await log_channel.send(embed=embed)


async def write_leave_log(guild, user, role_name, emoji):
    log_channel = find_text_channel(guild, Role_Log_Channel)
    if log_channel is None:
        return
    embed = discord.Embed(
        title="Role Removed",
        description=f"{user.mention} left {emoji} **{role_name}**",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text=f"User ID: {user.id}")
    await log_channel.send(embed=embed)


async def create_alliance_panel(guild, channel):
    alliance_manager.load_settings()
    server_name = alliance_manager.get_server_name(guild)
    alliances = alliance_manager.get_alliances(guild.id)

    if alliances:
        alliance_list = "\n".join(
            [f"{a['emoji']} **{a['name']}**" for a in alliances]
        )
        description = (
            f"Welcome to **{server_name}**!\n\n"
            "Our server consists of multiple allied alliances. "
            "Choose the alliance you belong to by clicking the buttons below.\n\n"
            f"**Available Alliances:**\n{alliance_list}\n\n"
            "Please select your alliance below."
        )
    else:
        description = (
            f"Welcome to **{server_name}**!\n\n"
            "⚠️ **No alliances have been configured yet.**\n\n"
            "Please contact a server admin to set up alliances using `/addalliance`."
        )

    embed = discord.Embed(
        title=f"⚔️ Alliance Registration — {server_name}",
        description=description,
        color=discord.Color.from_rgb(150, 150, 150)
    )
    embed.set_footer(text="Select your alliance to get the role!")

    view = DynamicAllianceView(guild.id)
    await channel.send(embed=embed, view=view)


async def ensure_alliance_panel(guild):
    alliance_manager.load_settings()
    channel = find_text_channel(guild, Role_Assignment_Channel)
    if channel is None:
        return

    try:
        async for message in channel.history(limit=50):
            if message.author.id != guild.me.id:
                continue
            if not message.embeds:
                continue
            if "Alliance Registration" in message.embeds[0].title:
                return

        await create_alliance_panel(guild, channel)
    except discord.errors.HTTPException as e:
        if e.status == 429:
            print("⚠️ Rate limited. Waiting 60 seconds...")
            await asyncio.sleep(60)
        else:
            print(f"⚠️ Discord API Error: {e}")
    except Exception as e:
        print(f"⚠️ Error in ensure_alliance_panel: {e}")


async def refresh_alliance_panel(guild):
    alliance_manager.load_settings()
    channel = find_text_channel(guild, Role_Assignment_Channel)
    if channel is None:
        return

    try:
        async for message in channel.history(limit=50):
            if message.author.id == guild.me.id and message.embeds:
                if "Alliance Registration" in message.embeds[0].title:
                    await message.delete()

        await create_alliance_panel(guild, channel)
        print(f"[RoleAssignment] ✅ Panel refreshed for {guild.name}")
    except Exception as e:
        print(f"⚠️ Error refreshing alliance panel: {e}")
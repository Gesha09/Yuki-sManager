import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from config import TOKEN, Pannel_Checks
from welcome import send_welcome, send_goodbye
from roleassignment import AllianceView, ensure_alliance_panel
from scheduler import EventScheduler


class AllianceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.scheduler = None

    async def setup_hook(self):
        self.add_view(AllianceView())
        self.check_alliance_panel.start()
        self.scheduler = EventScheduler(self)

        # Clear any existing commands to avoid signature mismatches
        self.tree.clear_commands(guild=None)
        
        # Register slash commands
        self.tree.add_command(self.setlogchannel)
        self.tree.add_command(self.disablewar)
        self.tree.add_command(self.enablewar)
        self.tree.add_command(self.disablecsw)
        self.tree.add_command(self.enablecsw)

        # Sync slash commands to Discord
        await self.tree.sync()
        print("✅ Slash commands synced!")

    async def on_ready(self):
        print(f"✅ Logged in as {self.user.name} (ID: {self.user.id})")
        print(f"🌐 Connected to {len(self.guilds)} server(s)")

        await asyncio.sleep(5)
        for guild in self.guilds:
            await ensure_alliance_panel(guild)

    async def on_member_join(self, member):
        await send_welcome(member)

    async def on_member_remove(self, member):
        await send_goodbye(member)

    # ========================================================
    # SLASH COMMANDS (Admin Only, Ephemeral)
    # ========================================================

    @app_commands.command(
        name="setlogchannel",
        description="Set the channel for event reminders and war completions"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setlogchannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        self.scheduler.set_log_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message(
            f"✅ Event reminders and war completions will now go to {channel.mention}.",
            ephemeral=True
        )

    @app_commands.command(
        name="disablewar",
        description="Disable all war messages (reminders + completions) for today"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def disablewar(
        self,
        interaction: discord.Interaction,
        send_rest_message: bool = False
    ):
        """
        send_rest_message: If True, sends a 'No war today, take rest' embed to the log channel
        """
        self.scheduler.set_war_disabled_today(interaction.guild.id, True)

        if send_rest_message:
            await self.scheduler.send_rest_day_message(interaction.guild)
            await interaction.response.send_message(
                "⚠️ War messages are now **disabled** for today.\n"
                "A rest message has been sent to the log channel.\n"
                "They will auto-re-enable tomorrow.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "⚠️ War messages are now **disabled** for today (silently).\n"
                "They will auto-re-enable tomorrow.",
                ephemeral=True
            )

    @app_commands.command(
        name="enablewar",
        description="Re-enable war messages if they were disabled"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def enablewar(self, interaction: discord.Interaction):
        self.scheduler.set_war_disabled_today(interaction.guild.id, False)
        await interaction.response.send_message(
            "✅ War messages are now **enabled**.",
            ephemeral=True
        )

    @app_commands.command(
        name="disablecsw",
        description="Permanently disable Cross-Server War messages"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def disablecsw(self, interaction: discord.Interaction):
        self.scheduler.set_csw_disabled(interaction.guild.id, True)
        await interaction.response.send_message(
            "⚠️ **Cross-Server War** messages are now **disabled**.\n"
            "Use `/enablecsw` to turn them back on.",
            ephemeral=True
        )

    @app_commands.command(
        name="enablecsw",
        description="Re-enable Cross-Server War messages"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def enablecsw(self, interaction: discord.Interaction):
        self.scheduler.set_csw_disabled(interaction.guild.id, False)
        await interaction.response.send_message(
            "✅ **Cross-Server War** messages are now **enabled**.",
            ephemeral=True
        )

    # ========================================================
    # ERROR HANDLER (for missing permissions)
    # ========================================================
    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You need **Administrator** permission to use this command.",
                ephemeral=True
            )
        else:
            print(f"⚠️ Slash command error: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Something went wrong.",
                    ephemeral=True
                )

    # ========================================================
    # TASKS
    # ========================================================
    @tasks.loop(minutes=Pannel_Checks)
    async def check_alliance_panel(self):
        for guild in self.guilds:
            await ensure_alliance_panel(guild)

    @check_alliance_panel.before_loop
    async def before_panel_check(self):
        await self.wait_until_ready()


if __name__ == "__main__":
    bot = AllianceBot()
    bot.run(TOKEN)
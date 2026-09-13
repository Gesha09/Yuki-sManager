import discord
from discord import app_commands
from discord.ext import commands


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        self.bot.scheduler.set_log_channel(interaction.guild.id, channel.id)
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
        self.bot.scheduler.set_war_disabled_today(interaction.guild.id, True)

        if send_rest_message:
            await self.bot.scheduler.send_rest_day_message(interaction.guild)
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
        self.bot.scheduler.set_war_disabled_today(interaction.guild.id, False)
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
        self.bot.scheduler.set_csw_disabled(interaction.guild.id, True)
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
        self.bot.scheduler.set_csw_disabled(interaction.guild.id, False)
        await interaction.response.send_message(
            "✅ **Cross-Server War** messages are now **enabled**.",
            ephemeral=True
        )

    @disablewar.error
    @enablewar.error
    @setlogchannel.error
    @disablecsw.error
    @enablecsw.error
    async def on_error(
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


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
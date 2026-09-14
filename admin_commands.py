import discord
from discord import app_commands
from discord.ext import commands
from alliance_manager import AllianceManager, EMOJI_COLORS
from roleassignment import refresh_alliance_panel


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alliance_manager = AllianceManager()

    @app_commands.command(
        name="addalliance",
        description="Add a new alliance to this server"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def addalliance(
        self,
        interaction: discord.Interaction,
        name: str,
        emoji: str,
        auto_create_role: bool = True
    ):
        await interaction.response.defer(ephemeral=True)

        if emoji not in EMOJI_COLORS:
            await interaction.edit_original_response(
                content=f"❌ Unsupported emoji. Use one of: {' '.join(EMOJI_COLORS.keys())}"
            )
            return

        alliance = self.alliance_manager.add_alliance(
            interaction.guild.id,
            name,
            emoji
        )

        role_created = False
        if auto_create_role:
            role = await self.alliance_manager.create_role_for_alliance(
                interaction.guild,
                alliance
            )
            role_created = role is not None

        await refresh_alliance_panel(interaction.guild)

        await interaction.edit_original_response(
            content=(
                f"✅ Alliance **{emoji} {name}** added!\n"
                f"{'✅ Role auto-created' if role_created else '⚠️ Role not created'}\n"
                "✅ Alliance panel updated!"
            )
        )

    @app_commands.command(
        name="removealliance",
        description="Remove an alliance from this server"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def removealliance(
        self,
        interaction: discord.Interaction,
        name: str
    ):
        await interaction.response.defer(ephemeral=True)

        removed = self.alliance_manager.remove_alliance(interaction.guild.id, name)
        if removed:
            await refresh_alliance_panel(interaction.guild)
            await interaction.edit_original_response(
                content=f"✅ Alliance **{name}** removed.\n✅ Alliance panel updated!"
            )
        else:
            await interaction.edit_original_response(
                content=f"❌ Alliance **{name}** not found."
            )

    @app_commands.command(
        name="listalliances",
        description="Show all configured alliances for this server"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def listalliances(self, interaction: discord.Interaction):
        alliances = self.alliance_manager.get_alliances(interaction.guild.id)
        if not alliances:
            await interaction.response.send_message(
                "❌ No alliances configured. Use `/addalliance` to add one.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"⚔️ Alliances in {interaction.guild.name}",
            color=discord.Color.blue()
        )

        for alliance in alliances:
            role_mention = "❌ Not created"
            if alliance.get("role_id"):
                role = interaction.guild.get_role(alliance["role_id"])
                role_mention = role.mention if role else "❌ Deleted"

            embed.add_field(
                name=f"{alliance['emoji']} {alliance['name']}",
                value=f"Role: {role_mention}\nColor: `{alliance['color']}`",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="verifysetup",
        description="Check if all alliances and channels are properly configured"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def verifysetup(self, interaction: discord.Interaction):
        issues = self.alliance_manager.verify_setup(interaction.guild)

        if not issues["missing_roles"] and not issues["missing_channels"]:
            await interaction.response.send_message(
                "✅ **All systems operational!**\n"
                "All alliances and channels are properly configured.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚠️ Setup Issues Detected",
            color=discord.Color.orange()
        )

        if issues["missing_roles"]:
            embed.add_field(
                name="❌ Missing/Invalid Roles",
                value="\n".join(issues["missing_roles"]),
                inline=False
            )

        if issues["missing_channels"]:
            embed.add_field(
                name="❌ Missing/Invalid Channels",
                value="\n".join(issues["missing_channels"]),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="setservername",
        description="Set a custom display name for this server in bot messages"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setservername(
        self,
        interaction: discord.Interaction,
        name: str
    ):
        self.alliance_manager.set_server_display_name(interaction.guild.id, name)
        await interaction.response.send_message(
            f"✅ Server display name set to **{name}**",
            ephemeral=True
        )

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
        self.alliance_manager.set_log_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message(
            f"✅ Event reminders and war completions will now go to {channel.mention}.",
            ephemeral=True
        )

    @app_commands.command(
        name="disablewar",
        description="Disable all war messages for today"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def disablewar(
        self,
        interaction: discord.Interaction,
        send_rest_message: bool = False
    ):
        if send_rest_message:
            await interaction.response.defer(ephemeral=True)

        self.alliance_manager.set_war_disabled_today(interaction.guild.id, True)

        if send_rest_message:
            await self.bot.scheduler.send_rest_day_message(interaction.guild)
            await interaction.edit_original_response(
                content=(
                    "⚠️ War messages **disabled** for today.\n"
                    "Rest message sent to log channel.\n"
                    "Auto-re-enables tomorrow."
                )
            )
        else:
            await interaction.response.send_message(
                "⚠️ War messages **disabled** for today (silently).",
                ephemeral=True
            )

    @app_commands.command(
        name="enablewar",
        description="Re-enable war messages"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def enablewar(self, interaction: discord.Interaction):
        self.alliance_manager.set_war_disabled_today(interaction.guild.id, False)
        await interaction.response.send_message(
            "✅ War messages **enabled**.",
            ephemeral=True
        )

    @app_commands.command(
        name="disablecsw",
        description="Permanently disable Cross-Server War messages"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def disablecsw(self, interaction: discord.Interaction):
        self.alliance_manager.set_csw_disabled(interaction.guild.id, True)
        await interaction.response.send_message(
            "⚠️ **CSW** messages disabled.",
            ephemeral=True
        )

    @app_commands.command(
        name="enablecsw",
        description="Re-enable Cross-Server War messages"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def enablecsw(self, interaction: discord.Interaction):
        self.alliance_manager.set_csw_disabled(interaction.guild.id, False)
        await interaction.response.send_message(
            "✅ **CSW** messages enabled.",
            ephemeral=True
        )

    @addalliance.error
    @removealliance.error
    @listalliances.error
    @verifysetup.error
    @setservername.error
    @setlogchannel.error
    @disablewar.error
    @enablewar.error
    @disablecsw.error
    @enablecsw.error
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            if interaction.response.is_done():
                await interaction.edit_original_response(
                    content="❌ You need **Administrator** permission."
                )
            else:
                await interaction.response.send_message(
                    "❌ You need **Administrator** permission.",
                    ephemeral=True
                )
        else:
            print(f"⚠️ Command error: {error}")
            if interaction.response.is_done():
                await interaction.edit_original_response(
                    content="❌ Something went wrong."
                )
            else:
                await interaction.response.send_message(
                    "❌ Something went wrong.",
                    ephemeral=True
                )


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
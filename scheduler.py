import discord
import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from discord.ext import tasks
from config import (
    Events,
    Reminder_Lead_Time,
    TIMEZONE
)
from alliance_manager import AllianceManager

SETTINGS_FILE = "bot_settings.json"


class EventScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.alliance_manager = AllianceManager()

        self.sent_reminders = set()
        self.sent_completion_messages = set()

        self.check_events.start()

    def get_now(self):
        return datetime.now(ZoneInfo(TIMEZONE))

    def get_log_channel(self, guild):
        settings = self.alliance_manager.get_server_settings(guild.id)
        channel_id = settings.get("log_channel_id")
        if not channel_id:
            return None
        return guild.get_channel(channel_id)

    async def send_reminder(self, guild, event_name, event_time, minutes_before, event_type):
        # ✅ Reload settings to get the latest log channel
        self.alliance_manager.load_settings()
        
        settings = self.alliance_manager.get_server_settings(guild.id)

        if event_type == "cross_server_war" and settings.get("csw_disabled", False):
            print(f"[Scheduler] ⚠️ CSW disabled for {guild.name}. Skipping {event_name}.")
            return

        if event_type in ("alliance_war", "cross_server_war") and settings.get("war_disabled_today", False):
            print(f"[Scheduler] ⚠️ Wars disabled today for {guild.name}. Skipping {event_name}.")
            return

        channel = self.get_log_channel(guild)
        if not channel:
            print(f"⚠️ No log channel set for {guild.name}. Use /setlogchannel.")
            return

        if minutes_before == 0:
            title = f"🚨 {event_name} IS STARTING NOW!"
            description = (
                f"**{event_name}** is starting **now!**\n\n"
                "⚔️ Get ready and head into battle!\n\n"
                "**Good luck everyone! 🔥**"
            )
        else:
            title = f"⏰ {event_name} Reminder"
            description = (
                f"**{event_name}** starts in **{minutes_before} minutes!**\n\n"
                f"🕐 Start time: **{event_time} IST**\n\n"
                "Get ready and don't miss it! ⚔️🔥"
            )

        embed = discord.Embed(title=title, description=description, color=discord.Color.orange())
        embed.set_footer(text=f"{self.alliance_manager.get_server_name(guild)} • India Time")

        await channel.send(content="@everyone", embed=embed)

    async def send_rest_day_message(self, guild):
        # ✅ Reload settings
        self.alliance_manager.load_settings()
        
        channel = self.get_log_channel(guild)
        if not channel:
            print(f"[Scheduler] ⚠️ No log channel for {guild.name}. Cannot send rest message.")
            return

        server_name = self.alliance_manager.get_server_name(guild)

        embed = discord.Embed(
            title="🛌 No War Today — Take a Rest!",
            description=(
                f"There are **no wars scheduled for today** in **{server_name}**.\n\n"
                "Relax, recharge, and enjoy the peace, warriors! 🌙\n\n"
                "**You've earned it. ⚔️💤**"
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"{server_name} • India Time")

        try:
            await channel.send(content="@everyone", embed=embed)
            print(f"[Scheduler] ✅ Rest message sent to #{channel.name} in {guild.name}")
        except Exception as error:
            print(f"[Scheduler] ❌ Error sending rest message: {error}")

    async def send_completion_messages(self, guild, event_name, event_type):
        # ✅ Reload settings
        self.alliance_manager.load_settings()
        
        settings = self.alliance_manager.get_server_settings(guild.id)

        if settings.get("war_disabled_today", False):
            print(f"[Scheduler] ⚠️ Wars disabled today for {guild.name}. Skipping completion for {event_name}.")
            return

        if event_type == "cross_server_war" and settings.get("csw_disabled", False):
            print(f"[Scheduler] ⚠️ CSW disabled for {guild.name}. Skipping completion for {event_name}.")
            return

        if event_type not in ("alliance_war", "cross_server_war"):
            return

        server_name = self.alliance_manager.get_server_name(guild)

        if event_type == "alliance_war":
            title = "⚔️ Alliance War Complete!"
            message = (
                f"**{event_name} has ended!**\n\n"
                "That was an intense battle! 🔥\n\n"
                "Thank you to everyone who participated and gave it their all.\n\n"
                "Every contribution matters.\n\n"
                "**Excellent work, warriors! ⚔️🔥**\n"
                "Rest up — we'll fight again!"
            )
        else:
            title = "🌐⚔️ Cross-Server War Complete!"
            message = (
                f"**{event_name} has ended!**\n\n"
                "What an intense battle! 🔥\n\n"
                "Thank you to everyone who participated in the Cross-Server Alliance War.\n\n"
                "Every contribution counts.\n\n"
                "**Great work, everyone! ⚔️🌐**"
            )

        channel = self.get_log_channel(guild)
        if not channel:
            print(f"[Scheduler] ❌ No log channel for {guild.name}. Use /setlogchannel.")
            return

        embed = discord.Embed(title=title, description=message, color=discord.Color.gold())
        embed.set_footer(text=f"{server_name} • India Time")

        try:
            await channel.send(embed=embed)
            print(f"[Scheduler] ✅ Completion sent to #{channel.name} in {guild.name}")
        except Exception as error:
            print(f"[Scheduler] ❌ Error sending completion: {error}")

    @tasks.loop(seconds=5)
    async def check_events(self):
        now = self.get_now()
        current_date = now.strftime("%Y-%m-%d")

        for guild_id, settings in self.alliance_manager.servers.items():
            if settings.get("war_disabled_today", False):
                disabled_date = settings.get("war_disabled_date")
                if disabled_date and disabled_date != current_date:
                    settings["war_disabled_today"] = False
                    settings["war_disabled_date"] = None
                    print(f"[Scheduler] ✅ New day. War messages re-enabled for guild {guild_id}.")
                    self.alliance_manager.save_settings()

        for event_name, event_data in Events.items():
            event_type = event_data.get("type", "raid")

            if event_type in ("alliance_war", "cross_server_war"):
                event_time = event_data["start"]
                duration_minutes = 0
            else:
                event_time = event_data["time"]
                duration_minutes = event_data.get("duration_in_minutes", 0)

            try:
                event_hour, event_minute = map(int, event_time.split(":"))
            except ValueError:
                print(f"⚠️ Invalid event time for {event_name}: {event_time}")
                continue

            event_datetime = now.replace(hour=event_hour, minute=event_minute, second=0, microsecond=0)
            if event_datetime < now:
                event_datetime += timedelta(days=1)

            seconds_until = (event_datetime - now).total_seconds()

            for reminder in Reminder_Lead_Time:
                reminder_seconds = reminder * 60
                if reminder_seconds - 5 <= seconds_until <= reminder_seconds + 5:
                    reminder_key = (current_date, event_name, reminder)
                    if reminder_key in self.sent_reminders:
                        continue

                    for guild in self.bot.guilds:
                        try:
                            await self.send_reminder(guild, event_name, event_time, reminder, event_type)
                        except Exception as e:
                            print(f"❌ Failed to send {event_name} to {guild.name}: {e}")
                        else:
                            self.sent_reminders.add(reminder_key)

            if event_type not in ("alliance_war", "cross_server_war"):
                continue

            end_time = event_data["end"]
            try:
                end_hour, end_minute = map(int, end_time.split(":"))
            except ValueError:
                print(f"❌ Invalid end time for {event_name}: {end_time}")
                continue

            event_end = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
            second_since_end = (now - event_end).total_seconds()

            if 0 <= second_since_end < 30:
                completion_key = (current_date, event_name)
                if completion_key in self.sent_completion_messages:
                    continue

                self.sent_completion_messages.add(completion_key)

                for guild in self.bot.guilds:
                    try:
                        await self.send_completion_messages(guild, event_name, event_type)
                    except Exception as e:
                        print(f"[Scheduler] ❌ Completion error in {guild.name}: {e}")

    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()

    def stop(self):
        self.check_events.cancel()
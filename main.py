import asyncio
import discord
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
    # ADMIN COMMANDS FOR EVENT LOGS
    # ========================================================
    @commands.command(name="setlogchannel")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setlogchannel(self, ctx, channel: discord.TextChannel):
        self.scheduler.set_log_channel(ctx.guild.id, channel.id)
        await ctx.send(f"✅ Event reminders and war completions will now go to {channel.mention}.")

    @commands.command(name="disablewar")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def disablewar(self, ctx, option: str = None):
        self.scheduler.set_war_disabled_today(ctx.guild.id, True)

        if option and option.lower() == "rest":
            await self.scheduler.send_rest_day_message(ctx.guild)
            await ctx.send(f"⚠️ Wars **disabled** for today in **{ctx.guild.name}**. Rest message sent. Auto-re-enables tomorrow.")
        else:
            await ctx.send(f"⚠️ Wars **disabled** for today in **{ctx.guild.name}** (silently). Auto-re-enables tomorrow.")

    @commands.command(name="enablewar")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def enablewar(self, ctx):
        self.scheduler.set_war_disabled_today(ctx.guild.id, False)
        await ctx.send(f"✅ Wars **enabled** for **{ctx.guild.name}**.")

    @commands.command(name="disablecsw")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def disablecsw(self, ctx):
        self.scheduler.set_csw_disabled(ctx.guild.id, True)
        await ctx.send(f"⚠️ **CSW** messages disabled for **{ctx.guild.name}**. Use `!enablecsw` to re-enable.")

    @commands.command(name="enablecsw")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def enablecsw(self, ctx):
        self.scheduler.set_csw_disabled(ctx.guild.id, False)
        await ctx.send(f"✅ **CSW** messages enabled for **{ctx.guild.name}**.")
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
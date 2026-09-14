import asyncio
import discord
from discord.ext import commands, tasks
from config import TOKEN, Pannel_Checks
from welcome import send_welcome, send_goodbye
from roleassignment import ensure_alliance_panel
from scheduler import EventScheduler


class AllianceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.scheduler = None

    async def setup_hook(self):
        self.check_alliance_panel.start()
        self.scheduler = EventScheduler(self)

        # Load slash commands from cog
        await self.load_extension("admin_commands")

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
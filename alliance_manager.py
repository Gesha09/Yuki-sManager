import discord
import json
import os
from typing import List, Dict, Optional

SETTINGS_FILE = "bot_settings.json"

EMOJI_COLORS = {
    "🟨": "#FFD700",
    "🟪": "#9B59B6",
    "🟥": "#E74C3C",
    "🟦": "#3498DB",
    "🟩": "#2ECC71",
    "🟧": "#F39C12",
    "⬛": "#2C3E50",
    "⬜": "#ECF0F1",
    "🟫": "#8B4513",
}


class AllianceManager:
    def __init__(self):
        self.servers = {}
        self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    for guild_id_str, settings in data.get("servers", {}).items():
                        self.servers[int(guild_id_str)] = settings
                print(f"[AllianceManager] ✅ Loaded settings for {len(self.servers)} server(s)")
            else:
                print(f"[AllianceManager] ℹ️ {SETTINGS_FILE} not found. Creating fresh.")
                self.save_settings()
        except Exception as e:
            print(f"[AllianceManager] ⚠️ Error loading settings: {e}")
            self.servers = {}

    def save_settings(self):
        try:
            data = {"servers": {str(k): v for k, v in self.servers.items()}}
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[AllianceManager] ⚠️ Error saving settings: {e}")

    def get_server_settings(self, guild_id: int) -> Dict:
        if guild_id not in self.servers:
            self.servers[guild_id] = {
                "server_display_name": None,
                "log_channel_id": None,
                "csw_disabled": False,
                "war_disabled_today": False,
                "war_disabled_date": None,
                "alliances": []
            }
        return self.servers[guild_id]

    def get_server_name(self, guild: discord.Guild) -> str:
        settings = self.get_server_settings(guild.id)
        return settings.get("server_display_name") or guild.name

    def get_alliances(self, guild_id: int) -> List[Dict]:
        settings = self.get_server_settings(guild_id)
        return settings.get("alliances", [])

    def add_alliance(
        self,
        guild_id: int,
        name: str,
        emoji: str,
        color: Optional[str] = None,
        role_id: Optional[int] = None
    ) -> Dict:
        settings = self.get_server_settings(guild_id)
        alliances = settings.get("alliances", [])

        if not color:
            color = EMOJI_COLORS.get(emoji, "#95A5A6")

        alliance = {
            "name": name,
            "role_id": role_id,
            "emoji": emoji,
            "color": color,
            "chat_channel_id": None
        }

        alliances.append(alliance)
        settings["alliances"] = alliances
        self.save_settings()
        return alliance

    def remove_alliance(self, guild_id: int, name: str) -> bool:
        settings = self.get_server_settings(guild_id)
        alliances = settings.get("alliances", [])
        initial_count = len(alliances)

        settings["alliances"] = [a for a in alliances if a["name"] != name]
        self.save_settings()
        return len(settings["alliances"]) < initial_count

    def update_alliance_role_id(self, guild_id: int, alliance_name: str, role_id: int):
        settings = self.get_server_settings(guild_id)
        for alliance in settings.get("alliances", []):
            if alliance["name"] == alliance_name:
                alliance["role_id"] = role_id
                self.save_settings()
                return True
        return False

    def set_log_channel(self, guild_id: int, channel_id: int):
        settings = self.get_server_settings(guild_id)
        settings["log_channel_id"] = channel_id
        self.save_settings()

    def set_server_display_name(self, guild_id: int, name: str):
        settings = self.get_server_settings(guild_id)
        settings["server_display_name"] = name
        self.save_settings()

    def set_csw_disabled(self, guild_id: int, disabled: bool):
        settings = self.get_server_settings(guild_id)
        settings["csw_disabled"] = disabled
        self.save_settings()

    def set_war_disabled_today(self, guild_id: int, disabled: bool):
        settings = self.get_server_settings(guild_id)
        settings["war_disabled_today"] = disabled
        if disabled:
            from datetime import datetime
            from zoneinfo import ZoneInfo
            settings["war_disabled_date"] = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
        else:
            settings["war_disabled_date"] = None
        self.save_settings()

    async def create_role_for_alliance(
        self,
        guild: discord.Guild,
        alliance: Dict
    ) -> Optional[discord.Role]:
        try:
            color = discord.Color(int(alliance["color"].lstrip("#"), 16))
            role = await guild.create_role(
                name=alliance["name"],
                color=color,
                reason=f"Auto-created for alliance: {alliance['name']}"
            )
            self.update_alliance_role_id(guild.id, alliance["name"], role.id)
            print(f"[AllianceManager] ✅ Created role '{alliance['name']}' in {guild.name}")
            return role
        except discord.Forbidden:
            print(f"[AllianceManager] ❌ Missing permissions to create role in {guild.name}")
            return None
        except Exception as e:
            print(f"[AllianceManager] ❌ Error creating role: {e}")
            return None

    def verify_setup(self, guild: discord.Guild) -> Dict[str, List[str]]:
        issues = {"missing_roles": [], "missing_channels": []}
        settings = self.get_server_settings(guild.id)

        for alliance in settings.get("alliances", []):
            role_id = alliance.get("role_id")
            if not role_id:
                issues["missing_roles"].append(f"{alliance['emoji']} {alliance['name']} (no role configured)")
            else:
                role = guild.get_role(role_id)
                if not role:
                    issues["missing_roles"].append(f"{alliance['emoji']} {alliance['name']} (role deleted)")

        log_channel_id = settings.get("log_channel_id")
        if not log_channel_id:
            issues["missing_channels"].append("Event log channel not set")
        else:
            channel = guild.get_channel(log_channel_id)
            if not channel:
                issues["missing_channels"].append("Event log channel deleted")

        return issues
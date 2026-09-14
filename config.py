import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN not found! Ensure your .env file exists and contains 'DISCORD_TOKEN=your_token'")

Role_Assignment_Channel = "role-assignment"
Role_Log_Channel = "role-log"
Welcome_Channel = "welcome-log"

Pannel_Checks = 10

TIMEZONE = "Asia/Kolkata"

Events = {
    "🌅 Morning Raid": {
        "time": "09:15",
        "type": "raid",
        "duration_in_minutes": 60
    },
    "🌇 Evening Raid": {
        "time": "16:15",
        "type": "raid",
        "duration_in_minutes": 60
    },
    "⚔️ Alliance War": {
        "start": "17:30",
        "end": "18:15",
        "type": "alliance_war"
    },
    "🌐 Cross-Server War": {
        "start": "18:30",
        "end": "19:15",
        "type": "cross_server_war"
    },
}

Reminder_Lead_Time = [10, 0]
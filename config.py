import os
from pathlib import Path
from dotenv import load_dotenv

# Robustly find and load the .env file in the same directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN not found! Ensure your .env file exists and contains 'DISCORD_TOKEN=your_token'")

#===============================================================================
#Discord roles name
#===============================================================================
Judgement_role_name = "Judgement"
Abbysal_role_name = "Abyssal Tides"

#===============================================================================
#Discord channel name (Only for Welcome & Role Assignment)
#===============================================================================
Role_Assignment_Channel = "role-assignment"
Role_Log_Channel = "role-log"
Welcome_Channel = "welcome-log"

#===============================================================================
#how often bot checks the channel in minutes
#===============================================================================
Pannel_Checks = 10

#===============================================================================
#EVENT REMINDERS
#===============================================================================
# TimeZone for the event reminders is India Standard Time (IST) which is UTC+5:30
TIMEZONE = "Asia/Kolkata"

#===============================================================================
#EVENT TIMES
#===============================================================================
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

#===============================================================================
#how many minutes before the event the bot should send a reminder
#===============================================================================
Reminder_Lead_Time = [10, 0]  # in minutes before each event start and when it starts
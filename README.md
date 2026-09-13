# ⚔️ The Judgement of Abyssal Tides — Discord Bot

A Discord bot designed to automate event reminders, role management, and war completion announcements for allied gaming communities. All event timings are based on India Standard Time (IST).

---

## ✨ Features

- **🎉 Welcome & Goodbye Messages**: Automatically greets new members and bids farewell to those who leave.
- **🟨🟪 Interactive Role Assignment**: A persistent button panel for members to join or leave the "Judgement" or "Abyssal Tides" alliances, with dedicated logging.
- **⏰ Automated Event Reminders**: Sends `@everyone` pings 5 minutes before and exactly at the start of Morning Raids, Evening Raids, Alliance Wars, and Cross-Server Wars.
- **🏁 War Completion Messages**: Automatically sends a celebratory embed to both `judgement-chat` and `abyssal-chat` when a war ends, preventing duplicates.

---

## 📋 Prerequisites

1. **Python 3.10 or higher** installed on your system.
2. A **Discord Bot Token** from the [Discord Developer Portal](https://discord.com/developers/applications).
3. **Required Intents** enabled in the Developer Portal:
   - ✅ Message Content Intent
   - ✅ Server Members Intent

---

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
---
### Configure Environment
Create a file named .env in the root directory and add your bot token:

```bash
DISCORD_TOKEN=your_bot_token_here
```
---

### Server Setup
---

- Ensure your Discord server has the following Roles and Channels (exact names):
- Roles: Judgement, Abyssal Tides (Bot role must be higher than these in the hierarchy)
- Channels:
    welcome-log (Welcome/Goodbye messages)
    role-assignment (Role selection panel)
    role-log (Role assignment tracking)
    event-reminder (Event reminders)
    judgement-chat & abyssal-chat (War completion messages)

---

### Run the Bot
---

```bash
python main.py
```
---

### 🎮 Command List
---

(Requires Administrator permissions)
|Command|Description|
|---|---|
!setlogchannel #channel | Sets a single channel for all event reminders and war completions.|
!disablewar | Silently disables all war messages (reminders + completions) for the day. |
!disablewar rest | Disables war messages and sends a "take a rest" embed to the log channel. |
!enablewar | Manually re-enables war messages before midnight. |
!disablecsw | Permanently disables Cross-Server War messages until re-enabled. |
!enablecsw | Re-enables Cross-Server War messages. |

---

### ℹ️ About
---

This bot was built to streamline community management for "The Judgement of Abyssal Tides" alliance. It handles the repetitive tasks of pinging for events, managing alliance roles, and celebrating victories, allowing leaders and members to focus on the game.

---

### 🤝 Contributing
---

- Contributions are welcome! To contribute:
- Fork the repository.
- Create a new branch (git checkout -b feature/YourFeature).
- Commit your changes (git commit -m 'Add YourFeature').
- Push to the branch and open a Pull Request.

---

### 📜 License
---

This project is licensed under the MIT License. You are free to use, modify, and distribute this code, provided the original copyright notice is included. See the LICENSE file for details.

---

made with 💕💕 by Gesha
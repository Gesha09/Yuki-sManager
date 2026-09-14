# ⚔️ The Judgement of Abyssal Tides — Discord Bot

A Discord bot designed to automate event reminders, role management, and war completion announcements for allied gaming communities. All event timings are based on India Standard Time (IST).

---

## 📖 Contents
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Setup](#️-setup)
- [Command List](#-command-list)
- [About](#ℹ️-about)
- [Contributing](#-contributing)
- [Licensce](#-license)


---

## ✨ Features

- **🎉 Welcome & Goodbye Messages**: Automatically greets new members and bids farewell to those who leave.
- **🟨🟪 Interactive Role Assignment**: A persistent button panel for members to join or leave the "Judgement" or "Abyssal Tides" alliances or any configured Alliance , with dedicated logging.
- **⏰ Automated Event Reminders**: Sends `@everyone` pings 10 minutes before and exactly at the start of Morning Raids, Evening Raids, Alliance Wars, and Cross-Server Wars.(in Ist)
- **🏁 War Completion Messages**: Automatically sends a celebratory embed to the configured server channel when a war ends.

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
- Roles: Judgement, Abyssal Tides (Bot role must be higher than these in the hierarchy)(or when adding alliance you will have option to auto create Roles).
- Make sure you add alliance (one or more) and set log channel to any channel you wish your reminder messages to appear.
- Channels:
   - welcome-log (Welcome/Goodbye messages)
   - role-assignment (Role selection panel)
   - role-log (Role assignment tracking)

---

### Run the Bot
---

```bash
python main.py
```
---

## 🎮 Command List
---

(Requires Administrator permissions)
|Command|Description|
|---|---|
/setlogchannel [channel] | Sets a single channel for all event reminders and war completions.|
/disablewar | Silently disables all war messages (reminders + completions) for the day. |
/disablewar [rest] | Disables war messages and sends a "take a rest" embed to the log channel. |
/enablewar | Manually re-enables war messages before midnight. |
/disablecsw | Permanently disables Cross-Server War messages until re-enabled. |
/enablecsw | Re-enables Cross-Server War messages. |
/addalliance [alliance_name][emoji][create_new_role] | add alliance and createes roles color accroding to emoji color |
removealliance [alliance_name] | remove alliance from the server |


---

## ℹ️ About
---

This bot was built to streamline community management for "The Judgement of Abyssal Tides" alliance. It handles the repetitive tasks of pinging for events, managing alliance roles, and celebrating victories, allowing leaders and members to focus on the game.

---

## 🤝 Contributing
---

- Contributions are welcome! To contribute:
- Fork the repository.
- Create a new branch (git checkout -b feature/YourFeature).
- Commit your changes (git commit -m 'Add YourFeature').
- Push to the branch and open a Pull Request.

---

## 📜 License
---

This project is licensed under the MIT License. You are free to use, modify, and distribute this code, provided the original copyright notice is included. See the LICENSE file for details.

---

made with 💕💕 by Gesha
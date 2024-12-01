import discord 
from discord import app_commands
from discord.ext import commands
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone, timedelta
from colorama import Fore, Style

import re
import os
import json
import requests
import asyncio
import threading
import time
import typing



#My own imports
import config 
from render import render, bulk_render

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents = intents)

bot.start_time = time.time()
bot.commands_executed = 0
bot.servers = []


#Ui init
window = tk.Tk()
window.title("Ludicolo admin panel ong fr")

# Global bot thread and state
bot_thread = None
bot_running = False

# =============================================================================================================================================


#Actual UI stuff :nerd:

# ===== Tkinter UI Initialization =====
tab_control = ttk.Notebook(window)
bot_control_tab = ttk.Frame(tab_control)
tab_control.add(bot_control_tab, text="Ludicolo management")

# Bot Metrics 
bot_metrics_tab = ttk.Frame(tab_control)
tab_control.add(bot_metrics_tab, text="Ludicolo Metrics")

# Loaded Commands Tab
commands_tab = ttk.Frame(tab_control)
tab_control.add(commands_tab, text="Loaded Commands")
tab_control.pack(expand=1, fill="both")

# ===== Bot Control Panel =====
bot_control_frame = ttk.LabelFrame(bot_control_tab, text="Bot Control Panel")
bot_control_frame.pack(fill="x", padx=10, pady=5)

def start_bot():
    global bot_thread, bot_running
    if not bot_running:
        log_message(" {Fore.GREEN} Starting Ludicolo :happy:...{Style.RESET_ALL}")
        status_label.config(text="Ludicolo is alive.... For now", fg="green")
        bot_running = True
        bot_thread = threading.Thread(target=run_discord_bot)
        bot_thread.start()

def stop_bot():
    global bot_running
    if bot_running:
        log_message("{Fore.RED}Stopping Ludicolo :sad: ...{Style.RESET_ALL}")
        status_label.config(text="Ludicolo is DEAD DEAD AS HELL DUDE", fg="red")
        bot_running = False
        asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)

def resync_commands():
    global bot_running
    if bot_running:
        try:
            log_message("Resyncing commands...")
            asyncio.run_coroutine_threadsafe(bot.tree.sync(), bot.loop)
            update_commands_list()
            log_message("Commands resynced.")
        except Exception as e:
            log_message(f"Error resyncing commands: {e}")

start_button = tk.Button(bot_control_frame, text="Start Bot", command=start_bot)
stop_button = tk.Button(bot_control_frame, text="Stop Bot", command=stop_bot)
status_label = tk.Label(bot_control_frame, text="Bot Status: Offline", fg="red")
start_button.grid(row=0, column=0, padx=5, pady=5)
stop_button.grid(row=0, column=1, padx=5, pady=5)
status_label.grid(row=0, column=2, padx=5, pady=5)

# ===== Log Window =====
log_frame = ttk.LabelFrame(bot_control_tab, text="Log Window")
log_frame.pack(fill="both", expand=True, padx=10, pady=5)
log_text = tk.Text(log_frame, height=10, width=80, bg="#1e1e1e", fg="#ffffff")
log_text.pack(side="left", fill="both", expand=True)

log_scroll = tk.Scrollbar(log_frame)
log_scroll.pack(side="right", fill="y")
log_text.config(yscrollcommand=log_scroll.set)
log_scroll.config(command=log_text.yview)

def clear_logs():
    log_text.delete(1.0, tk.END)

clear_log_button = tk.Button(log_frame, text="Clear Logs", command=clear_logs)
clear_log_button.pack(pady=5)

# ===== Bot Metrics/Stats =====
metrics_frame = ttk.LabelFrame(bot_metrics_tab, text="Bot Metrics/Stats")
metrics_frame.pack(fill="x", padx=10, pady=5)
uptime_label = tk.Label(metrics_frame, text="Uptime: 0 seconds")
commands_executed_label = tk.Label(metrics_frame, text="Commands Executed: 0")
servers_label = tk.Label(metrics_frame, text="Servers:")
uptime_label.grid(row=0, column=0, padx=5, pady=5)
commands_executed_label.grid(row=0, column=1, padx=5, pady=5)
servers_label.grid(row=1, column=0, padx=5, pady=5)

# Server List
server_listbox_frame = ttk.Frame(metrics_frame)
server_listbox_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
server_listbox = tk.Listbox(server_listbox_frame, height=10, width=60, bg="#1e1e1e", fg="#ffffff")
server_listbox.pack(side="left", fill="y")
server_scroll = tk.Scrollbar(server_listbox_frame)
server_scroll.pack(side="right", fill="y")
server_listbox.config(yscrollcommand=server_scroll.set)
server_scroll.config(command=server_listbox.yview)


# ===== Loaded Commands Tab =====
commands_frame = ttk.LabelFrame(commands_tab, text="Loaded Commands")
commands_frame.pack(fill="both", expand=True, padx=10, pady=5)

commands_listbox_frame = ttk.Frame(commands_frame)
commands_listbox_frame.pack(fill="both", expand=True)

commands_listbox = tk.Listbox(commands_listbox_frame, height=15, width=60, bg="#1e1e1e", fg="#ffffff")
commands_listbox.pack(side="left", fill="y")

commands_scroll = tk.Scrollbar(commands_listbox_frame)
commands_scroll.pack(side="right", fill="y")

resync_commands_button = ttk.Button(commands_frame, text="Resync commands", command=resync_commands)
resync_commands_button.pack(side="right")

commands_listbox.config(yscrollcommand=commands_scroll.set)
commands_scroll.config(command=commands_listbox.yview)


# =============================================================================================================================================
# Actual UI init ig we'll define the ui itself more precisely later on


def run_discord_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        bot.tree.sync()
        bot.run(config.BOT_TOKEN)
    except Exception as e:
        log_message(f"{Fore.RED}Error running bot: {Style.RESET_ALL}{e}")

color_code_pattern = re.compile(r'(\x1b\[\d+;?\d*m)')


#That's super ugly huh? You're welcome !
log_text.tag_configure("black", foreground="black")
log_text.tag_configure("red", foreground="red")
log_text.tag_configure("green", foreground="green2")
log_text.tag_configure("yellow", foreground="gold")
log_text.tag_configure("blue", foreground="blue")
log_text.tag_configure("magenta", foreground="magenta")
log_text.tag_configure("cyan", foreground="cyan")
log_text.tag_configure("reset", foreground="white")

color_map = {
    "{Fore.BLACK}": "black",
    "{Fore.RED}": "red",
    "{Fore.GREEN}": "green",
    "{Fore.YELLOW}": "yellow",
    "{Fore.BLUE}": "blue",
    "{Fore.MAGENTA}": "magenta",
    "{Fore.CYAN}": "cyan",
    "{Fore.WHITE}": "white",
    "{Style.RESET_ALL}": "reset"
}

def log_message(message):
    tag = "reset"
    message = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
    parts = []
    for keyword, color_tag in color_map.items():
        if keyword in message:
            message = message.replace(keyword, f"|||{color_tag}|||")
    
    parts = message.split("|||")
    
    for part in parts:
        if part in color_map.values():
            tag = part
        else:
            log_text.insert(tk.END, part, tag)
    
    log_text.insert(tk.END, "\n")
    log_text.see(tk.END)

bot.log_message = log_message #Global export of my own logs to make them available for the cogs


def update_metrics():
    if bot.is_ready():
        uptime = time.time() - bot.start_time
        uptime_label.config(text=f"Uptime: {int(uptime)} seconds")
        commands_executed_label.config(text=f"Commands Executed: {bot.commands_executed}")
        
        server_listbox.delete(0, tk.END)
        for server in bot.servers:
            server_listbox.insert(tk.END, server)

def update_commands_list():
    commands_listbox.delete(0, tk.END)
    try:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "utils.py":
                commands_listbox.insert(tk.END, f"{filename[:-3]}")
    except Exception as e:
        log_message(f"Error while updating commands list: {e}")
    #For now only the help command is listed here, I'll prob move all the discord commands to cogs to make the code cleaner but also for them to be listed here.



"""

This is just a large chunk of functions I'll need later on so I'll just define them here, the actual discord commands are later in the code

"""




@bot.event
async def on_ready():
    bot.start_time = time.time()
    bot.servers = [guild.name for guild in bot.guilds]
    update_metrics()
    log_message(f'Bot connected as {bot.user.name}')
    try:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "utils.py":
                await bot.load_extension(f"cogs.{filename[:-3]}")
                log_message(f'Loaded {filename}')
        log_message(f'Loaded Everything, ready to go!')
    except Exception as e:
        log_message(f"Failed to load cog {filename}: {e}")

@bot.event
async def on_app_command_completion(interaction, command):
    bot.commands_executed += 1 #Yeah I tracked the number of commands ran bcs smh the bot kept crashing but apparently it was due tue the host so that part is prob useless nowadays
    log_message(f'Command executed: {command.name} succesfuli') #Dw the typo is intentionnal COZ FUNIIII
    update_metrics()

update_commands_list()
window.mainloop()
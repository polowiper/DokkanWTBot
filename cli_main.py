import discord
from discord.ext import commands
from datetime import datetime
from colorama import Fore, Style

import os

import config

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents = intents)

def log_message(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

async def resync_commands():
    try:
        log_message("Resyncing commands...")
        await bot.tree.sync()
        log_message("Commands resynced.")
    except Exception as e:
        log_message(f"Error resyncing commands: {e}")


def run_discord_bot():
    try:
        bot.run(config.BOT_TOKEN)
    except Exception as e:
        log_message(f"{Fore.RED}Error running bot: {Style.RESET_ALL}{e}")

bot.log_message = log_message #Global export of my own logs to make them available for the cogs




@bot.event
async def on_ready():
    log_message(f'Bot connected as {bot.user.name}')
    try:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "utils.py":
                await bot.load_extension(f"cogs.{filename[:-3]}")
                log_message(f'Loaded {filename}')
        log_message(f'Loaded Everything, syncing commands:')
        await resync_commands()
    except Exception as e:
        log_message(f"Failed to load cog {filename}: {e}")

run_discord_bot()

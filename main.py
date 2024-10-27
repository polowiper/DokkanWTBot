import discord 
from discord import app_commands
from discord.ext import commands
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone, timedelta


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


output_dir = 'top100_data'

#Ui init
window = tk.Tk()
window.title("Ludicolo admin panel ong fr")

# Global bot thread and state
bot_thread = None
bot_running = False

# =============================================================================================================================================
# Actual UI init ig we'll define the ui itself more precisely later on
def start_bot():
    global bot_thread, bot_running
    if not bot_running:
        log_message("Starting Ludicolo :happy:...")
        status_label.config(text="Ludicolo is alive.... For now", fg="green")
        bot_running = True
        bot_thread = threading.Thread(target=run_discord_bot)
        bot_thread.start()

def stop_bot():
    global bot_running
    if bot_running:
        log_message("Stopping Ludicolo :sad: ...")
        status_label.config(text="Ludicolo is DEAD DEAD AS HELL DUDE", fg="red")
        bot_running = False
        asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)


def run_discord_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        bot.run(config.BOT_TOKEN)
    except Exception as e:
        log_message(f"Error running bot: {e}")

def log_message(message):
    log_text.insert(tk.END, f"{message}\n")
    log_text.see(tk.END)


def clear_logs():
    log_text.delete(1.0, tk.END)


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
    for command in bot.commands:
        commands_listbox.insert(tk.END, f"{command.name}")
    #For now only the help command is listed here, I'll prob move all the discord commands to cogs to make the code cleaner but also for them to be listed here.


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

commands_listbox.config(yscrollcommand=commands_scroll.set)
commands_scroll.config(command=commands_listbox.yview)

"""

This is just a large chunk of functions I'll need later on so I'll just define them here, the actual discord commands are later in the code

"""



if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)

def load_discord_users():
    if not os.path.exists('discord_users.json'):
        with open('discord_users.json', 'w') as f:
            json.dump({}, f)
    with open('discord_users.json', 'r') as f:
        return json.load(f)

def save_discord_users(discord_users):
    with open('discord_users.json', 'w') as f:
        json.dump(discord_users, f, indent=5)

def latest_fetch():
    output_dir = "fetches"
    i = 0
    while True:
        filename = f"fetch{i}.json"
        if not os.path.exists(os.path.join(output_dir, filename)):
            break
        i += 1
    return f"{output_dir}/fetch{i-1}.json" if os.path.exists(os.path.join(output_dir, f"fetch{i-1}.json")) else None

def time_data():
    latest_fetch_path = latest_fetch()

    if latest_fetch_path:
        with open(latest_fetch_path, 'r') as file:
            data = json.load(file)
#            print("Data loaded from the latest fetch file:")
            ping = requests.get('https://dokkan.wiki/api/budokai/55') #That's where you'll need your API_KEY 
            ping.raise_for_status()
            start_end = ping.json()
            start = datetime.utcfromtimestamp(start_end["start_at"]).replace(tzinfo=timezone.utc) 
            end = datetime.utcfromtimestamp(start_end["end_at"]).replace(tzinfo=timezone.utc) 
            update = datetime.utcfromtimestamp(data["rank1000_updated_at"]).replace(tzinfo=timezone.utc)
            #update = datetime.utcfromtimestamp(data[f"top{100 if rank<=100 else 1000 if 100<rank<=1000 else 10000}_updated_at"]).replace(tzinfo=timezone.utc)
            total = end - start
            left = end - update
            elapsed = update - start
            return update, start, end, total, left, elapsed
    else:
        print("No fetch files found in the directory.")
        return None, None, None, None, None, None
    #yeah it's fucking ugly but I might need them on multiple occasions so I'll just get everything to make it simplier
    #update, start, end, total, left, elapsed = time_data()

def find_gap(main_player, data):
    main_rank = main_player["ranks"][-1]
    top, bottom = None, None
    for player in data:
        if player["ranks"][-1] == (main_rank - 1):
            top = player
        if player["ranks"][-1] == (main_rank + 1): 
            bottom = player
    return top, bottom 

def find_player(data, identifier):
    for player in data:
        if player['name'] == str(identifier) or player['id'] == (int(identifier) if identifier.isdigit() == True else 0):
            return player
    return None


@bot.event
async def on_ready():
    bot.start_time = time.time()
    bot.servers = [guild.name for guild in bot.guilds]
    update_metrics()
    log_message(f'Bot connected as {bot.user.name}')
    try:
        await bot.load_extension("cogs.help")
        log_message("Loaded cogs successfully.")
    except Exception as e:
        log_message(f"Failed to load cogs: {e}")


@bot.event
async def on_app_command_completion(interaction, command):
    bot.commands_executed += 1 #Yeah I tracked the number of commands ran bcs smh the bot kept crashing but apparently it was due tue the host so that part is prob useless nowadays
    log_message(f'Command executed: {command.name} succesfuli') #Dw the typo is intentionnal COZ FUNIIII
    update_metrics()

#Autocompletion max
async def autocompletion_type_max(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=a, value=a)
        for a in ["wins", "points"]
        ]
    return choices

@bot.tree.command(name="max", description="Show the maximum points or wins of a player.")
@app_commands.describe(type="The type of maximum you want to see. Either 'points' or 'wins'.", identifier="The identifier of the player you want to see the maximum of.")
@app_commands.autocomplete(type=autocompletion_type_max)
async def max_(ctx, type: str = "points", identifier: str = None):
    try:
        await ctx.response.defer()
        # check type
        if type not in ["wins", "points"]:
            await ctx.followup.send("Please provide a valid type. Either 'points' or 'wins'.")
            return
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()
        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                return
        player = find_player(players, identifier)
        if player is None:
            await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        maximum = player.get(f"max_{type}")
        if maximum:
            render([player], output_dir, f"max_{type}")
            current_max = maximum[-1] 
            image_path = os.path.join(output_dir, player["name"].replace('$', '\\$'), f'max_{type}.png')

            embed = discord.Embed(
                title=f"{player['name']}'s maximum {type} achieveable",
                description=f"Your current max is **{round(current_max, 0):,} {type}**.",
                color=discord.Color.green()
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename=f"max_{type}.png")
                embed.set_image(url=f"attachment://max_{type}.png")
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(file=file, embed=embed)
            else:
                
                await ctx.followup.send(embed=embed)
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
        else:
            await ctx.followup.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")
    except Exception as e:
        log_message(e)

@bot.tree.command(name="target", description="Show the pace needed to reach a goal.")
@app_commands.describe(goal="The goal you want to reach.", identifier="The identifier of the player you want to see the pace of.")
async def target(ctx, goal: str, identifier: str = None):
    try:
        await ctx.response.defer()
        # Test goal (500M --> 500000000)
        num = {
            "m": 1000000,
            "b": 1000000000,
            "k": 1000
        }
        goal = int(goal[:-1]) * num[goal[-1]]
        try:
            goal = int(goal)
        except ValueError: # l'argument fourni n'est pas un nombre
            await ctx.followup.send("Please provide a valid number as a goal.", ephemeral=True)
            return
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()
        if identifier is None:
            # cette ligne va raise un AttributeError si l'author n'est pas register, on modifie donc
            try:
                user_id = str(ctx.user.id)
            except AttributeError as e:
                # raise e # debug
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link).")
                return
            # tout va bien si on arrive là, on continue
            identifier = discord_users.get(user_id)
            if identifier is None: # si c'est None pour une raison ou pour une autre, même tarif c'est qu'il n'est pas register
                await ctx.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link).")
                return
        if goal == -1 : # devrait être useless
            await ctx.send("Please provide a goal")
            return
        player = find_player(players, identifier)
        if player is None:
            await ctx.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        wins_points_ratio = player["points_wins"][-1]
        update, start, end, total, left, elapsed = time_data()
        req_pace = (goal - player["points"][-1]) / (left.days * 24 + left.seconds / 3600)
        req_wins_pace = req_pace / wins_points_ratio
        # Check si le nombre de points est plus petit que goal
        if player["points"][-1] >= goal: # plus grand, problème
            addtt = "**:warning: You already have more points than your goal, thus the pace needed is 0.**\n\n"
        else: # rien à signaler, circulez monsieur bonne journée 👮
            addtt = ""
        # await ctx.send(f"Based on your current points, your goal, the time left and your average points/wins ratio.\n You would need to have a pace of {req_wins_pace} wins/hour to be able to reach {goal} points")
        embed = discord.Embed(
            title=f"{player['name']}'s target pace",
            color=discord.Color.green(),
            description=f"{addtt}• You would need to have a pace of **{round(req_wins_pace, 2)}** wins/hour to be able to reach **{goal:,}** points.\n\n_Note : this is based on your current points, your goal, the time left and your average points/wins ratio._",
        )
        await ctx.followup.send(embed=embed)
    except Exception as e:
        log_message(e)

@bot.tree.command(name='highest', description="Show the highest pace of a person was.")#A command to show what the highest pace of a person was (it was in the TODO so I guess someone asked for it)
@app_commands.describe(identifier="The identifier of the player you want to see the highest pace of.")
async def highest(ctx, identifier: str = None):
    try:
        await ctx.response.defer()
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()

        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                return
        player = find_player(players, identifier)
        if player is None:
            await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        paces = player.get("wins_pace")
        highest_pace = 0
        for i in paces:
            if i>highest_pace:
                highest_pace = i
        # await ctx.send(highest_pace)
        embed = discord.Embed(
                title=f"{player['name']}'s highest pace",
                description=f"The highest pace you've had was **{highest_pace}**.",
                color=discord.Color.green()
            )
        
        await ctx.followup.send(embed=embed)
    except Exception as e:
        log_message(e)

# Autocompletion leaderboard
async def autocompletion_type_lb(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=a, value=a)
        for a in ["wins_pace", "points_pace", "wins", "points"]
        ]
    return choices

@bot.tree.command(name="leaderboard", description="Show the top players leaderboard.")
@app_commands.autocomplete(type=autocompletion_type_lb)
@app_commands.describe(type="The type of leaderboard you want to see. Either 'wins', 'points', 'wins_pace' or 'points_pace'.", page="The page of the leaderboard you want to see.")
async def leaderboard(ctx, type: str = "wins_pace", page: int = 1):
    try:
        await ctx.response.defer()
        # vérifier si le type est valide
        if type not in ["wins_pace", "points_pace", "wins", "points"]:
            await ctx.followup.send("Please provide a valid type. Either 'wins_pace', 'points_pace', 'wins' or 'points'.")
            return
        players = load_data()
        update, start, end, total, left, elapsed = time_data()
        #make a quick loop to only keep the players where their hours[-1] == round(elapsed.days * 24 + elapsed.seconds / 3600 -0.01, 2)
        lb = []
        for player in players:
            if player["hours"][-1] == round(elapsed.days * 24 + elapsed.seconds / 3600 -0.01, 2):
                lb.append((player["name"], player[type][-1]))
        final_lb = sorted(lb, key=lambda x: x[1], reverse=True)

        players_per_page = 10
        total_pages = (len(final_lb) + players_per_page - 1) // players_per_page  # Ceiling division

        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        start_index = (page - 1) * players_per_page
        end_index = start_index + players_per_page

        embed = discord.Embed(
            title="🏆 Top Players Leaderboard 🏆",
            description=f"Here are the players ranked {start_index + 1} to {min(end_index, len(final_lb))} with the highest {type}.",
            color=discord.Color.gold()
        )

        for idx, (name, comp) in enumerate(final_lb[start_index:end_index], start=start_index + 1):
            if idx == 1:
                rank_emoji = "🥇"
            elif idx == 2:
                rank_emoji = "🥈"
            elif idx == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"**#{idx}**"
            # majuscule
            type = type.capitalize()
            embed.add_field(
                name=f"{rank_emoji} {name}",
                value=f"{type}: **{comp:,}**",
                inline=False
            )

        embed.set_footer(text=f"Page {page} of {total_pages}")
        await ctx.followup.send(embed=embed)
    except Exception as e:
        log_message(e)

@bot.tree.command(name = "gap", description="Show the gap between the player and the player above and below (if any).")
@app_commands.describe(identifier="The identifier of the player you want to see the gap of.")
async def gap(ctx, identifier: str = None):
    try:
        await ctx.response.defer()
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()

        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                return
        player = find_player(players, identifier)
        if player is None:
            await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        pro, noob = find_gap(player, players)
        embed = discord.Embed(
            title=f"{player['name']} - Points Gap",
            description=f"Points gap comparison for {player['name']}",
            color=0x00b0f4
        )
        pro_gap = abs(pro['points'][-1] - player['points'][-1]) if pro else 1e99 #SUPER UGLY FUCKING HELL PLEASE KILL ME 
        if pro:
            delta_pro = pro_gap - abs(pro['points'][-2] - player['points'][-2]) if len(player['points'])>=2 and len(pro['points'])>=2 else 0
        noob_gap = abs(noob['points'][-1] - player['points'][-1]) if noob else 1e99
        if noob:
            delta_noob = noob_gap - abs(noob['points'][-2] - player['points'][-2]) if len(player['points'])>=2 and len(noob['points'])>=2 else 0
        player_arrow = "↗" if pro_gap < noob_gap else "↘"
        if pro:
            pro_arrow = "⬆️"
            """embed.add_field(
                name=f"{pro_arrow} Nr.{pro['ranks'][-1]}: {pro['name']}",
                value=f"Points: **{pro['points'][-1]:,}**\n"
                    f"Gap: **{abs(pro['points'][-1] - player['points'][-1]):,} ({'+' if delta_pro > 0 else ''}{delta_pro:,})**",
                inline=False
            )"""
            estimated_time_pro = round((pro_gap / ( delta_pro * 4))*60) if delta_pro != 0 else 0
            enplus = ""
            if pro['points_pace'][-1] > player['points_pace'][-1] : # l'user est plus lent que le prochain
                enplus = f"*:warning: {pro['name']} is farming faster than you ! Skill issue, take this L *"
            else: # on est plus rapide !
                enplus = f"          |--> `around {estimated_time_pro} minutes needed` --> ( <t:{int(update.timestamp() + estimated_time_pro*60)}:R> TO BE FIXED XD)"
            embed.add_field(name=f" ⬆️ - {pro['ranks'][-1]} - {pro['name']}",
                            value=f"• Points : **{pro['points'][-1]:,}**\n•   Gap   :  **{abs(pro['points'][-1] - player['points'][-1]):,}** **({'+' if delta_pro > 0 else ''}{delta_pro:,})**\n{enplus}",
                            inline=False)
        embed.add_field(
            name=f" ▶️ - {player['ranks'][-1]} - {player['name']}",
            value=f"Points: **{player['points'][-1]:,}**",
            inline=False
        )
        if noob:
            noob_arrow = "⬇️"
            embed.add_field(
                name=f" ⬇️ - {noob['ranks'][-1]} - {noob['name']}",
                value=f"Points: **{noob['points'][-1]:,}**\n"
                    f"Gap: **{abs(player['points'][-1] - noob['points'][-1]):,} ({'+' if delta_noob > 0 else ''}{delta_noob:,})**\n",
                inline=False
            )

        embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
        
        await ctx.followup.send(embed=embed)
    except Exception as e:
        log_message(e)

@bot.tree.command(name='seed', description="Show the seed performance of a player.")
@app_commands.describe(identifier="The identifier of the player you want to see the seed performance of.")
async def seed(ctx, identifier: str = None):
    try:
        await ctx.response.defer()
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()

        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                return
        player = find_player(players, identifier)
        if player is None:
            await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        seed_data = player.get("points_wins")
        if seed_data:
            render([player], output_dir, "points_wins")
            current_seed = seed_data[-1]
            image_path = os.path.join(output_dir, player["name"].replace('$', '\\$'), 'points_wins.png')

            embed = discord.Embed(
                title=f"{player['name']}'s seed performance",
                description=f"Your seed's current points/win ratio is **{int(current_seed):,}**.",
                color=discord.Color.purple()
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="points_wins.png")
                embed.set_image(url=f"attachment://points_wins.png")
                
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                await ctx.followup.send(file=file, embed=embed)
            else:
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")
    except Exception as e:
        log_message(e)

# Autocompletion compare
async def autocompletion_type_cmp(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=a, value=b)
        for (a,b) in [("points pace", "points_pace"), ("wins pace", "wins_pace"), ("ranking", "ranks"), ("wins", "wins"), ("points", "points"), ("seed", "points_wins"), ("max wins", "max_wins"), ("max points", "max_points")]
        ]
    return choices

@bot.tree.command(name="bulk", description="Get the bulk infos of a player")
async def bulk(ctx, identifier:str = None):
    try: 
        await ctx.response.defer()
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()
        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (!link)")
                return
        player = find_player(players, identifier)
        if player is None:
            await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        bulk_render([player], output_dir, ["points", "points_pace", "ranks", "wins"])
        image_path = os.path.join(output_dir, player["name"].replace('$', '\\$'), 'bulk_points_points_pace_ranks_wins.png')
        embed = discord.Embed(
            title = "Summary ig",
            description = "ab lablalbla",
            color = discord.Color.purple()
            )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="bulk.png")
            embed.set_image(url=f"attachment://bulk.png")
            embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
            await ctx.followup.send(file=file, embed=embed)
        else:
            await ctx.followup.send(embed=embed)
    except Exception as e:
        log_message(e)

@bot.tree.command(name="compare", description="Compare multiple users.")
@app_commands.describe(type="The type of comparison you want to see. Either 'wins', 'points' or 'ranks'.", users="The users you want to compare (ex. /compare type:points users:Discord BabaYaga Lotad).")
@app_commands.autocomplete(type=autocompletion_type_cmp)
async def compare(ctx, type: str = None, users: str = None):
    try:
        await ctx.response.defer()
        # check type
        if type not in ["points_pace", "wins_pace", "ranks", "wins", "points", "points_wins", "max_wins", "max_points"]:
            await ctx.followup.send("Please provide a valid type. Either 'wins', 'points', 'max_points', 'max_wins', 'wins_pace', 'points_pace' or 'ranks'.")
            return
        # print(users) # debug
        old_users = users
        users = users.split(" ")
        if len(users) < 2:
            await ctx.followup.send("Please provide more than 2 users")
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()

        player_list = []
        player_not_found = []
        for user in users:
            player = find_player(players, user)
            if player is None:
                player_not_found.append(user)
                # await ctx.followup.send(f'Player with name or ID "{user}" not found. (not in the top10 000 ???)') # hold up
                continue
                # return
            player_list.append(player)
        # test pseudos non trouvés
        for player_ in player_not_found:
            for player_2 in player_not_found:
                #print(player_ + " " + player_2)
                if player_ + " " + player_2 in old_users: # existe mais avec un espace
                    player_not_found.remove(player_)
                    player_not_found.remove(player_2)
                    # Ajouter à player_list
                    player__ = find_player(players, player_ + " " + player_2)
                    if player__ is None: # il n'existe pas
                        player_not_found.append(player_ + " " + player_2)
                        # await ctx.followup.send(f'Player with name or ID "{user}" not found. (not in the top10 000 ???)') # hold up
                        continue
                        # return
                    player_list.append(player__)
        # test si des pseudos encore pas trouvé
        if len(player_not_found) > 0:
            await ctx.followup.send(f"Players with name or ID {', '.join(player_not_found)} not found. (not in the top10 000 ???)")
            return
        #print(player_list)
        render(player_list, output_dir, type, multiple=True)
        image_path = os.path.join(output_dir,f"multiple{type}.png")
        embed = discord.Embed(
                title="Comparison",
                description = f"Here's the {type} comparison between {', '.join(users[:-1])}, and {users[-1]}.\n",
                color=discord.Color.blurple()
            )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="comp.png")
            embed.set_image(url=f"attachment://comp.png")
            embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
            
            await ctx.followup.send(file=file, embed=embed)
        else:
            embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
            
            await ctx.followup.send(embed=embed)
    except Exception as e:
        log_message(e)

@bot.tree.command(name='ranking', description="Show the ranking of a player.")
@app_commands.describe(identifier="The identifier of the player you want to see the ranking of.")
async def ranking(ctx, identifier: str = None):
    try:
        await ctx.response.defer()
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()

        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                return
        player = find_player(players, identifier)
        if player is None:
            await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        ranks_data = player.get("ranks")
        if ranks_data:
            render([player], output_dir, "ranks", step=True)
            current_rank = ranks_data[-1]
            image_path = os.path.join(output_dir, player["name"].replace('$', '\\$'), 'ranks.png')

            embed = discord.Embed(
                title=f"{player['name']}'s ranking",
                description=f"Your current ranking is **{current_rank:,}**.",
                color=discord.Color.green()
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="ranks.png")
                embed.set_image(url=f"attachment://ranks.png")
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(file=file, embed=embed)
            else:
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")
    except Exception as e:
        log_message(e)
@bot.tree.command(name='points', description="Show the points of a player.")
@app_commands.describe(identifier="The identifier of the player you want to see the points of.")
async def points(ctx, identifier: str = None):
    try:
        await ctx.response.defer()
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()

        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                return
        player = find_player(players, identifier)
        if player is None:
            await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        points_data = player.get("points")
        if points_data:
            render([player], output_dir, "points")
            current_points = points_data[-1]
            image_path = os.path.join(output_dir, player["name"], 'points.png')

            embed = discord.Embed(
                title=f"{player['name']}'s current points",
                description=f"The current points are **{current_points:,}**.",
                color=discord.Color.red()
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="points.png")
                embed.set_image(url=f"attachment://points.png")
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(file=file, embed=embed)
            else:
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")
    except Exception as e:
        log_message(e)

@bot.tree.command(name='wins', description="Show the wins of a player.")
@app_commands.describe(identifier="The identifier of the player you want to see the wins of.")
async def wins(ctx, identifier: str = None):
    try:
        await ctx.response.defer()
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()

        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                return
        player = find_player(players, identifier)
        if player is None:
            await ctx.response.send_message(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        wins_data = player.get("wins")
        if wins_data:
            render([player], output_dir, "wins")
            current_wins = wins_data[-1]
            image_path = os.path.join(output_dir, player["name"], 'wins.png')

            embed = discord.Embed(
                title=f"{player['name']}'s current wins",
                description=f"The current wins are **{current_wins}**.",
                color=discord.Color.brand_red()
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename="wins.png")
                embed.set_image(url=f"attachment://wins.png")
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(file=file, embed=embed)
            else:
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(f"No data available for wins. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")
    except Exception as e:
        log_message(e)

#Autocompletion when
async def autocompletion_type_goal(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=a, value=a)
        for a in ["wins", "points"]
        ]
    return choices

@bot.tree.command(name="when", description="Show the estimated time of when a player will reach a goal.")
@app_commands.describe(goal="The goal you want to reach.", identifier="The identifier of the player you want to see the estimated time of.")
@app_commands.autocomplete(goal_type=autocompletion_type_goal)
async def when(ctx, goal: str, goal_type: str = "points", pace: int = 0, identifier: str = None):
    try:
        await ctx.response.defer()
        if pace == 0:
            await ctx.followup.send("Please provide a pace.")
            return
        num = {
            "m": 1000000,
            "b": 1000000000,
            "k": 1000
        }
        goal = int(goal[:-1]) * num[goal[-1]]
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()

        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                return

        player = find_player(players, identifier)

        if player is None:
            await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return
        if goal_type == "points":
            player_points = player["points"][-1]
            goal_points = int(goal)
            if goal_points < player_points:
                await ctx.followup.send("Please provide a goal higher than your current points.")
                return
            req_points = goal_points - player_points
            req_hours = req_points / pace
            final_timestamp = (update + timedelta(hours=req_hours)).timestamp()
            req = req_points
        elif goal_type == "wins":
            player_wins = player["wins"][-1]
            goal_wins = int(goal)
            if goal_wins < player_wins:
                await ctx.followup.send("Please provide a goal higher than your current wins.")
                return
            req_wins = goal_wins - player_wins
            req_hours = req_wins / pace
            final_timestamp = (update + timedelta(hours=req_hours)).timestamp()
            req = req_wins
        if final_timestamp > end.timestamp():
            await ctx.followup.send("You can't reach this goal in the future.... L")
            return
        embed = discord.Embed(
            title=f"{player['name']}'s estimated time to reach {goal:,} points",
            description=f"You need to reach **{req:,}** points in **{round(req_hours, 2):,}** hours to reach your goal.",
            color=discord.Color.green()
        )
        embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
        
        await ctx.followup.send(embed=embed)
    except Exception as e:
        log_message(e)

# Autocompletion pace
async def autocompletion_type_pace(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=a, value=a)
        for a in ["wins", "points"]
        ]
    return choices

@bot.tree.command(name='pace', description="Show your current pace.")
@app_commands.describe(pace_type="The pace type you want to see. Either 'wins' or 'points'.", identifier="The identifier of the player you want to see the pace of.")
@app_commands.autocomplete(pace_type=autocompletion_type_pace)
async def pace(ctx, pace_type: str = "wins", identifier: str = None):
    try:
        await ctx.response.defer()
        # vérifier si le type est valide
        if pace_type not in ["wins", "points"]:
            await ctx.followup.send("Please provide a valid type. Either 'wins' or 'points'.")
            return
        players = load_data()
        discord_users = load_discord_users()
        update, start, end, total, left, elapsed = time_data()

        if identifier is None:
            user_id = str(ctx.user.id)
            identifier = discord_users.get(user_id)
            if identifier is None:
                await ctx.followup.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (/link)")
                return

        player = find_player(players, identifier)

        if player is None:
            await ctx.followup.send(f'Player with name or ID "{identifier}" not found. (not in the top10 000 ???)')
            return

        pace_type = pace_type + "_pace"
        if pace_type not in ['wins_pace', 'points_pace']:
            await ctx.followup.send(f'Invalid pace type "{pace_type}". Use "wins" or "points" ex:`!pace wins Lotad`.')
            return

        pace_data = player.get(pace_type)
        if pace_data:
            render([player], output_dir, pace_type)
            latest_pace = pace_data[-1]
            image_path = os.path.join(output_dir, player["name"], f'{pace_type}.png')

            embed = discord.Embed(
                title=f"{player['name']}'s current {pace_type.replace('_', ' ')}",
                description=f"Your current {pace_type.replace('_', ' ')} is **{latest_pace}**.",
                color=discord.Color.blue()
            )
            if os.path.exists(image_path):
                file = discord.File(image_path, filename=f"{pace_type}.png")
                embed.set_image(url=f"attachment://{pace_type}.png")
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(file=file, embed=embed)
            else:
                embed.add_field(name="Updated at",value=f"<t:{int(update.timestamp())}:f>    (<t:{int(update.timestamp())}:R>)", inline=False)
                
                await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(f"No data available for {pace_type}. (either fetch failed and it's a huge skill issue or you're not in the top10 000 and that's a skill issue as well)")
    except Exception as e:
        log_message(e)
@bot.tree.command(name='link', description="Link your Discord account to your Dokkan ig name/ID.")
@app_commands.describe(identifier="The identifier you want to link your Discord account to.")
async def link(ctx, identifier: str):
    try:
        await ctx.response.defer()
        exist = False
        discord_users = load_discord_users()
        user_id = str(ctx.user.id)

        async def callback_yesconf(interaction: discord.Interaction):
            if int(ctx.user.id) != int(interaction.user.id):
                return await interaction.followup.send(embed=discord.Embed(
                    description=f"❌ {interaction.user.mention}, - you can't do that !"),
                    ephemeral=True)
            # Remplacer l'identifiant
            discord_users[user_id] = identifier
            save_discord_users(discord_users)
            # Dire que l'identifiant a été remplacé
            await ctx.channel.send(embed=discord.Embed
            (
                description=f'**✅♻ - Your Discord ID has refreshed and is now linked to player "{identifier}**".',
                color=discord.Color.blue()
            ))
            await interaction.message.delete()

        async def callback_noconf(interaction: discord.Interaction):
            if int(ctx.user.id) != int(interaction.user.id):
                return await interaction.followup.send(embed=discord.Embed(
                    description=f"❌ {interaction.user.mention}, - you can't do that !"),
                    ephemeral=True)
            await interaction.message.delete()

        view = discord.ui.View()
        button_validate = discord.ui.Button(style=discord.ButtonStyle.green, emoji="✅", label="Oui")
        button_cancel = discord.ui.Button(style=discord.ButtonStyle.red, emoji="❌", label="Non")
        button_validate.callback = callback_yesconf
        button_cancel.callback = callback_noconf
        view.add_item(button_validate)
        view.add_item(button_cancel)

        # await ctx.send(f'Your Discord ID has been successfully linked to player "{identifier}".'))

        # Check si l'utilisateur existe
        try:
            if type(discord_users[user_id]) is int:
                pass
            exist = True
        except KeyError: # Existe pas, car erreur
            exist = False

        if exist:
            # Demander si il veut remplacer son identifiant
            await ctx.followup.send(f"Would you like to replace ``{discord_users[str(ctx.user.id)]}`` by ``{identifier}`` ?", view=view, ephemeral=False)
        else:
            # Existe pas
            discord_users[user_id] = identifier
            save_discord_users(discord_users)
            await ctx.send(embed=discord.Embed
            (
                description=f'**✅ - Your Discord ID has been successfully linked to player "{identifier}**".',
                color=discord.Color.blue()
            ))
    except Exception as e:
        log_message(e)



update_commands_list()
window.mainloop()
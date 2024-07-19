import discord
from discord.ext import commands
import json
from render import render
import os 

TOKEN = 'BOT TOKEN' 
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents = intents)
output_dir = 'top100_data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)

def load_discord_users():
    if not os.path.exists('discord_users.json'):
        with open('discord_users.json', 'w') as f:
            json.dump({}, f)  # Create an empty dictionary if file doesn't exist
    with open('discord_users.json', 'r') as f:
        return json.load(f)

def save_discord_users(discord_users):
    with open('discord_users.json', 'w') as f:
        json.dump(discord_users, f, indent=4)


def find_player(data, identifier):
    for player in data:
        print(player['name'] + "|" + player['name'] == identifier)
        if player['name'] == str(identifier) or player['id'] == (int(identifier) if identifier.isdigit() == True else 0):
            return player
    return None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='points')
async def points(ctx, identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    if identifier is None:
        user_id = str(ctx.author.id)
        identifier = discord_users.get(user_id)
        if identifier is None:
            await ctx.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (!link)")
            return
    player = find_player(players, identifier)
    if player is None:
        await ctx.send(f'Player with name or ID "{identifier}" not found. (not in the top100 ???)')
        return
    points_data = player.get("points")
    if points_data:
        render([player], output_dir)
        current_points = points_data[-1]  # Get the latest pace value
        image_path = os.path.join(output_dir, player["name"], 'points.png')

        embed = discord.Embed(
            title=f"{player['name']}'s current points",
            description=f"The current points are {current_points}.",
            color=discord.Color.red()
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="points.png")
            embed.set_image(url=f"attachment://points.png")
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top100 and that's a skill issue as well)")

@bot.command(name='wins')
async def wins(ctx, identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    if identifier is None:
        user_id = str(ctx.author.id)
        identifier = discord_users.get(user_id)
        if identifier is None:
            await ctx.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (!link)")
            return
    player = find_player(players, identifier)
    if player is None:
        await ctx.send(f'Player with name or ID "{identifier}" not found. (not in the top100 ???)')
        return
    wins_data = player.get("wins")
    if wins_data:
        render([player], output_dir)
        current_wins = wins_data[-1]  # Get the latest pace value
        image_path = os.path.join(output_dir, player["name"], 'wins.png')

        embed = discord.Embed(
            title=f"{player['name']}'s current wins",
            description=f"The current wins are {current_wins}.",
            color=discord.Color.red()
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="wins.png")
            embed.set_image(url=f"attachment://wins.png")
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"No data available for wins. (either fetch failed and it's a huge skill issue or you're not in the top100 and that's a skill issue as well)")


@bot.command(name='pace')
async def pace(ctx, identifier: str = None, pace_type: str = "wins_pace"):
    players = load_data()
    discord_users = load_discord_users()

    if identifier is None:
        user_id = str(ctx.author.id)
        identifier = discord_users.get(user_id)
        if identifier is None:
            await ctx.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (!link)")
            return
    
    player = find_player(players, identifier)
    
    if player is None:
        await ctx.send(f'Player with name or ID "{identifier}" not found. (not in the top100 ???)')
        return

    if pace_type not in ['wins_pace', 'points_pace']:
        await ctx.send(f'Invalid pace type "{pace_type}". Use "wins_pace" or "points_pace".')
        return

    pace_data = player.get(pace_type)
    if pace_data:
        render([player], output_dir)
        latest_pace = pace_data[-1]  # Get the latest pace value
        image_path = os.path.join(output_dir, player["name"], f'{pace_type}.png')

        embed = discord.Embed(
            title=f"{player['name']}'s current {pace_type.replace('_', ' ')}",
            description=f"Your current {pace_type.replace('_', ' ')} is {latest_pace}.",
            color=discord.Color.blue()
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename=f"{pace_type}.png")
            embed.set_image(url=f"attachment://{pace_type}.png")
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"No data available for {pace_type}. (either fetch failed and it's a huge skill issue or you're not in the top100 and that's a skill issue as well)")

@bot.command(name='link')
async def link(ctx, identifier: str):
    discord_users = load_discord_users()
    user_id = str(ctx.author.id)
    discord_users[user_id] = identifier
    save_discord_users(discord_users)
    
    await ctx.send(f'Your Discord ID has been successfully linked to player "{identifier}".')

bot.run(TOKEN)

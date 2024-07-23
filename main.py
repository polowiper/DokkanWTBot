import discord
from discord.ext import commands
import json
from render import render
import os 
from datetime import datetime, timezone, timedelta


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
    return f"{output_dir}/fetch{i-1}.json"

def time_data():
    latest_fetch_path = latest_fetch()

    if latest_fetch_path:
        with open(latest_fetch_path, 'r') as file:
            data = json.load(file)
            print("Data loaded from the latest fetch file:")
            update = datetime.utcfromtimestamp(data["userlist"]["updated_at"]).replace(tzinfo=timezone.utc)
            start = datetime.fromisoformat(data["start_at"]).astimezone(timezone.utc)
            end = datetime.fromisoformat(data["end_at"]).astimezone(timezone.utc)
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
    print(f'Logged in as {bot.user.name}')
@bot.command(name="max")
async def max(ctx, type: str = "points", identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    update, start, end, total, left, elapsed = time_data()
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
    maximum = player.get(f"max_{type}")
    if maximum:
        render([player], output_dir, f"max_{type}")
        current_max = maximum[-1] 
        image_path = os.path.join(output_dir, player["name"].replace('$$', '\$\$'), f'max_{type}.png')

        embed = discord.Embed(
            title=f"{player['name']}'s maximum {type} achieveable",
            description=f"Your current max is **{round(current_max, 0):,} {type}**.",
            color=discord.Color.green()
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename=f"max_{type}.png")
            embed.set_image(url=f"attachment://max_{type}.png")
            embed.add_field(name="Updated at",value=update, inline=False)
            await ctx.send(file=file, embed=embed)
        else:
            await ctx.send(embed=embed)
            embed.add_field(name="Updated at",value=update, inline=False)
    else:
        await ctx.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top100 and that's a skill issue as well)")

@bot.command(name="target")
async def target(ctx, goal: int, identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    update, start, end, total, left, elapsed = time_data()
    if identifier is None:
        user_id = str(ctx.author.id)
        identifier = discord_users.get(user_id)
        if identifier is None:
            await ctx.send("You did not provide a Dokkan name/ID and your Discord account isn't linked to any please provide an identifier or link your Discord account (!link)")
            return
    if goal is None:
        await ctx.send("Please provide a goal")
        return
    player = find_player(players, identifier)
    if player is None:
        await ctx.send(f'Player with name or ID "{identifier}" not found. (not in the top100 ???)')
        return
    wins_points_ratio = player["points_wins"][-1]
    update, start, end, total, left, elapsed = time_data()
    req_pace = (goal - player["points"][-1]) / (left.days * 24 + left.seconds / 3600)
    req_wins_pace = req_pace / wins_points_ratio
    await ctx.send(f"Based on your current points, your goal, the time left and your average points/wins ratio.\n You would need to have a pace of {req_wins_pace} wins/hour to be able to reach {goal}")   

@bot.command(name = "gap")
async def gap(ctx, identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    update, start, end, total, left, elapsed = time_data()
    
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
    pro, noob = find_gap(player, players)
    embed = discord.Embed(
        title=f"{player['name']} - Points Gap",
        description=f"Points gap comparison for {player['name']}",
        color=discord.Color.yellow()
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
        embed.add_field(
            name=f"{pro_arrow} Nr.{pro['ranks'][-1]}: {pro['name']}",
            value=f"Points: **{pro['points'][-1]:,}**\n"
                f"Gap: **{abs(pro['points'][-1] - player['points'][-1]):,} ({'+' if delta_pro > 0 else ''}{delta_pro:,})**",
            inline=False
        )
    embed.add_field(
        name=f"{player_arrow} Nr.{player['ranks'][-1]}:{player['name']}",
        value=f"Points: **{player['points'][-1]:,}**",
        inline=False
    )
    if noob:
        noob_arrow = "⬇️"
        embed.add_field(
            name=f"{noob_arrow} Nr.{noob['ranks'][-1]}: {noob['name']}",
            value=f"Points: **{noob['points'][-1]:,}**\n"
                f"Gap: **{abs(player['points'][-1] - noob['points'][-1]):,} ({'+' if delta_noob > 0 else ''}{delta_noob:,})**\n",
            inline=False
        )
    
    embed.add_field(name="Updated at",value=update, inline=False)
    await ctx.send(embed=embed)
                       
@bot.command(name='seed')
async def seed(ctx, identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    update, start, end, total, left, elapsed = time_data()
    
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
    seed_data = player.get("points_wins")
    if seed_data:
        render([player], output_dir, "points_wins")
        current_seed = seed_data[-1]
        image_path = os.path.join(output_dir, player["name"].replace('$$', '\$\$'), 'points_wins.png')

        embed = discord.Embed(
            title=f"{player['name']}'s seed performance",
            description=f"Your seed's current points/win ratio is {current_seed}.",
            color=discord.Color.purple()
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="points_wins.png")
            embed.set_image(url=f"attachment://points_wins.png")
            await ctx.send(file=file, embed=embed)
            embed.add_field(name="Updated at",value=update, inline=False)
        else:
            embed.add_field(name="Updated at",value=update, inline=False)
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top100 and that's a skill issue as well)")

@bot.command(name="compare")
async def compare(ctx, type: str = None, *users):
    if len(users) < 2:
        await ctx.send("Please provide more than 2 users")
    players = load_data()
    discord_users = load_discord_users()
    update, start, end, total, left, elapsed = time_data()
    
    player_list = []
    for user in users:
        player = find_player(players, user)
        if player is None:
            await ctx.send(f'Player with name or ID "{identifier}" not found. (not in the top100 ???)')
            return
        player_list.append(player)
    render(player_list, output_dir, type, multiple=True)
    image_path = os.path.join(output_dir,f"multiple{type}.png")
    embed = discord.Embed(
            title="a",
            description="I CAN'T TAKE IT ANYMORE I'M GOING INSANE IMA YUGHFUYEWGEYFGEAWIODWO",
            color=discord.Color.green()
        )
    if os.path.exists(image_path):
        file = discord.File(image_path, filename="comp.png")
        embed.set_image(url=f"attachment://comp.png")
        embed.add_field(name="Updated at",value=update, inline=False)
        await ctx.send(file=file, embed=embed)
    else:
        embed.add_field(name="Updated at",value=update, inline=False)
        await ctx.send(embed=embed)


@bot.command(name='ranking')
async def ranking(ctx, identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    update, start, end, total, left, elapsed = time_data()
    
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
    ranks_data = player.get("ranks")
    if ranks_data:
        render([player], output_dir, "ranks")
        current_rank = ranks_data[-1]
        image_path = os.path.join(output_dir, player["name"].replace('$$', '\$\$'), 'ranks.png')

        embed = discord.Embed(
            title=f"{player['name']}'s ranking",
            description=f"Your current ranking is {current_rank}.",
            color=discord.Color.green()
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="ranks.png")
            embed.set_image(url=f"attachment://ranks.png")
            embed.add_field(name="Updated at",value=update, inline=False)
            await ctx.send(file=file, embed=embed)
        else:
            embed.add_field(name="Updated at",value=update, inline=False)
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top100 and that's a skill issue as well)")


@bot.command(name='points')
async def points(ctx, identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    update, start, end, total, left, elapsed = time_data()
    
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
        render([player], output_dir, "points")
        current_points = points_data[-1]
        image_path = os.path.join(output_dir, player["name"], 'points.png')

        embed = discord.Embed(
            title=f"{player['name']}'s current points",
            description=f"The current points are {current_points}.",
            color=discord.Color.red()
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="points.png")
            embed.set_image(url=f"attachment://points.png")
            embed.add_field(name="Updated at",value=update, inline=False)
            await ctx.send(file=file, embed=embed)
        else:
            embed.add_field(name="Updated at",value=update, inline=False)
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"No data available for points. (either fetch failed and it's a huge skill issue or you're not in the top100 and that's a skill issue as well)")

@bot.command(name='wins')
async def wins(ctx, identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    update, start, end, total, left, elapsed = time_data()
    
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
        render([player], output_dir, "wins")
        current_wins = wins_data[-1]
        image_path = os.path.join(output_dir, player["name"], 'wins.png')

        embed = discord.Embed(
            title=f"{player['name']}'s current wins",
            description=f"The current wins are {current_wins}.",
            color=discord.Color.red()
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="wins.png")
            embed.set_image(url=f"attachment://wins.png")
            embed.add_field(name="Updated at",value=update, inline=False)
            await ctx.send(file=file, embed=embed)
        else:
            embed.add_field(name="Updated at",value=update, inline=False)
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"No data available for wins. (either fetch failed and it's a huge skill issue or you're not in the top100 and that's a skill issue as well)")


@bot.command(name='pace')
async def pace(ctx, pace_type: str = "wins", identifier: str = None):
    players = load_data()
    discord_users = load_discord_users()
    update, start, end, total, left, elapsed = time_data()
    
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

    pace_type = pace_type + "_pace"
    if pace_type not in ['wins_pace', 'points_pace']:
        await ctx.send(f'Invalid pace type "{pace_type}". Use "wins" or "points" ex:`!pace wins Lotad`.')
        return

    pace_data = player.get(pace_type)
    if pace_data:
        render([player], output_dir, pace_type)
        latest_pace = pace_data[-1]
        image_path = os.path.join(output_dir, player["name"], f'{pace_type}.png')

        embed = discord.Embed(
            title=f"{player['name']}'s current {pace_type.replace('_', ' ')}",
            description=f"Your current {pace_type.replace('_', ' ')} is {latest_pace}.",
            color=discord.Color.blue()
        )
        if os.path.exists(image_path):
            file = discord.File(image_path, filename=f"{pace_type}.png")
            embed.set_image(url=f"attachment://{pace_type}.png")
            embed.add_field(name="Updated at",value=update, inline=False)
            await ctx.send(file=file, embed=embed)
        else:
            embed.add_field(name="Updated at",value=update, inline=False)
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

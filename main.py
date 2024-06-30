import discord
from discord.ext import commands
import requests
import json
import pytz
from datetime import datetime
TOKEN = 'BOT TOKEN'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents = intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def fetchinfo(ctx, *args):
    print("a")
    ids = [int(arg) for arg in args]
    
    if not ids:
        await ctx.send('Please provide at least one ID.')
        return
    
    try:
        response = requests.get('https://dbz-dokkanbattle.com/api/budokai/52')
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        userlist = data.get("userlist", {})
        rankers = userlist.get("rankers", [])
        found_rankers = []
        for ranker in rankers:
            if ranker.get("id") in ids:
                found_rankers.append(ranker)

        if found_rankers:
            with open('rankers_info.json', 'w') as f:
                json.dump(found_rankers, f, indent=4)
            await ctx.send(f'Found and saved info for IDs: {", ".join(map(str, ids))}')
        else:
            await ctx.send(f'No rankers found with IDs: {", ".join(map(str, ids))}')

    except requests.exceptions.RequestException as e:
        await ctx.send(f'Error fetching data: {e}')
    except json.JSONDecodeError:
        await ctx.send('Error decoding the JSON response.')

@bot.command()
async def addIds(ctx, *args):
    try:
        ids = [int(arg) for arg in args]
        
        if not ids:
            await ctx.send('Please provide at least one ID.')
            return
        try:
            with open('ids.json', 'r') as f:
                existing_ids = json.load(f)
        except FileNotFoundError:
            existing_ids = []

        new_ids = [id for id in ids if id not in existing_ids]
        existing_ids.extend(new_ids)
        with open('ids.json', 'w') as f:
            json.dump(existing_ids, f, indent=4)

        await ctx.send(f'Added {len(new_ids)} new IDs to the list.')

    except ValueError:
        await ctx.send('Invalid ID format. Please provide integers.')

@bot.command()
async def getinfo(ctx):
    print("b")
    try:
        with open('rankers_info.json', 'r') as f:
            rankers_info = json.load(f)
        with open('data.json', 'r') as r:
            data = json.load(r)
        start_at = data["start_at"]
        end_at = data["end_at"]
        start_time = datetime.fromisoformat(start_at)
        end_time = datetime.fromisoformat(end_at)
        total_time = round((end_time - start_time).total_seconds() / 3600)
        updated_at_naive = datetime.fromtimestamp(data["userlist"]["updated_at"])
        #Because the .fromisoformat and .fromtimestamp are different one is timezone aware and the other isn't so I need to convert to do operations on it yes this is fucking dumb it's 3am plz help ty
        updated_at_aware = updated_at_naive.replace(tzinfo=pytz.UTC)
        elapsed_time = round((updated_at_aware - start_time).total_seconds() / 3600, 1)
        time_left = round((end_time - updated_at_aware).total_seconds() / 3600, 1)
        if rankers_info:
            embed = discord.Embed(title="Rankers Info", color=0x00ff00)
            for ranker in rankers_info:
                wins = ranker['title_num']
                pace_pts = round(ranker['point']/elapsed_time)
                pace_wins = round(wins/elapsed_time, 1)
                max_result = round(ranker['point'] + (pace_pts * time_left))
                embed.add_field(name=f"Hour {elapsed_time}\nUsername: {ranker['name']}", value=f"ID: {ranker['id']}\nRank: {ranker['ranking']}\nScore: {ranker['point']}\n Pace: {pace_pts} points/hour\n Elapsed Time: {elapsed_time}hours\nRemaining time: {time_left}hours\n Pace (wins): {pace_wins}/hour\n Theorical points: {max_result}", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send('No rankers info found.')

    except FileNotFoundError:
        await ctx.send('No rankers info found. Use !fetchinfo command first.')
    except json.JSONDecodeError:
        await ctx.send('Error decoding rankers info.')

bot.run(TOKEN)

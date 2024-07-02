import discord
from discord.ext import commands
import requests
import json
import pytz
from datetime import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()
TOKEN = 'BOT TOKEN'
TARGET_TIMEZONE = 'UTC' 
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents = intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

def update_scores(scores_data, id:int, score:int, hour:float, wins:int):
    for dict in scores_data:
        if dict["id"] == str(id):
            if not dict['scores'] or dict['scores'][-1] != score:
                dict['scores'].append(score)
                if dict['wins']:
                    dict['pace'].append(round((wins - dict['wins'][-1]) / (hour - dict['hours'][-1]), 1))
                else:
                    dict['pace'].append(round(wins / hour, 1))
                dict['hours'].append(hour)
                dict['wins'].append(wins)
            return scores_data
    else:
        new_dict = {
            "id": str(id),
            "scores": [score],
            "hours": [hour],
            "wins": [wins],
            "pace": [round(wins / hour, 1)]
        }
        scores_data.append(new_dict)
        return scores_data


@bot.command()
async def addIds(ctx, *args):
    try:
        ids = [{"id": str(arg), "scores": [], "hours": [], "wins": [], "pace": []} for arg in args]
        
        if not ids:
            await ctx.send('Please provide at least one ID.')
            return
        try:
            with open('ids.json', 'r') as f:
                existing_ids = json.load(f)
        except FileNotFoundError:
            existing_ids = []

        new_ids = [id for id in ids if id["id"] not in [existing_id["id"] for existing_id in existing_ids]]
        existing_ids.extend(new_ids)
        with open('ids.json', 'w') as f:
            json.dump(existing_ids, f, indent=4)

        await ctx.send(f'Added {len(new_ids)} new IDs to the list.')

    except ValueError:
        await ctx.send('Invalid ID format. Please provide integers.')

@bot.command()

async def getinfo(ctx, *args):

    ids = [int(arg) for arg in args]

    print("b")

    try:

        response = requests.get('https://dbz-dokkanbattle.com/api/budokai/52')

        response.raise_for_status()

        data = response.json()


        userlist = data.get("userlist", {})

        rankers = userlist.get("rankers", [])

        found_rankers = []

        IdsList = []

        if not ids:

            #blah blah blah look into the ids file\

            with open('ids.json', 'r') as f:

                id_data = json.load(f)

            IdsList = [int(id_dict["id"]) for id_dict in id_data]
            
        else:
            IdsList = ids
        print(f'\nHere are the {len(IdsList)} Ids : {IdsList}\n')
        for ranker in rankers:

            if ranker.get("id") in IdsList:

                found_rankers.append(ranker)

        start_at = data["start_at"]

        end_at = data["end_at"]

        start_time = datetime.fromisoformat(start_at).replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(TARGET_TIMEZONE))
        end_time = datetime.fromisoformat(end_at).replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(TARGET_TIMEZONE))

        total_time = round((end_time - start_time).total_seconds() / 3600)
        updated_at_naive = datetime.fromtimestamp(data["userlist"]["updated_at"])
        updated_at_aware = updated_at_naive.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(TARGET_TIMEZONE))


        elapsed_time = round((updated_at_aware - start_time).total_seconds() / 3600  - 2, 1)

        time_left = round((end_time - updated_at_aware).total_seconds() / 3600 + 2 , 1)
        if IdsList:
            embed = discord.Embed(title="Rankers Info", color=0x00ff00)

            for ranker in found_rankers:
                
                wins = ranker['title_num']

                pace_pts = round(ranker['point']/elapsed_time)

                pace_wins = round(wins/elapsed_time, 1)

                max_result = round(ranker['point'] + (pace_pts * time_left))
                print(f"ID: {ranker['id']}\nRank: {ranker['ranking']}\nScore: {ranker['point']}\n Pace: {pace_pts} points/hour\n Elapsed Time: {elapsed_time}hours\nRemaining time: {time_left}hours\n Pace (wins): {pace_wins}/hour\n Theorical points: {max_result}")
                with open('ids.json', 'r') as f:
                    id_data = json.load(f)

                id_data = update_scores(id_data, int(ranker['id']), ranker['point'], elapsed_time, int(wins))

                with open('ids.json', 'w') as f:
                    json.dump(id_data, f, indent=4)

                if len(IdsList) < 15:
                    embed.add_field(name=f"Hour {elapsed_time}\nUsername: {ranker['name']}", value=f"ID: {ranker['id']}\nRank: {ranker['ranking']}\nScore: {ranker['point']}\n Pace: {pace_pts} points/hour\n Elapsed Time: {elapsed_time}hours\nRemaining time: {time_left}hours\n Pace (wins): {pace_wins}/hour\n Theorical points: {max_result}", inline=False)
            await ctx.send(embed=embed)

        else:

            await ctx.send('No rankers info found.')


    except FileNotFoundError:

        await ctx.send('No rankers info found.')

    except json.JSONDecodeError:

        await ctx.send('Error decoding rankers info.')

async def update_scores_task():
    print("c")
    try:
        print("d")
    except FileNotFoundError:

        print('No IDs or scores found.')

    except json.JSONDecodeError:

        print('Error decoding IDs or scores.')
@bot.command()
async def synctop100(ctx):
    try:
        response = requests.get('https://dbz-dokkanbattle.com/api/budokai/52')

        response.raise_for_status()

        data = response.json()


        userlist = data.get("userlist", {})

        rankers = userlist.get("rankers", [])

        IdsList = [ranker['id'] for ranker in rankers]
        print(IdsList)
        await addIds(ctx, *IdsList)
        await ctx.send('The top 100 has been synced')
    except FileNotFoundError:

        print('No IDs or scores found.')

    except json.JSONDecodeError:

        print('Error decoding IDs or scores.')
scheduler.add_job(update_scores_task, 'interval', minutes=1)


scheduler.start()
bot.run(TOKEN)

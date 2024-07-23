import json
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
#with open('test.json', 'r') as file:
#    data = json.load(file)

output_dir = 'final_data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# My promo lol
author_tag = "Author's Twitter: @polo51852166"

def calculate_figsize(num_players, max_name_length):
    width = 10 + max(0, (max_name_length - 10) * 0.5)
    height = 6 + num_players * 0.2
    return (width, height)


def plot_and_save(players, key, xlabel, ylabel, title, output_dir, step=False, animate=False, multiple=False):
    if multiple:
        max_name_length = max(len(player['name']) for player in players)
        figsize = calculate_figsize(len(players), max_name_length)
        
        fig, ax = plt.subplots(figsize=figsize)
        lines = []

        for player in players:
            player_name = player['name'].replace('$$', '\$\$')
            line, = ax.step(player['hour'], player[key], where='mid', label=player_name) if step else ax.plot(player['hour'], player[key], label=player_name)
            lines.append(line)

        def update(num):
            for line, player in zip(lines, players):
                line.set_data(player['hour'][:num], player[key][:num])
            return lines

        if animate:
            ani = FuncAnimation(fig, update, frames=len(players[0]['hour']), blit=True)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
            plt.grid(True)
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.text(0, -0.1, author_tag, transform=plt.gca().transAxes, ha='left', va='top', fontsize=10)
            output_path = os.path.join(output_dir, f'multiple{key}.gif')
            ani.save(output_path, writer=PillowWriter(fps=10))
        else:
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
            plt.grid(True)
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.text(0, -0.1, author_tag, transform=plt.gca().transAxes, ha='left', va='top', fontsize=10)
            output_path = os.path.join(output_dir, f'multiple{key}.png')
            if step:
                plt.gca().invert_yaxis()
            
            plt.savefig(output_path, bbox_inches='tight')
        
        plt.close()

    else:
        for player in players:
            player_name = player['name'].replace('$$', '\$\$') #FUCK YOU RU$$IA
            player_dir = os.path.join(output_dir, player_name)
            
            if not os.path.exists(player_dir):
                os.makedirs(player_dir)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            if step:
                line, = ax.step(player['hour'], player[key], where='mid')
                plt.gca().invert_yaxis()
                y_ticks = np.linspace(min(player[key]), max(player[key]), 10, dtype=int)
                plt.gca().set_yticks(y_ticks)
                #plt.gca().yaxis.set_major_locator(MultipleLocator(5))
            else:
                print(f"there are {len(player['hour'])} different hours and {len(player[key])} {key}")
                line, = ax.plot(player['hour'], player[key])

            def update(num):
                line.set_data(player['hour'][:num], player[key][:num])
                return line,

            if animate:
                ani = FuncAnimation(fig, update, frames=len(player['hour']), blit=True)
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.title(f"{player_name}'s {title}")
                plt.grid(True)
                plt.text(0, -0.1, author_tag, transform=plt.gca().transAxes, ha='left', va='top', fontsize=10)
                output_path = os.path.join(player_dir, f'{key}.gif')
                ani.save(output_path, writer=PillowWriter(fps=10))
            else:
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.title(f"{player_name}'s {title}")
                plt.grid(True)
                plt.text(0, -0.1, author_tag, transform=plt.gca().transAxes, ha='left', va='top', fontsize=10)
                output_path = os.path.join(player_dir, f'{key}.png')
                plt.savefig(output_path, bbox_inches='tight')
            
            plt.close()

def render(players, output_dir, type="all", animate=False, multiple=False):
    match type:
        case "all":
            plot_and_save(players, 'wins', 'Hours', 'Wins', "Wins by Hour", output_dir, animate=animate, multiple=multiple)
            plot_and_save(players, 'points', 'Hours', 'Points', "Points by Hour", output_dir, animate=animate, multiple=multiple)
            plot_and_save(players, 'wins_pace', 'Hours', 'Wins Pace', "Wins Pace by Hour", output_dir, animate=animate, multiple=multiple)
            plot_and_save(players, 'points_pace', 'Hours', 'Points Pace', "Points Pace by Hour", output_dir, animate=animate, multiple=multiple)
            plot_and_save(players, 'ranks', 'Hours', 'Ranks', "Ranks by Hour", output_dir, step=True, animate=animate, multiple=multiple)
            plot_and_save(players, 'points_wins', 'Hours', 'Points/Wins', "Points per Win ratio by Hour", output_dir, animate=animate, multiple=multiple)
            plot_and_save(players, 'max_wins', 'Hours', 'Max wins achievable', "Theoretical max", output_dir, animate=animate, multiple=multiple)
            plot_and_save(players, 'max_points', 'Hours', 'Max points achievable', "Theoretical max", output_dir, animate=animate, multiple=multiple) 
        case "wins":
            plot_and_save(players, 'wins', 'Hours', 'Wins', "Wins by Hour", output_dir, animate=animate, multiple=multiple)
        case "points":
            plot_and_save(players, 'points', 'Hours', 'Points', "Points by Hour", output_dir, animate=animate, multiple=multiple)
        case "wins_pace":
            plot_and_save(players, 'wins_pace', 'Hours', 'Wins Pace', "Wins Pace by Hour", output_dir, animate=animate, multiple=multiple)
        case "points_pace":
            plot_and_save(players, 'points_pace', 'Hours', 'Points Pace', "Points Pace by Hour", output_dir, animate=animate, multiple=multiple)
        case "ranks":
            plot_and_save(players, 'ranks', 'Hours', 'Ranks', "Ranks by Hour", output_dir, step=True, animate=animate, multiple=multiple)
        case "points_wins":
            plot_and_save(players, 'points_wins', 'Hours', 'Points/Wins', "Points per Win ratio by Hour", output_dir, animate=animate, multiple=multiple)
        case "max_wins":
            plot_and_save(players, 'max_wins', 'Hours', 'Max wins achievable', "Theoretical max", output_dir, animate=animate, multiple=multiple)
        case "max_points":
            plot_and_save(players, 'max_points', 'Hours', 'Max points achievable', "Theoretical max", output_dir, animate=animate, multiple=multiple)
        case _:
            raise ValueError(f"Invalid type: {type}. Please choose from 'all', 'wins', 'points', 'wins_pace', 'points_pace', 'ranks', 'points_wins', 'max_wins', 'max_points'.")


    #I do agree it looks kinda ugly but there are some cases where I can't just use the f"{type}" for example for the titles there is prob an easier way and cleaner way to do this but idc and it's 3am 
    print("Generated players' data")


#animate = False  # Animated graphs will be set to False by default to save resources
#multiple = True
#
#render(data, output_dir)
#render(data[:3]+[data[7]], output_dir, multiple=True)
#
#theoretical_max(data[:3]+[data[7]], 'wins', 'wins_pace', 'Hours', 'Wins', 'Theoretical Max Wins by Hour', output_dir, animate=animate, multiple=multiple)
#theoretical_max(data[:3]+[data[7]], 'points', 'points_pace', 'Hours', 'Points', 'Theoretical Max Points by Hour', output_dir, animate=animate, multiple=multiple)
#
#print("Graphs have been generated and saved successfully.")

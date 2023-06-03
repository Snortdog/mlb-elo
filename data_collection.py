import re
import requests
import os
import glob
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from pybaseball import statcast
from pybaseball import statcast_batter, statcast_pitcher
from pybaseball import playerid_lookup
from selenium import webdriver
from datetime import date, timedelta
from bs4 import BeautifulSoup
from pybaseball import playerid_lookup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pybaseball import playerid_reverse_lookup



# Set directory paths for hitter and pitcher CSV files
hitters_csv = r"C:\Users\willa\OneDrive\Desktop\savantData\hitterData.csv"
pitchers_csv = r"C:\Users\willa\OneDrive\Desktop\savantData\pitcherData.csv"

failed_players_file = r"C:\Users\willa\OneDrive\Desktop\mlb-elo\failed_players.txt"
# Check if 'failed_players.txt' exists, and create it if it doesn't
if not os.path.exists(failed_players_file):
    with open(failed_players_file, "w") as f:
        pass
# Set directory path where CSV files are stored
data_directory = r"C:\Users\willa\OneDrive\Desktop\savantData" # Replace with the path to the directory containing the CSV files

# Get a list of all CSV files in the directory
csv_files = glob.glob(os.path.join(data_directory, "*.csv"))

# Load each file into a DataFrame and store it in a list
dataframes = [pd.read_csv(csv) for csv in csv_files]

# Merge all DataFrames into one
all_data = pd.concat(dataframes, ignore_index=True)

def browse_file():
    tk.Tk().withdraw()
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    return filepath

def get_statcast_pitcher_logs_for_player(player_id, start_date, end_date):
    try:
        player_info = playerid_reverse_lookup([player_id], key_type='mlbam')

        if player_info.empty:
            print(f"Could not find player information for MLBAM ID {player_id}. Skipping.")
            return None, None, pd.DataFrame()
            
        player_name = f"{player_info['name_first'].iloc[0]} {player_info['name_last'].iloc[0]}"

        play_logs = statcast_pitcher(start_date, end_date, player_id)

        return player_id, player_name, play_logs
    except Exception as e:
        print(f"Error fetching play logs for MLBAM ID {player_id}: {e}")
        return None, None, pd.DataFrame()
            
def get_statcast_logs_for_player_using_name(player_name, player_id, start_date, end_date):
    name_parts = player_name.split(', ')
    if len(name_parts) == 2:
        first_name, last_name = name_parts[1], name_parts[0]
    else:
        first_name, last_name = name_parts

    try:
        player_ids = playerid_lookup(last_name, first_name)
        if player_ids.empty:
            raise ValueError("Player ID not found")

        play_logs = statcast_batter(start_date, end_date, player_id)
        if play_logs.empty:
            play_logs = statcast_pitcher(start_date, end_date, player_id)
            return play_logs
    except ValueError as e:
        print(f"Error: {e}. Could not find play logs for {player_name} ({player_id}).")
        return pd.DataFrame()

    
    # Fetch the Statcast data using the player's MLBAM id
    data = statcast_batter(start_date, end_date, player_id)

    # Filter data by team, if provided
    #if team:
        #data = data[(data['home_team'].str.contains(team, case=False, na=False)) |
                    #(data['away_team'].str.contains(team, case=False, na=False))]
                    
    # Filter data by events
    filtered_data = data[data['events'].isin(['strikeout', 'walk', 'field_out', 'single', 'double', 'triple', 'home_run', 'hit_by_pitch', 'sac_bunt', 'sac_fly', 'field_error', 'fielders_choice', 'fielders_choice_out', 'force_out', 'double_play', 'sac_bunt_double_play', 'intentional_walk', 'gidp', 'triple_play'])]

    # Get player names for batters and pitchers
    all_mlbam_ids = pd.concat([filtered_data['batter'], filtered_data['pitcher']]).unique()
    player_id_name_map = {}

    for mlbam_id in all_mlbam_ids:
        player_info = player_ids[player_ids['key_mlbam'] == mlbam_id]
        if not player_info.empty:
            player_id_name_map[mlbam_id] = f"{player_info.iloc[0]['name_first']} {player_info.iloc[0]['name_last']}"

    batter_names = filtered_data['batter'].map(player_id_name_map)
    new_filtered_data = filtered_data.assign(batter_name=batter_names)

    # For pitchers
    pitcher_names = filtered_data['pitcher'].map(player_id_name_map)
    new_filtered_data = new_filtered_data.assign(pitcher_name=pitcher_names)

    return new_filtered_data.reset_index(drop=True)
    



# Constants for Expected Stats Leaderboards URLs
EXPECTED_STATS_HITTERS_URL = "https://baseballsavant.mlb.com/expected_statistics_leaderboard/items?type=batter&season=2023"
EXPECTED_STATS_PITCHERS_URL = "https://baseballsavant.mlb.com/expected_statistics_leaderboard/items?type=pitcher&season=2023"
    
# Set season, start_date, and end_date for play logs
season = 2023
start_date = '2023-03-30'
end_date = date.today().strftime("%Y-%m-%d")

#print("Please select the CSV file containing the list of hitters.")
#hitters_csv = r"C:\Users\willa\OneDrive\Desktop\savantData\hitterData.csv"

#print("Please select pitcher file")
#pitchers_csv = r"C:\Users\willa\OneDrive\Desktop\savantData\pitcherData.csv"

# Create the 'Events' folder
os.makedirs('Events', exist_ok=True)


hitters_df = pd.read_csv(hitters_csv)
pitchers_df = pd.read_csv(pitchers_csv)

successful_players = []
failed_players = []

with open(failed_players_file, "r") as f:
    failed_player_names = [line.strip() for line in f.readlines()]

hitters_player_info = hitters_df[['player_name', 'player_id']]
pitchers_player_info = pitchers_df[['player_name', 'player_id']]
all_player_info = pd.concat([hitters_player_info, pitchers_player_info], ignore_index=True)
failed_players_df = all_player_info[all_player_info['player_name'].isin(failed_player_names)]

# Loop to process failed players first:
for player_name in failed_player_names:
    player_id = failed_players_df[failed_players_df["player_name"] == player_name]["player_id"].item()

    


    play_logs = get_statcast_logs_for_player_using_name(player_name, player_id, start_date, end_date)

    if not play_logs.empty:
        successful_players.append(player_name)
        failed_player_names.remove(player_name)  # Remove the player from the failed_players list
        filename = f"Events/{player_name}_play_logs.csv"
        play_logs.to_csv(filename, index=False)
        print(f"Successfully fetched play logs for {player_name} ({player_id}).")
    else:
        # Store the failed players in the failed_players list for the next iteration
        failed_players.append(player_name)

# Process all players in the all_players_df DataFrame
for df in [hitters_player_info, pitchers_player_info]:
     for index, player in df.iterrows():
        player_name = player['player_name']
        player_id = player['player_id']

        if player_name not in successful_players:
            play_logs = get_statcast_logs_for_player_using_name(player_name, player_id, start_date, end_date)


        if not play_logs.empty:
            successful_players.append(player_name)
            filename = f"Events/{player_name}_play_logs.csv"
            play_logs.to_csv(filename, index=False)
        else:
            failed_players.append(player_name)

            
with open(failed_players_file, "w") as f:
    for player_name in [player['player_name'] for index, player in failed_players.iterrows()]:
        f.write(f"{player_name}\n")
    
    

print("Play logs saved.")

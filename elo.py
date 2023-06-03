import pandas as pd
import os
import glob

# Define constants
INITIAL_ELO = 1500
K_FACTOR = 20

weights = {
    'triple_play': -1.5,
    'sac_bunt_double_play': -1,
    'gidp': -0.75,
    'double_play': -0.7,
    'strikeout': -0.5,
    'field_out': -0.25,
    'force_out': -0.25,
    'error': 0,
    'fielders_choice_out': -0.15,
    'fielders_choice': 0,
    'sac_fly': 0.1,
    'sac_bunt': 0.1,
    'hit_by_pitch': 0.25,
    'intentional_walk': 0.2,
    'walk': 0.2,
    'single': 0.5,
    'double': 0.7,
    'triple': 1.0,
    'home_run': 1.5,
}

min_weight = min(weights.values())
max_weight = max(weights.values())

weight_range = max_weight - min_weight

normalized_weights = {event: (weight - min_weight) / weight_range for event, weight in weights.items()}

adjusted_weights = {event: (2 * weight - 1) for event, weight in normalized_weights.items()}




def is_valid_csv(file_path):
    try:
        temp_df = pd.read_csv(file_path)
        return len(temp_df.columns) > 0
    except pd.errors.EmptyDataError:
        return False


def load_play_logs(directory='Events'):
    csv_files = glob.glob(f"{directory}/*_play_logs.csv")

    # Read valid CSV files
    play_logs_list = []
    for csv in csv_files:
        if is_valid_csv(csv):  # Check if the file is a valid non-empty CSV with columns
            play_logs_list.append(pd.read_csv(csv))

    return play_logs_list

def calculate_expected_score(rating1, rating2):
    return 1 / (1 + 10**((rating2 - rating1) / 400))

def update_elo(rating1, rating2, score, k_factor):
    expected_score = calculate_expected_score(rating1, rating2)
    new_rating = rating1 + k_factor * (score - expected_score)
    return new_rating

def process_play_logs(play_logs_list, pitcher_elo_ratings, hitter_elo_ratings, k_factor):
    at_bats = {}  # Store the number of at-bats for each player
    for play_logs in play_logs_list:
        at_bat_outcomes = play_logs[play_logs["events"].isin(list(weights.keys()))]
        for index, row in at_bat_outcomes.iterrows():
            pitcher_id = row['pitcher']
            batter_id = row['batter']
            outcome = row['events']
            
            if batter_id not in at_bats:
                at_bats[batter_id] = 0
            at_bats[batter_id] += 1
        
            # Initialize separate ELO ratings for pitchers and hitters
            if pitcher_id not in pitcher_elo_ratings:
                pitcher_elo_ratings[pitcher_id] = INITIAL_ELO
            if batter_id not in hitter_elo_ratings:
                hitter_elo_ratings[batter_id] = INITIAL_ELO

            pitcher_initial_elo = pitcher_elo_ratings[pitcher_id]
            batter_initial_elo = hitter_elo_ratings[batter_id]

            # Update ELO ratings based on the outcome
            outcome_weight = weights[outcome]
            pitcher_new_elo = update_elo(pitcher_initial_elo, batter_initial_elo, 1 - outcome_weight / 10, k_factor)
            batter_new_elo = update_elo(batter_initial_elo, pitcher_initial_elo, outcome_weight / 10, k_factor)
    
            # Store the updated ELO ratings
            pitcher_elo_ratings[pitcher_id] = pitcher_new_elo
            hitter_elo_ratings[batter_id] = batter_new_elo

    return pitcher_elo_ratings, hitter_elo_ratings, at_bats
    
    
def create_leaderboards(pitcher_elo_ratings, hitter_elo_ratings, at_bats, all_player_info):
    #elo_data = [{"player_id": player_id, "elo_rating": elo_rating} for player_id, elo_rating in elo_ratings.items()]
     # Create separate DataFrames for pitcher_elo_ratings and hitter_elo_ratings
    pitcher_elo_df = pd.DataFrame(pitcher_elo_ratings.items(), columns=["player_id", "elo_rating"])
    hitter_elo_df = pd.DataFrame(hitter_elo_ratings.items(), columns=["player_id", "elo_rating"])
    at_bats_data = [{"player_id": player_id, "at_bats": at_bats_count} for player_id, at_bats_count in at_bats.items()]
    #elo_df = pd.DataFrame(elo_data)
    at_bats_df = pd.DataFrame(at_bats_data)
    
    # Merge innings_pitched information with pitchers_leaderboard
    #innings_pitched_data = [{"player_id": player_id, "innings_pitched": innings} for player_id, innings in innings_pitched.items()]
    #innings_pitched_df = pd.DataFrame(innings_pitched_data)
    #pitchers_leaderboard = pitchers_leaderboard.merge(innings_pitched_df, on="player_id", how="left")

    

    
    # Merge with all_player_info
    pitcher_leaderboards = all_player_info.merge(
        pd.DataFrame(pitcher_elo_ratings.items(), columns=["player_id", "elo_rating"]),
        on="player_id", how="left"
    ).merge(at_bats_df, on="player_id", how="left")

    hitter_leaderboards = all_player_info.merge(
        pd.DataFrame(hitter_elo_ratings.items(), columns=["player_id", "elo_rating"]),
        on="player_id", how="left"
    ).merge(at_bats_df, on="player_id", how="left")
    
    # Sort by ELO rating descending
    pitcher_leaderboards = pitcher_leaderboards.sort_values(by="elo_rating", ascending=False)
    hitter_leaderboards = hitter_leaderboards.sort_values(by="elo_rating", ascending=False)


    # Split pitchers and hitters
    pitchers_leaderboard = pitcher_leaderboards[pitcher_leaderboards["player_id"].isin(pitchers_player_info["player_id"])]
    hitters_leaderboard = hitter_leaderboards[hitter_leaderboards["player_id"].isin(hitters_player_info["player_id"])]
    
     # Define Shohei Ohtani's player_id (replace with the correct value)
    ohtani_id = 660271   # Replace this with Ohtani's actual player_id

    # Check if Ohtani's data is present in the leaderboards DataFrame
    ohtani_data = hitter_leaderboards[hitter_leaderboards["player_id"] == ohtani_id]


    # If the data is present, append it to the pitchers_leaderboard
    if not ohtani_data.empty:
        pitchers_leaderboard = pd.concat([pitchers_leaderboard, ohtani_data])
        pitchers_leaderboard = pitchers_leaderboard.sort_values(by="elo_rating", ascending=False)
    
     # Filter hitters with at least 1 plate appearance per game their team has played
    #hitters_leaderboard = hitters_leaderboard[(hitters_leaderboard['at_bats'] / hitters_leaderboard['team_game_max']) >= min_pa_per_game]
    
      # Filter pitchers with at least one inning per 5 games their team has played
    #pitchers_leaderboard['team_game_max'] = pitchers_leaderboard['player_id'].map(at_bats.groupby('player_id')['team_game'].max())
   # pitchers_leaderboard = pitchers_leaderboard[(pitchers_leaderboard['innings_pitched'] / (pitchers_leaderboard['team_game_max'] / 5)) >= min_ip_per_5_games]

    # Filter pitchers based on minimum innings pitched requirement
    #pitchers_leaderboard = pitchers_leaderboard[pitchers_leaderboard["innings_pitched"] >= min_innings_pitched]

    
    # Filter hitters with at least 50 at-bats
    hitters_leaderboard = hitters_leaderboard[hitters_leaderboard["at_bats"] >= 75]

    return pitchers_leaderboard, hitters_leaderboard

# Initialize separate dictionaries for pitcher and hitter ELO ratings
pitcher_elo_ratings = {}
hitter_elo_ratings = {}

play_logs_list = load_play_logs()

pitcher_elo_ratings, hitter_elo_ratings, at_bats = process_play_logs(play_logs_list, pitcher_elo_ratings, hitter_elo_ratings, K_FACTOR)

hitters_csv = r'C:\Users\willa\OneDrive\Desktop\savantData\hitterData.csv'
pitchers_csv = r'C:\Users\willa\OneDrive\Desktop\savantData\pitcherData.csv'

hitters_df = pd.read_csv(hitters_csv)
pitchers_df = pd.read_csv(pitchers_csv)
hitters_player_info = hitters_df[['player_name', 'player_id']]
pitchers_player_info = pitchers_df[['player_name', 'player_id']]



all_player_info = pd.concat([hitters_player_info, pitchers_player_info], ignore_index=True)

# Calculate total innings pitched for each pitcher
#innings_pitched = pitchers_df.groupby("player_id")["innings_pitched"].sum().to_dict()


pitchers_leaderboard, hitters_leaderboard = create_leaderboards(pitcher_elo_ratings, hitter_elo_ratings, at_bats, all_player_info)


pitchers_leaderboard.to_csv("pitchers_leaderboard.csv", index=False)
hitters_leaderboard.to_csv("hitters_leaderboard.csv", index=False)
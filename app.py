from flask import Flask, render_template, jsonify, request
import pandas as pd

app = Flask(__name__)

#hitters_csv = r'C:\Users\willa\OneDrive\Desktop\savantData\hitterData.csv'
#pitchers_csv = r'C:\Users\willa\OneDrive\Desktop\savantData\pitcherData.csv'

# Replace with the paths to your leaderboard CSV files
pitchers_leaderboard_csv = r'C:\Users\willa\OneDrive\Desktop\mlb-elo\pitchers_leaderboard.csv'
hitters_leaderboard_csv = r'C:\Users\willa\OneDrive\Desktop\mlb-elo\hitters_leaderboard.csv'

global hitters_lb, pitchers_lb
# Read leaderboards from CSV files
pitchers_lb = pd.read_csv(pitchers_leaderboard_csv)
hitters_lb = pd.read_csv(hitters_leaderboard_csv)


# Add img_url columns with profile picture URLs to the DataFrames
#pitchers_lb['img_url'] = 'https://www.baseballsavant.com/application/upload/player_pyramid/' + pitchers_lb['player_id'].astype(str) + '.png'
#hitters_lb['img_url'] = 'https://www.baseballsavant.com/application/upload/player_pyramid/' + hitters_lb['player_id'].astype(str) + '.png'

# Add the profile_url column with URLs to the players' Baseball Savant pages
#pitchers_lb['profile_url'] = 'https://baseballsavant.mlb.com/savant-player/' + pitchers_lb['player_id'].astype(str)
#hitters_lb['profile_url'] = 'https://baseballsavant.mlb.com/savant-player/' + hitters_lb['player_id'].astype(str)

# Drop duplicate rows based on player_id
#hitters_lb = hitters_lb.drop_duplicates(subset='player_id')
#hitters_lb = pd.DataFrame()
#pitchers_lb = pd.DataFrame()

# Calculate mean ELO scores for hitters and pitchers
mean_hitter_elo = hitters_lb['elo_rating'].mean()
mean_pitcher_elo = pitchers_lb['elo_rating'].mean()

# Calculate scaling factors
hitter_scaling_factor = mean_pitcher_elo / mean_hitter_elo
pitcher_scaling_factor = 1  # Keep pitchers' ELO unchanged

# Normalize ELO scores using the scaling factors
hitters_lb['normalized_elo'] = hitters_lb['elo_rating'] * hitter_scaling_factor
pitchers_lb['normalized_elo'] = pitchers_lb['elo_rating'] * pitcher_scaling_factor

# Rename the 'normalized_elo' column to 'elo'
hitters_lb.rename(columns={'elo': 'elo_rating'}, inplace=True)
pitchers_lb.rename(columns={'elo': 'elo_rating'}, inplace=True)

# After creating the 'pitchers_leaderboard' and 'hitters_leaderboard' DataFrames
pitchers_lb.reset_index(drop=True, inplace=True)
hitters_lb.reset_index(drop=True, inplace=True)

# Set the index to start at 1
pitchers_lb.index = pitchers_lb.index + 1
hitters_lb.index = hitters_lb.index + 1

@app.route('/')
def index():
    return render_template('index.html')

#@app.route('/leaderboards')
#def leaderboards():
    # Read leaderboards from CSV files
    #pitchers_leaderboard = pd.read_csv(pitchers_leaderboard_csv)
    #hitters_leaderboard = pd.read_csv(hitters_leaderboard_csv)

    # Drop duplicate rows based on player_id
    #hitters_leaderboard = hitters_leaderboard.drop_duplicates(subset='player_id')

    # Convert DataFrames to HTML tables
    #pitchers_table = pitchers_leaderboard.to_html(classes='table table-striped')
    #hitters_table = hitters_leaderboard.to_html(classes='table table-striped')

    # Render HTML template with the tables
    #return render_template("leaderboards.html", pitchers_table=pitchers_table, hitters_table=hitters_table) 
    
@app.route('/hitters_leaderboard')
def hitters_leaderboard():
    global hitters_lb
    # Read leaderboards from CSV files
    #hitters_lb = pd.read_csv(hitters_leaderboard_csv)
    print("Hitters columns:", hitters_lb.columns)
    # Drop duplicate rows based on player_id
    hitters_lb = hitters_lb.drop_duplicates(subset='player_id')
    
    #hitters_display = hitters_lb.drop(columns=["at_bats"])
    #hitters_lb.drop(columns=["at_bats"], inplace=True)
    #hitters_lb = hitters_lb.drop(columns=["player_id"])
    
    if "at_bats" in hitters_lb.columns:
        hitters_lb.drop(columns=["at_bats"], inplace=True)
        
    if "elo_rating" in hitters_lb.columns:
        hitters_lb.drop(columns=["elo_rating"], inplace=True)
    
    #if "player_id" in hitters_lb.columns:
        #hitters_lb.drop(columns=["player_id"], inplace=True)
    # Reset the index to start at 1
    #hitters_lb.index = hitters_lb.index + 1
    
    # Convert hitters_leaderboard DataFrame to an HTML table
    hitters_table = hitters_lb.to_html(classes='table table-striped')

    # Render HTML template with the hitters_table
    return render_template("hitters_leaderboard.html", hitters_table=hitters_table)
    
@app.route('/pitchers_leaderboard')
def pitchers_leaderboard():
    global pitchers_lb
    # Read leaderboards from CSV files
    #pitchers_lb = pd.read_csv(pitchers_leaderboard_csv)
    print("Pitchers columns:", pitchers_lb.columns)
    
    #pitchers_display = pitchers_lb.drop(columns=["at_bats"])
    #pitchers_lb.drop(columns=["at_bats"], inplace=True)
    #pitchers_lb = pitchers_lb.drop(columns=["player_id"])
    
    if "at_bats" in pitchers_lb.columns:
        pitchers_lb.drop(columns=["at_bats"], inplace=True)
        
    if "elo_rating" in pitchers_lb.columns:
        pitchers_lb.drop(columns=["elo_rating"], inplace=True)
      
    #if "player_id" in pitchers_lb.columns:
       # pitchers_lb.drop(columns=["player_id"], inplace=True)
    
    # Reset the index to start at 1
    #pitchers_lb.index = pitchers_lb.index + 1
    
    # Convert pitchers_leaderboard DataFrame to an HTML table
    pitchers_table = pitchers_lb.to_html(classes='table table-striped')

    # Render HTML template with the pitchers_table
    return render_template("pitchers_leaderboard.html", pitchers_table=pitchers_table)
    
@app.route('/search_player', methods=['GET'])
def search_player():
    global hitters_lb, pitchers_lb
    # Getthe player's name from the search form
    search_name = request.args.get('search_name').lower()
    # Print columns of the DataFrames
    print("Hitters columns:", hitters_lb.columns)
    print("Pitchers columns:", pitchers_lb.columns)
      # Raise an error if the "player_name" column is not found in either DataFrame
    #if 'player_name' not in hitters_lb.columns or 'player_name' not in pitchers_lb.columns:
        #raise ValueError("The 'player_name' column is missing from one of the DataFrames")
    
    # Search for the player in hitters and pitchers leaderboards
    searched_hitters = hitters_lb[hitters_lb['player_name'].str.lower().str.contains(search_name)]
    searched_pitchers = pitchers_lb[pitchers_lb['player_name'].str.lower().str.contains(search_name)]
    
    # Reset the index of the search results to start at 1 and keep their original position
   # searched_hitters.index = searched_hitters.index + 1
   # searched_pitchers.index = searched_pitchers.index + 1

    hitters_table = searched_hitters.to_html(classes='table table-striped', index_names=False, index=True)
    pitchers_table = searched_pitchers.to_html(classes='table table-striped', index_names=False, index=True)
    # Convert DataFrames to HTML tables without the "at_bats" column
    #hitters_table = searched_hitters.to_html(classes='table table-striped', index=False)
    #pitchers_table = searched_pitchers.to_html(classes='table table-striped', index=False)

    # Render HTML templates with search results
    return render_template("search_results.html", hitters_table=hitters_table, pitchers_table=pitchers_table) 

#hitters_table = hitters_leaderboard.to_html(classes='table table-striped')
#pitchers_table = pitchers_leaderboard.to_html(classes='table table-striped')
    
if __name__ == '__main__':
    app.run(debug=True)
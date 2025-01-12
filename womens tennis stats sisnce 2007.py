import warnings
import os
import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Path to chromedriver (update this to your local path for chromedriver)
driver_path = "/path/to/chromedriver"  # Update the path to chromedriver on your machine

# Initialize the Service and Options for the WebDriver
service = Service(driver_path)
options = Options()
options.add_argument("--headless")  # Run headless if you don't need the browser window to open

# Initialize WebDriver with Service and Options
driver = webdriver.Chrome(service=service, options=options)

# Open the WTA Rankings page
wta_url = "https://www.wtatennis.com/rankings/singles"
driver.get(wta_url)

# Initialize empty lists to store player names and ranks
players = []
ranks = []

try:
    # Wait until the rankings table is loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody.js-rankings-body tr"))
    )

    # Click the "Load More" button 5 times to load additional rankings
    for i in range(5):
        try:
            # Check if the overlay (cookie consent) is present and close it
            overlay = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".onetrust-pc-dark-filter.ot-fade-in"))
            )

            # If overlay is visible, close it
            if overlay.is_displayed():
                close_button = driver.find_element(By.CSS_SELECTOR, ".onetrust-pc-btn-handler")
                close_button.click()  # Close the overlay
                print(f"Overlay closed during load more attempt {i + 1}")

            # Scroll down the page to make sure the "Load More" button is in view
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the page to scroll down

            # Wait for the "Load More" button to be clickable and click it
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.rankings__show-more.js-mobile-load-more"))
            )
            print(f"'Load More' button found, clicking...")

            # Scroll the button into view and click it using JavaScript (to bypass any visual block)
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            driver.execute_script("arguments[0].click();", load_more_button)
            print(f"Clicked 'Load More' button during load more attempt {i + 1}")

            # Wait for the rankings to load after each click
            time.sleep(3)  # Wait for the new rankings to be loaded

        except Exception as e:
            print(f"Error during load more attempt {i + 1}: {e}")
            break  # Stop the loop if there's an issue with the button

    # Extract rankings after all "Load More" actions are done
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody.js-rankings-body tr")

    # Extract rank and player name after all pages have loaded
    for row in rows:
        try:
            rank = row.find_element(By.CSS_SELECTOR, "span.rankings__rank").text.strip()
        except Exception:
            rank = None  # If there's an error, store None for rank

        try:
            name = row.get_attribute("data-player-name").strip()
        except Exception:
            name = None  # If there's an error, store None for player name

        if name and rank:
            players.append(name)
            ranks.append(rank)

    # Create a DataFrame with player name and rank
    wta_rankings = pd.DataFrame({"Player": players, "Rank": ranks})

    # Reassign ranks from 1 to 100
    wta_rankings['Rank'] = range(1, len(wta_rankings) + 1)

    # Slice the DataFrame to get the first 100 rows
    wta_rankings = wta_rankings.head(100)

    # Define the path to save the CSV file on your Desktop (or any location you prefer)
    save_path = "/path/to/your/folder/wta_rankings.csv"  # Update to desired directory

    # Save the data to a CSV file
    wta_rankings.to_csv(save_path, index=False)

    # Print the file location
    print(f"CSV file saved at: {save_path}")

except Exception as e:
    print(f"Error while scraping WTA rankings: {e}")

finally:
    driver.quit()

# Format the Player Names in the Rankings Dataset
wta_ranking_df = pd.read_csv('/path/to/your/folder/wta_rankings.csv')  # Update path to saved file

# Format player names to "Last Name, First Initial"
wta_ranking_df['Formatted_Player'] = wta_ranking_df['Player'].apply(
    lambda x: ' '.join([x.split()[-1], x.split()[0][0] + '.']))

# Save the dataset with formatted player names
formatted_wta_ranking_path = '/path/to/your/folder/formatted_wta_rankings.csv'  # Update path
wta_ranking_df.to_csv(formatted_wta_ranking_path, index=False)
print(f"Formatted ranking data saved to: {formatted_wta_ranking_path}")

# Load the WTA Historical Match Data and Filter Players
wta_df = pd.read_csv('/path/to/your/folder/wta.csv', low_memory=False)  # Update path
player_history_df = pd.read_csv('/path/to/your/folder/wta.csv', low_memory=False)  # Update path

# Load the formatted rankings dataset (current rankings)
current_rankings_df = pd.read_csv("/path/to/your/folder/formatted_wta_rankings.csv")  # Update path

# Load Player History and Rankings for Analysis
player_ranking_df = pd.read_csv('/path/to/your/folder/formatted_wta_rankings.csv')  # Update path

# Convert 'Date' column to datetime format
player_history_df['Date'] = pd.to_datetime(player_history_df['Date'], errors='coerce')

# Remove time portion from 'Date' column
player_history_df['Date'] = player_history_df['Date'].dt.date


# Functions to Get Stats for Player Overview and H2H
def get_h2h(player_1, player_2, surface=None, tournament=None):
    matches = player_history_df[((player_history_df['Player_1'] == player_1) &
                                 (player_history_df['Player_2'] == player_2)) |
                                ((player_history_df['Player_1'] == player_2) &
                                 (player_history_df['Player_2'] == player_1))]

    if surface:
        matches = matches[matches['Surface'] == surface]
    if tournament:
        matches = matches[matches['Tournament'] == tournament]

    wins_player_1 = matches[matches['Winner'] == player_1]
    wins_player_2 = matches[matches['Winner'] == player_2]

    return len(wins_player_1), len(wins_player_2), len(matches), matches

def get_player_rank(player):
    rank = player_ranking_df.loc[player_ranking_df['Formatted_Player'] == player, 'Rank'].values
    return rank[0] if len(rank) > 0 else "Rank Not Available"

def get_player_overview(player):
    total_matches = player_history_df[(player_history_df['Player_1'] == player) |
                                      (player_history_df['Player_2'] == player)]
    total_wins = total_matches[total_matches['Winner'] == player]
    total_losses = len(total_matches) - len(total_wins)

    surfaces = ['Hard', 'Clay', 'Grass']
    surface_stats = []
    for surface in surfaces:
        surface_matches = total_matches[total_matches['Surface'] == surface]
        surface_wins = surface_matches[surface_matches['Winner'] == player]
        surface_losses = len(surface_matches) - len(surface_wins)
        surface_stats.append({
            "Surface": surface,
            "Matches Played": len(surface_matches),
            "Wins": len(surface_wins),
            "Losses": surface_losses
        })

    tournaments = total_matches['Tournament'].unique()
    tournament_stats = []
    for tournament in tournaments:
        tournament_matches = total_matches[total_matches['Tournament'] == tournament]
        tournament_wins = tournament_matches[tournament_matches['Winner'] == player]
        tournament_losses = len(tournament_matches) - len(tournament_wins)
        tournament_stats.append({
            "Tournament": tournament,
            "Matches Played": len(tournament_matches),
            "Wins": len(tournament_wins),
            "Losses": tournament_losses
        })

    return total_matches, total_wins, total_losses, surface_stats, tournament_stats

# Streamlit Web Interface
st.title("Womens Tennis Player Stats Comparison & Overview Since 2007")

stats_choice = st.radio("Select View", ["Player Comparison", "Player Overview"])

if stats_choice == "Player Overview":
    players = sorted(set(player_history_df['Player_1']).union(set(player_history_df['Player_2'])))
    player = st.selectbox("Select Player", players)

    player_overview = get_player_overview(player)
    total_matches = player_overview[0]
    total_wins = player_overview[1]
    total_losses = player_overview[2]

    st.subheader(f"Overall Stats for {player}")
    st.write(f"Matches Played: {len(total_matches)}")
    st.write(f"Wins: {len(total_wins)}")
    st.write(f"Losses: {total_losses}")

    player_rank = get_player_rank(player)
    st.write(f"Player Rank: {player_rank}")

    st.subheader("Surface-wise Stats")
    surface_stats_df = pd.DataFrame(player_overview[3])
    st.table(surface_stats_df)

    st.subheader("Tournament-wise Stats")
    tournament_stats_df = pd.DataFrame(player_overview[4])
    st.table(tournament_stats_df)

elif stats_choice == "Player Comparison":
    players = sorted(set(player_history_df['Player_1']).union(set(player_history_df['Player_2'])))
    player_1 = st.selectbox("Select Player 1", players)
    player_2 = st.selectbox("Select Player 2", players)

    comparison_type = st.radio("Select Comparison Type", ["Tournament Comparison", "Overall Comparison"])

    if comparison_type == "Tournament Comparison":
        tournaments = sorted(player_history_df['Tournament'].unique())
        tournament = st.selectbox("Select Tournament", tournaments)

        surfaces = sorted(player_history_df[player_history_df['Tournament'] == tournament]['Surface'].unique())
        surface = st.selectbox("Select Surface", surfaces)

        if st.button("Show Tournament Stats"):
            h2h_tournament = get_h2h(player_1, player_2, tournament=tournament)
            st.subheader(f"H2H Stats: {player_1} vs {player_2} in Tournament: {tournament}")
            h2h_data = {
                "Metric": ["H2H in Tournament"],
                f"{player_1} Wins": [h2h_tournament[0]],
                f"{player_2} Wins": [h2h_tournament[1]],
                "Total Matches": [h2h_tournament[2]],
            }
            h2h_df = pd.DataFrame(h2h_data)
            st.table(h2h_df)

            matches = h2h_tournament[3]
            match_scores = matches[['Player_1', 'Player_2', 'Score', 'Date']]
            match_scores['Date'] = match_scores['Date'].dt.strftime('%Y-%m-%d')
            match_scores.reset_index(drop=True, inplace=True)
            st.table(match_scores)

    elif comparison_type == "Overall Comparison":
        if st.button("Show Overall Stats"):
            h2h_overall = get_h2h(player_1, player_2)

            st.subheader(f"Overall H2H Stats: {player_1} vs {player_2}")
            h2h_data_overall = {
                "Metric": ["Overall H2H"],
                f"{player_1} Wins": [h2h_overall[0]],
                f"{player_2} Wins": [h2h_overall[1]],
                "Total Matches": [h2h_overall[2]],
            }
            h2h_df_overall = pd.DataFrame(h2h_data_overall)
            st.table(h2h_df_overall)

            surfaces = ['Hard', 'Clay', 'Grass']
            surface_stats = []
            for surface in surfaces:
                h2h_surface = get_h2h(player_1, player_2, surface=surface)
                surface_stats.append({
                    "Surface": surface,
                    f"{player_1} Wins": h2h_surface[0],
                    f"{player_2} Wins": h2h_surface[1],
                    "Total Matches": h2h_surface[2],
                })

            st.subheader(f"H2H Stats for each Surface")
            surface_stats_df = pd.DataFrame(surface_stats)
            st.table(surface_stats_df)

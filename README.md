# Womens-Tennis-Stats-since-2007
# WTA Tennis Player Stats Comparison & Overview

This project provides a comprehensive overview of the Women's Tennis Association (WTA) player rankings, player statistics, and head-to-head (H2H) comparisons using historical match data. It uses web scraping techniques with Selenium to extract the WTA rankings, processes the data, and allows users to explore player stats via a Streamlit-based web interface.

## Features

- **WTA Rankings Scraping**: Scrape and save the top 100 WTA player rankings.
- **Player Stats Overview**: View overall stats, surface-wise performance, and tournament-wise performance of a selected player.
- **Head-to-Head (H2H) Comparison**: Compare two players' performances in specific tournaments or overall.
- **Interactive Web Interface**: Built using Streamlit to allow users to easily interact with the data and visualize stats.

  ## Project Files

- `womens tennis stats since 2007.py`: Python script containing the main logic for scraping, processing, and displaying player stats.
- `wta.csv`: Historical match data obtained from [Kaggle: WTA Tennis 2007-2023 Daily Update](https://www.kaggle.com/datasets/dissfya/wta-tennis-2007-2023-daily-update).
- `wta_rankings.csv`: Output CSV file containing the top 100 WTA player rankings.
- `formatted_wta_rankings.csv`: CSV file containing player rankings with formatted player names.
- `requirements.txt`: List of Python packages required for the project.


## Prerequisites

Before running the project, ensure that you have the following installed:
- Python 3.x
- Selenium
- Streamlit
- Pandas
- Chrome WebDriver (for web scraping)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/santhosharun99/Womens-Tennis-Stats-since-2007.git
   cd Womens-Tennis-Stats-since-2007

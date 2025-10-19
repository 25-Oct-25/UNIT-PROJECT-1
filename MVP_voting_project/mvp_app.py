import sqlite3
import pandas as pd
import csv
from tabulate import tabulate
import os

DATABASE_NAME = "mvp_votes.db"
PLAYER_DATA_FILE = "plyers_data.cvs"

def create_initial_players_data():
    '''Generates the initial CVS file for the players statistics. '''

    players_data= [
                   ['Name', 'Team', 'PPG', 'RPG', 'APG', 'Games_Played'], 
                   ['Nikola Jokic', 'Denver Nuggets', 26.4, 12.4, 9.0, 79],
                   ['Shai Gilgeous-Alexander', 'Oklahoma City Thunder', 30.1, 5.5, 6.2, 80],
                   ['Luka Doncic', 'Dallas Mavericks', 33.9, 9.2, 9.8, 70],
                   ['Giannis Antetokounmpo', 'Milwaukee Buckes', 30.4, 11.5, 6.5, 73],
                   ['Jayson Tatum', 'Boston Celtics', 26.9, 8.1, 4.9, 76]
                ]
    
    try:
        with open(PLAYER_DATA_FILE, "w", encoding="UTF-8", newline='') as cvsfile:
            writer = csv.writer(cvsfile)
            writer.writerow(players_data)
            print(f"Initial plyer data file created: {PLAYER_DATA_FILE}")
    except Exception as e:
        print(f"Error occurred while creating the file!\n{e}")

create_initial_players_data()
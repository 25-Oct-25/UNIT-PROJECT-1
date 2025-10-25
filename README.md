🏀 Fantasy Basketball Trade Analyzer

A Python-based command-line application designed to provide objective, category-based analysis for fantasy basketball trades. It uses the Z-Score methodology to calculate the normalized fantasy value of players across nine standard categories (9-CAT), helping users determine which side wins a proposed trade.

The application features an interactive menu, season selection, robust typo correction (fuzzy matching), and a styled console output using rich library.

Features:

- Objective Analysis (9-CAT): Analyzes players based on the nine standard fantasy categories (PTS, REB, AST, STL, BLK, FG%, FT%, 3PM, TOV).

- Z-Score Methodology: Calculates each player's value based on Standard Deviations from the league mean, providing a clear, normalized Total Z-Score.

- Interactive Menu: Seamlessly switch between viewing individual player stats and analyzing complex trades.

- Season Selector: Fetches official NBA data for the specific season you choose (e.g., 2024-25, 2023-24,...).

- Fuzzy Matching & Correction: Handles common player name typos (e.g., typing "Lebrone" will suggest "LeBron James").

- Styled Output: Uses the rich library for highly readable, colored, and professional-looking tables and reports.

 Install Dependencies:

 The application relies on several powerful Python packages:

 - nba_api
 - pandas
 - fuzzywuzzy
 - rich
import pandas as pd
from fuzzywuzzy import process, fuzz

class PlayerManagement:

    def __init__(self, categories):
        self.categories = categories
        self.z_cols = [cat + '_Z' for cat in self.categories]

    
    def resolve_player_names(self, input_names, avalible_players_list):

        matched_names= []
        unmatched_names= []

        print(f"\nAttempting to resolve {len(input_names)} player names...")

        for name in input_names:
            best_match= process.extractOne(
                name,
                avalible_players_list,
                score_cutoff= 85,
                scorer= fuzz.token_sort_ratio
            )
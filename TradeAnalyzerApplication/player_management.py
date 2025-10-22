from fuzzywuzzy import process,fuzz
from rich.console import Console
from rich.table import Table
from rich.progress import track


class PlayerManagement:
    '''Maneges all players logic includin Z-score calculation and name resolving'''

    def __init__(self, categories):
        self.categories= categories
        self.score_cutoff= 85
        self.z_cols= [cat +'_Z' for cat in self.categories]
        self.console= Console()
    
    def __calculate_total_z(self,df):
        '''Calculates the total Z-score value for each player'''
        positive_z_cols = [cat + '_Z' for cat in self.categories if cat != 'TOV']
        tov_z_col = 'TOV_Z'
        df['TOTAL_Z_SCORE'] = df[positive_z_cols].sum(axis=1) - df [tov_z_col]
        return df
    
    def calculate_z_scores(self, df_stats, console):
        '''Calculates Z-score for each category for every player.
        Z-Score = (Player Stats- Category Mean) / Category Standard Deviation
        '''

        df_z_scores = df_stats.copy()

        for cat in track(self.categories, description= "[bold blue]Calculating Z-Scores...[/bold blue]"):
            mean = df_stats[cat].mean()
            std =  df_stats[cat].std()

            if cat == 'TOV':
                df_z_scores[cat+'_Z'] = (mean - df_stats[cat]) / std
            else:
                df_z_scores[cat + '_Z'] = (df_stats[cat] - mean) / std

        df_z_scores = self.__calculate_total_z(df_z_scores)
        console.print("\n[bold green]Z-Scores calclation completed successfuly[/bold green]")
        return df_z_scores
    
    def player_stats_report(self, player_info, console):
        '''Prints a detailed report for a single player'''


        console.print(f"\n[bold green]Player Report: {player_info['PLAYER_NAME']}[/bold green]", style="bold")
        console.print(f"[yellow]Total Z-Score Value: {player_info['TOTAL_Z_SCORE']:.2f}[/yellow]\n")

        table = Table(title="Player Statistics and Value", show_header= True, header_style= "bold cyan", border_style= "green")
        table.add_column("Category",style= "magenta",justify= "left")
        table.add_column("Statistics", justify="right")
        table.add_column("Z-Score", justify="right")

        for cat in self.categories:
            z_score = player_info[cat + '_Z']
            stat_value = player_info[cat]

            score_style = "green3" if z_score >=0 else "red3"

            if cat in ['FG_PCT', 'FT_PCT']:
                stats_str= f"{stat_value:.3f}"
            else:
                stats_str= f"{stat_value:.1f}"
            
            table.add_row(
                cat,
                stats_str,
                f"[{score_style}]{z_score:+.3f}[/]"
            )

        console.print(table)


    def resolve_players_names(self, input_names, avalible_players_list, console):
        '''Resolve user input names that may contain some typos and display the user name suggestions'''

        matched_names=[]
        
        console.print("\n[bold]--- Resolving Player/s ---[/bold]", style="blue")

        for name in input_names:
            resolved = False
            current_input = name

            while not resolved:

                best_match, score= process.extractOne(
                    current_input,
                    avalible_players_list,
                    scorer=fuzz.token_sort_ratio
                )

                if score>= self.score_cutoff:
                    console.print(f"    [green]Matched found for[/green] '[cyan]{name}[/cyan]' with '{best_match}' ([dim]Score: {score}[/dim]) ")
                    matched_names.append(best_match)
                    resolved= True

                else:
                    console.print(f"    [red]Cannot find a strong match[/red] for '[cyan]{current_input}[/cyan]'")
                    suggestions = process.extract(
                        current_input,
                        avalible_players_list,
                        scorer= fuzz.token_sort_ratio,
                        limit=5
                    )

                    console.print("\n   [yellow]Did you mean? (Enter the number of the name or re-type the name. Press 'Enter' to skip):[/yellow]")

                    suggestions_table= Table(show_header=True, border_style="dim", width=40)
                    suggestions_table.add_column("", width=3, style="bold magenta")
                    suggestions_table.add_column("Player Name", style="white")
                    suggestions_table.add_column("Score", justify="right", style="dim")

                    for index, (name,score) in enumerate(suggestions, 1):
                        suggestions_table.add_row(
                            f"{index}.",
                            name,
                            f"{score}"
                        )

                    console.print(suggestions_table)

                    try:
                        user_choice= input(" -->  ").strip()
                        if user_choice.isdigit():
                            name_index = int(user_choice) - 1
                            if 0 <= name_index < len(suggestions):
                                selected_name= suggestions[name_index][0]

                                console.print(f"    [green]Selected name:[/green] '{selected_name}'.")
                                matched_names.append(selected_name)
                                resolved=True
                            else: 
                                console.print("     [red]Invalid number.[/red] Please try again", style= "bold red")
                        elif user_choice:
                            current_input= user_choice
                            console.print((f"    Retry matching with new name: '[yellow]{current_input}[/yellow]'..."))
                        elif user_choice == "":
                            raise Exception("No player enterd. Returning to main menu.")

                    except Exception as e:
                        self.console.print(f"[red]{e}[/red]")
                        return

        return matched_names
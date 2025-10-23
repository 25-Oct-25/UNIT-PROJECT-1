import time
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from data_fetcher import DataFetcher
from player_management import PlayerManagement


class TradeAnalyzerApp:
    '''The main application file'''
    
    def __init__(self):
        self.fantasy_categories= [
            'FG_PCT', 'FT_PCT', 'FG3M', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV' 
        ]
        self.min_gp =20
        self.current_season = '2024-25'
        self.data_fetcher= None
        self.player_management= None
        self.df_z_scores= None
        self.available_players_list=[]
        self.is_data_fetched= False
        self.console= Console()

    def __user_player_name_input(self, prompt):

        '''Prompt the user to enter the player name'''

        self.console.print(prompt,style="bold yellow")

        try:
            user_input= input(" --> ").strip()
            if user_input.isdigit():
                raise Exception ("Please enter a valid name")
        except Exception as e:
            self.console.print(f"{e}", style="red")
            return

        players_names= [name.strip() for name in user_input.split(',') if name.strip()]
        return players_names
    
    def __user_season_choice(self):
        '''Prompt the user to change the NBA season for analysis'''

        while True:
            self.console.print("\nEnter the NBA season (e.g., 2024-25):", style="cyan")
            try:
                season_input = input(f"[{self.current_season}] --> ").strip()

                if not season_input:
                    self.console.print(f"Using current season: [green]{self.current_season}[/green]")
                    return self.current_season

                if pd.Series([season_input]).str.match(r'^\d{4}-\d{2}$').iloc[0]:
                    return season_input
                else:
                    self.console.print("Invalid format. Please use YYYY-YY (e.g., 2023-24).", style="red")
            except Exception as e:
                print(e)
                return
                
            
    def __generate_report(self, team_a_players, team_b_players, total_z_a, total_z_b):
        '''To generate the trade report'''

        def create_tables(df, title, total_z):
            '''To generate the tables for the trade report'''

            table= Table(
                title=f"{title}| Total Z-Score: {total_z:+.2f}",
                show_header= True,
                header_style="bold magenta",
                title_style="bold white on blue",
                border_style="blue"
            )

            table.add_column("Player", style="cyan", justify="left")
            table.add_column("Total Z", style="bold white", justify="right")

            for _, row in df.iterrows():
                z_score = row["TOTAL_Z_SCORE"]

                score_style= "bold green" if z_score >=0 else "bold red"

                table.add_row(
                    row["PLAYER_NAME"],
                    f"[{score_style}]{z_score:+.2f}[/]"
                )
            return table
        

        self.console.print("\n[bold]--- FANTASY TRADE ANALSIS[/bold] ---\n",style="white")

        df_a_sort = team_a_players[['PLAYER_NAME', 'TOTAL_Z_SCORE']].sort_values(by= 'TOTAL_Z_SCORE', ascending=False)
        table_a=create_tables(df_a_sort, "Team 'A' (Giving Up)", total_z_a)
        self.console.print(table_a)

        df_b_sort= team_b_players[['PLAYER_NAME', 'TOTAL_Z_SCORE']].sort_values(by= 'TOTAL_Z_SCORE', ascending= False)
        table_b= create_tables(df_b_sort, "Team 'B' (Receiving)", total_z_b)
        self.console.print(table_b)

        value_difference = abs(total_z_a - total_z_b)

        if total_z_a > total_z_b:
            result= f"[bold dodger_blue1]Team'B' wins the trade by {value_difference:.2f} Z-Score Unit![/bold dodger_blue1]"
            result_style= "on blue"
        elif total_z_b > total_z_a:
            result= f"[bold dodger_blue1]Team'A' wins the trade by {value_difference:.2f} Z-Score Unit![/bold dodger_blue1]"
            result_style= "on blue"
        else:
            result= f"[bold yellow]Trade is even.[/bold yellow]"
            result_style= "on grey42"
        
        self.console.print(f"[bold]RRESULTS[/bold]: {result}", style= result_style)

        if len(team_a_players)== 1 and len(team_b_players)==1:
            player_a_z= team_a_players[[col for col in self.player_management.z_cols if col.endswith('_Z')]].iloc[0]
            player_b_z= team_b_players[[col for col in self.player_management.z_cols if col.endswith('_Z')]].iloc[0]

            comparison_table = Table(
                title= "Detailed Category Comparison",
                show_header= True,
                header_style= "bold yellow",
                border_style= "yellow"
            )

            comparison_table.add_column("Category", style="cyan", justify="left")
            comparison_table.add_column("Difference", justify="right")

            for cat in self.fantasy_categories:
                diff = player_a_z[cat +'_Z'] - player_b_z[cat +'_Z']
                diff_style = "bold green" if diff >0.05 else ("bold red" if diff < -0.05 else "white")

                comparison_table.add_row(
                    cat,
                    f"[{diff_style}]{diff:+.2f}[/]"
                )
            self.console.print("\n[bold]--- CATEGORY BREAKDOWN ---[/bold]")
            self.console.print(comparison_table)

    def __data_fetching_check(self, force_reset= False):
        '''To check if the data is fetched and prepared when the user change the season'''

        if self.is_data_fetched and not force_reset:
            return True
        
        new_season= self.__user_season_choice()
        if new_season is None:
            return False
        else:
            self.current_season = new_season

        self.console.print((f"\n[bold blue]Fetching data for season: [cyan]{self.current_season}[/cyan]..."))

        self.data_fetcher= DataFetcher(
            season=self.current_season,
            min_gp=self.min_gp,
            categories=self.fantasy_categories
        )

        self.player_management = PlayerManagement(categories=self.fantasy_categories)

        df_stats =self.data_fetcher.fetch_and_prepare()
        time.sleep(1)

        if df_stats is None:
            self.console.print(f"[bold red]Error occured while fetching data for {self.current_season}.", style="bold red")
            self.is_data_fetched= False
            return False
        
        self.df_z_scores = self.player_management.calculate_z_scores(df_stats, self.console)
        self.available_players_list = df_stats['PLAYER_NAME'].tolist()

        self.is_data_fetched=True
        self.console.print(f"[bold green]Data for [cyan]{self.current_season}[/cyan] ready. Welcome!\n", style="bold")
        return True
    
    def __change_season(self):
        '''To force re-fetching the data when the user change the season'''
        self.is_data_fetched = False
        self.df_z_scores = None
        self.available_players_list =[]

        self.__data_fetching_check(force_reset=True)

    def view_player_stats(self):
        '''To display player stats'''

        if not self.__data_fetching_check():
            return
        
        self.console.print("\n[bold]VIEW PLAYER STATS[/bold]", style="dark_orange")
        input_name= self.__user_player_name_input("Enter the player name to display his stats:")

        try:
            if not input_name:
                raise Exception ("No player enterd. Returning to main menu.")

            else:
                 if input_name:
                    matched= self.player_management.resolve_players_names(input_name, self.available_players_list, self.console)

            if matched:
                player_name = matched[0]
                player_data = self.df_z_scores[self.df_z_scores['PLAYER_NAME'] == player_name].iloc[0]
                self.player_management.player_stats_report(player_data, self.console)

            else:
                self.console.print("Stats lookup failed. Please make sure the name is entered correctly and try again.",style="red")
        except Exception as e:
            self.console.print(f"[red]{e}[/red]")
            return


    def analyze_trade_flow(self):
        '''to prepare the information for the trade analysis'''
        
        if not self.__data_fetching_check():
            return

        self.console.print("\n[bold]ANALYZE THE TRADE[/bold]", style="magenta")

        try:
            team_a= self.__user_player_name_input("Enter the player/s for team 'A' (Giving Up), separated by commas (e.g., LeBron James, Austin Reaves)")
            team_b= self.__user_player_name_input("Enter the player/s for team 'B' (Receiving), separated by commas (e.g., LeBron James, Austin Reaves)")

            if not team_a or not team_b:
                raise Exception ("Analysis aborted: Please enter at least one player for each team.")                
            matched_a = self.player_management.resolve_players_names(
                team_a, self.available_players_list, self.console
            )
            matched_b = self.player_management.resolve_players_names(
                team_b, self.available_players_list, self.console
            )

            if not matched_a and not matched_b:
                self.console.print("\n[bold red]Analysis aborted:[/bold red] No players were matched on either side.")
                
        except Exception as e:
                self.console.print(f"[red]{e}[/red]")
                return

        self.analyze_trade(matched_a,matched_b)

    def analyze_trade(self, matched_a, matched_b):
        '''To calculate the total Z-value for the teams'''

        if self.df_z_scores is None:
            self.console.print("Error: Z-Scores data not available.", style="bold red")
            return
        
        team_a_players = self.df_z_scores[self.df_z_scores['PLAYER_NAME'].isin(matched_a)]
        team_b_players = self.df_z_scores[self.df_z_scores['PLAYER_NAME'].isin(matched_b)]

        total_z_a = team_a_players['TOTAL_Z_SCORE'].sum()
        total_z_b = team_b_players['TOTAL_Z_SCORE'].sum()

        self.__generate_report(team_a_players, team_b_players, total_z_a, total_z_b)

    def __display_menu(self):
        '''To display the menu for the user'''
        
        title = f"[bold white on blue]  FANTASY BASKETBALL TRADE ANALYZER  [/bold white on blue]"
        subtitle = f"CURRENT SEASON: [yellow]{self.current_season}[/yellow]"
        
        menu_text = (
            f"{subtitle}\n\n"
            "1. View single player stats & Z-scores\n"
            "2. Analyze a trade (Team A vs. Team B)\n"
            "3. Change analysis season\n"
            "4. Exit application"
        )
        
        panel = Panel(
            menu_text,
            title=title,
            border_style="cyan",
            title_align="center"
        )
        self.console.print(panel)
        
    def run(self):
        '''The main excution loop for the user choice'''

        while True:
            self.__display_menu()
            
            try:
                choice = input("Enter your choice (1, 2, 3, or 4): ").strip()
            except Exception:
                self.console.print("Error reading input. Exiting.", style="red")
                break

            if choice == '1':
                self.view_player_stats()
            elif choice == '2':
                self.analyze_trade_flow()
            elif choice == '3':
                self.__change_season()
            elif choice == '4':
                self.console.print("\n[bold green]Thank you for using the Trade Analyzer. See you soon![/bold green]", style="bold")
                break
            else:
                self.console.print("\nInvalid choice. Please enter 1, 2, 3, or 4.", style="red")

if __name__ == '__main__':
    try:
        app = TradeAnalyzerApp()
        app.run()
    except ImportError as e:
        print(f"\nMissing necessary library: {e}")
        print("Please ensure you have run: pip install pandas numpy fuzzywuzzy python-levenshtein nba_api rich")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
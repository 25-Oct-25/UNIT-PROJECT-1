from rich.console import Console
from nba_api.stats.endpoints import leaguedashplayerstats

class DataFetcher:
    '''Handles fetching NBA player stats and initial data preparation.'''

    def __init__(self, season= '2024-25', min_gp=20, categories= []):

        self.season= season
        self.min_gp= min_gp
        self.categories= categories
        self.console= Console()

    def fetch_and_prepare(self):
        '''Fetches player stats from the NBA API and filters the DataFrame.'''

        try:
            data = leaguedashplayerstats.LeagueDashPlayerStats(
                season=self.season,
                per_mode_detailed= 'PerGame'
            )

            df= data.get_data_frames()[0]

        except Exception as e:
            print(f"Error occured while fetching data from NBA API. Check connections: {e}")
            return None
        
        df_filtered = df[df['GP'] >= self.min_gp].copy()


        selected_cols= ['PLAYER_NAME', 'GP', 'MIN'] + self.categories
        df_stats= df_filtered[selected_cols].copy()

        df_stats['FGM'] = df_filtered['FGM']
        df_stats['FGA'] = df_filtered['FGA']
        df_stats['FTM'] = df_filtered['FTM']
        df_stats['FTA'] = df_filtered['FTA']


        self.console.print(f"[bold blue]Data fetched and filtered successfuly. Found [cyan]{len(df_stats)}[/cyan] qualified players.")
        return df_stats
    

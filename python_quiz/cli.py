from .game import run_round
from .leaderboard import rank_session
from .style import print_title, colored, TITLE_CLR, OK_CLR, WARN_CLR, print_winner_banner, apply_color_config
from .storage import save_session, load_all_sessions
from .ai_gen import generate_questions_with_source, generate_questions
from .reporting import make_session_pdf, make_leaderboard_pdf
from .config import load_config, distribution_str, total_questions

from collections import defaultdict


def _print_players(players):
    """
    Print the current in-memory players list (for this upcoming session only).
    """
    print(colored(f"Current players ({len(players)}): {', '.join(players) if players else 'None'}", TITLE_CLR))


def _add_player(players):
    """
    Add a new player to the current session list (does not affect historical data).
    """
    name = input(colored("Enter new player name: ", OK_CLR)).strip()
    if not name:
        print(colored("Name cannot be empty.", WARN_CLR))
        return
    if name in players:
        print(colored("Player already in the current list.", WARN_CLR))
        return
    players.append(name)
    print(colored(f"Added player: {name}", OK_CLR))


def _search_previous_player():
    """
    Search all previous sessions for a given player name and show the most recent record.
    Does NOT modify any data; purely informational. Returns to the main menu after display.
    """
    name = input(colored("Enter player name to search in previous sessions: ", OK_CLR)).strip()
    if not name:
        print(colored("Name cannot be empty.", WARN_CLR))
        return
    sessions = load_all_sessions()
    if not sessions:
        print(colored("No previous sessions found.", WARN_CLR))
        return

    found = []
    for sess in sessions:
        for row in sess.get("results_sorted", []):
            if row.get("name", "").lower() == name.lower():
                found.append((sess.get("timestamp", "?"), row))

    if not found:
        print(colored(f"No record found for '{name}'.", WARN_CLR))
        return

    ts, last = found[-1]
    print(colored(f"\nLast record for {name}:", OK_CLR))
    print(f"  Timestamp: {ts}")
    print(f"  Score: {last.get('score')}%")
    print(f"  Avg time: {last.get('avg_time')}s")
    print(f"  Result: {last.get('label')}\n")


def _build_all_time_stats():
    """
    Aggregate all-time stats across all sessions.
    Returns a sorted list of tuples: (name, avg_score, avg_time, appearances),
    sorted by: avg_score DESC, avg_time ASC, name ASC.
    """
    sessions = load_all_sessions()
    if not sessions:
        return []

    sums = defaultdict(lambda: {"score": 0.0, "time": 0.0, "n": 0})
    for sess in sessions:
        for row in sess.get("results_sorted", []):
            name = row.get("name", "")
            sums[name]["score"] += float(row.get("score", 0.0))
            sums[name]["time"] += float(row.get("avg_time", 0.0))
            sums[name]["n"] += 1

    stats = []
    for name, acc in sums.items():
        n = max(1, acc["n"])
        avg_score = acc["score"] / n
        avg_time = acc["time"] / n
        stats.append((name, avg_score, avg_time, n))

    stats.sort(key=lambda t: (-t[1], t[2], t[0].lower()))
    return stats


def _show_all_time_list_and_maybe_report():
    """
    Print the all-time ranked players table and optionally export a PDF leaderboard.
    Returns to the main menu afterwards.
    """
    stats = _build_all_time_stats()
    if not stats:
        print(colored("No previous sessions found.", WARN_CLR))
        return

    lines = [
        "All-Time Players (Ranked):",
        "---------------------------------------------",
        "Rank | Name           | Avg Score | Avg Time | Games",
        "---------------------------------------------"
    ]
    for i, (name, avg_s, avg_t, n) in enumerate(stats, 1):
        lines.append(f"{i:<4} | {name:<14} | {avg_s:>8.1f}% | {avg_t:.2f}s   | {n}")

    print(colored("\n" + "\n".join(lines) + "\n", TITLE_CLR))

    yn = input(colored("Generate a PDF leaderboard? (yes/no): ", OK_CLR)).strip().lower()
    if yn in ("yes", "y"):
        path = make_leaderboard_pdf(stats)
        print(colored(f"Leaderboard PDF saved to: {path}\n", OK_CLR))


def _crud_submenu(players):
    """
    Show a pre-start CRUD menu to manage current session players.
    Options:
      1) Add Player
      2) Update Player Name
      3) Delete Player
      4) No Change (Continue)
    Loops until the user chooses "No Change".
    """
    while True:
        print(colored("\n--------------------------", TITLE_CLR))
        print(colored("Manage Players:", TITLE_CLR))
        print(colored("--------------------------", TITLE_CLR))
        print("1) Add Player")
        print("2) Update Player Name")
        print("3) Delete Player")
        print("4) No Change (Continue)")
        choice = input(colored("Enter your choice (1-4): ", OK_CLR)).strip()

        if choice == "1":
            name = input(colored("Enter new player name: ", OK_CLR)).strip()
            if not name:
                print(colored("Name cannot be empty.", WARN_CLR))
            elif name in players:
                print(colored("Player already in the current list.", WARN_CLR))
            else:
                players.append(name)
                print(colored(f"Added player: {name}", OK_CLR))
            _print_players(players)

        elif choice == "2":
            old = input(colored("Enter current player name: ", OK_CLR)).strip()
            if old not in players:
                print(colored(f"Not found in current list: {old}", WARN_CLR))
            else:
                new = input(colored("Enter new name: ", OK_CLR)).strip()
                if not new:
                    print(colored("New name cannot be empty.", WARN_CLR))
                elif new in players:
                    print(colored("Name already exists in current list.", WARN_CLR))
                else:
                    idx = players.index(old)
                    players[idx] = new
                    print(colored(f"Updated: {old} -> {new}", OK_CLR))
            _print_players(players)

        elif choice == "3":
            name = input(colored("Enter player name to delete: ", OK_CLR)).strip()
            if name in players:
                players.remove(name)
                print(colored(f"Deleted player: {name}", OK_CLR))
            else:
                print(colored(f"Not found in current list: {name}", WARN_CLR))
            _print_players(players)

        elif choice == "4":
            print(colored("No change. Proceeding to the game...", OK_CLR))
            return  # proceed to game

        else:
            print(colored("Please choose a valid option (1-4).", WARN_CLR))


def _start_game_flow(cfg):
    """
    Orchestrate one full game session:
      - Ask for number of players and names.
      - Offer pre-start CRUD to manage current players.
      - Run the quiz for each player.
      - Show final leaderboard and winner banner.
      - Save JSON/CSV.
      - Ask if the user wants a session PDF.
      - Return to main menu.
    """
    # Apply colors (in case config was updated)
    apply_color_config(cfg.get("colors"))

    # Determine question source and show mode line
    n_easy, n_med, n_hard = int(cfg["num_easy"]), int(cfg["num_medium"]), int(cfg["num_hard"])
    first_qs, src_label = generate_questions_with_source(n_easy, n_med, n_hard)
    mode_line = f"Single-level mode • {total_questions(cfg)} questions per player ({distribution_str(cfg)})"
    print(colored(f"Question source: {src_label}", TITLE_CLR))
    print(colored(mode_line, TITLE_CLR))
    print("=" * 70)

    # Ask for number of players with clear instructions and limit
    max_players = 4
    attempts = 0

    print(colored(f"\nWelcome to the Game Setup!", TITLE_CLR))
    print(colored(f"You can play solo or with friends (1 to {max_players} players).", OK_CLR))
    print(colored("Let's set up your session below ", OK_CLR))

    while True:
        try:
            n = int(input(colored(f"How many players? (1-{max_players}): ", OK_CLR)))
            if 1 <= n <= max_players:
                print(colored(f"Great! {n} player{'s' if n > 1 else ''} will play this round.", OK_CLR))
                break
            else:
                print(colored(f"Please enter a number between 1 and {max_players}.", WARN_CLR))
        except ValueError:
            print(colored("Invalid input. Please enter a number.", WARN_CLR))

        attempts += 1
        if attempts >= 4:
            print(colored("\nToo many invalid attempts. Returning to main menu...", WARN_CLR))
            return # return to the main menu

    players = []
    for i in range(1, n + 1):
        name = input(colored(f"Player {i} name: ", OK_CLR)).strip() or f"Player{i}"
        players.append(name)

    print(colored("\nPlayers entered.", TITLE_CLR))
    _print_players(players)

    # CRUD before starting the first player
    _crud_submenu(players)
    if not players:
        print(colored("No players in the list. Returning to the main menu...", WARN_CLR))
        return


    print(colored(f"\nEach player will get {total_questions(cfg)} questions: {distribution_str(cfg)}.\n", TITLE_CLR))

    # Run the game
    results = []
    for idx, name in enumerate(players, 1):
        print(colored(f"\nNow playing: {name}", TITLE_CLR))
        qs = first_qs if idx == 1 else generate_questions(n_easy, n_med, n_hard)
        score, avg_time, label, message, dev_plan = run_round(name, questions=qs)
        results.append((name, score, avg_time, label, message, dev_plan))
        if idx < len(players):
            print(colored(f"\nCalling next player: {players[idx]}", OK_CLR))

    # Leaderboard
    print(colored("\n==========================", TITLE_CLR))
    print(colored("     FINAL LEADERBOARD    ", TITLE_CLR))
    print(colored("==========================", TITLE_CLR))
    table, winners, is_tie, sorted_rows = rank_session(results)
    print(table)
    print()
    print_winner_banner(winners, is_tie)

    # Persist JSON + CSV 
    json_path, timestamp, csv_path = save_session(
        players,
        sorted_rows,
        meta={"mode": "single-level", "source": src_label},
        save_csv=bool(cfg.get("save_csv", True)),
    )
    print(colored(f"\nResults saved to: {json_path}", OK_CLR))
    if csv_path:
        print(colored(f"CSV appended to: {csv_path}", OK_CLR))

    # Ask for session PDF explicitly
    yn = input(colored("Do you want a PDF report for this session? (yes/no): ", OK_CLR)).strip().lower()
    if yn in ("yes", "y"):
        pdf_path = make_session_pdf(players, sorted_rows, src_label, winners, is_tie, timestamp=timestamp)
        print(colored(f"PDF report saved to: {pdf_path}\n", OK_CLR))

    # Ask for another round
    while True:
        again = input(colored("Start another round? (yes/no): ", OK_CLR)).strip().lower()

        if again in ("yes", "y"):
            print(colored("Returning to main menu...\n", OK_CLR))
            return  # go back to main menu

        elif again in ("no", "n"):
            print(colored("Goodbye!", OK_CLR))
            exit()  # completely exit the program

        else:
            print(colored("Please enter 'yes' or 'no'.", WARN_CLR))



    



def main():
    """
    Entry point.
    Renders the title, then loops on the Main Menu:
      1) Start Game: runs one full session flow, then returns to menu.
      2) Show All Players: prints all-time ranked players and can export a PDF leaderboard.
      3) Player Info: search previous sessions for a given player (most recent record).
      4) Exit: quits the program.
    """
    cfg = load_config()
    apply_color_config(cfg.get("colors"))
    print_title()

    while True:
        print(colored("\n=================================", TITLE_CLR))
        print(colored("        PYTHON CHALLENGE       ", TITLE_CLR))
        print(colored("=================================", TITLE_CLR))
        print("Main Menu:")
        print("------------------")
        print("1) Start Game")
        print("2) Show All Players")
        print("3) Player Info")
        print("4) Exit")
        choice = input(colored("Enter your choice (1-4): ", OK_CLR)).strip()

        if choice == "1":
            _start_game_flow(cfg)

        elif choice == "2":
            _show_all_time_list_and_maybe_report()

        elif choice == "3":
            _search_previous_player()

        elif choice == "4":
            print(colored("Goodbye.", OK_CLR))
            break

        else:
            print(colored("Please choose a valid option (1-4).", WARN_CLR))


if __name__ == "__main__":
    main()

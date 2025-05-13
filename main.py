from datetime import datetime
from pathlib import Path

from rinks import RINK_NAMES

from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog
from prompt_toolkit.completion import FuzzyWordCompleter, FuzzyCompleter, WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory

from game_downloader import download_game
from game_concatenator import concatenate_game

# Sample list of items to search from
rink_names = RINK_NAMES.values()
rink_codes = RINK_NAMES.keys()
teams = ["12U Storm North", "12U Storm Select", "12U Jr Aeros", "...other"]


opponent_history = FileHistory(".opponent_history")


def team_selector():
    selected_team = radiolist_dialog(
        title="Team dialog",
        text="Which team ?",
        values=[(team, team) for team in teams],
    ).run()

    if selected_team == "...other":
        selected_team = prompt("Enter team name: ")
    return selected_team


def download():
    selected_team = team_selector()

    # Load opponent history from FileHistory
    # opponent_history_entries = [entry for entry in opponent_history.load()]

    # Create a FuzzyWordCompleter with the history entries
    # opponent_completer = FuzzyWordCompleter(list(opponent_history.load()))

    # Prompt the user with fuzzy search enabled and history
    # opponent_team = prompt("Opponent Team: ", completer=opponent_completer)

    opponent_team = prompt("Opponent Team: ", auto_suggest=AutoSuggestFromHistory())

    # Create a FuzzyWordCompleter with the list of items
    rink_completer = FuzzyWordCompleter(list(rink_names))

    # Prompt the user with fuzzy search enabled
    rink_name = prompt("Select Rink: ", completer=rink_completer)

    selected_rink_code = [code for code, name in RINK_NAMES.items() if name == rink_name][0]

    start_date_input = prompt("Game Start Date: ", default=datetime.now().date().strftime("%Y-%m-%d"))
    start_date = datetime.strptime(start_date_input, "%Y-%m-%d").date()

    start_time_input = prompt("Game Start Time: ", default=datetime.now().time().strftime("%H:%M"))
    start_time = datetime.strptime(start_time_input, "%H:%M").time()

    game_length = float(prompt("Game Length (in hours): ", default="1.00"))

    use_pano_mode = prompt("Use Pano Mode? (True/False): ", default="False").strip().lower() == "true"

    print("You selected:", selected_team, rink_name, start_date, start_time.strftime("%H:%M"), game_length)

    root_path = (Path(__file__).parent / "video").joinpath(selected_team)

    download_game(
        rink=selected_rink_code,
        start_time=f"{start_date} {start_time.strftime('%H:%M')}",
        length=game_length,
        root_path=root_path,
        game_name=f"{selected_team} vs {opponent_team}",
        download_pano=use_pano_mode,
    )


def concat():
    print("Concatenating the video")
    selected_team = team_selector()

    game_folder = (Path(__file__).parent / "video").joinpath(selected_team)

    # list all subfolders
    subfolders = [f for f in game_folder.glob("*") if f.is_dir()]

    selected_game = radiolist_dialog(
        title="Game",
        text="Which game ?",
        values=[(p, p.name) for p in subfolders],
    ).run()

    print("Selected game:", selected_game)

    trim_at_start = prompt("Trim Start Time: ", default="00:00:00")
    trim_at_end = prompt("Trim End Time: ", default="00:00:00")

    concatenate_game(selected_game, trim_start_time=trim_at_start, trim_end_time=trim_at_end, delete_parts=False)


def main():
    selected_function = radiolist_dialog(
        title="Get Started",
        text="Select an option",
        values=[("download", "Download"), ("concat", "Concatenate")],
    ).run()

    if selected_function == "download":
        print("Selection is download")
        download()
    elif selected_function == "concat":
        print("Selection is concatenate")
        concat()

    print("Exiting", selected_function)


if __name__ == "__main__":
    main()

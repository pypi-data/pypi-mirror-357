from fun_apis.api_clients import *
from fun_apis.config import load_api_key, configure_api_key
from fun_apis.constants import welcome_message, help_message, console, no_api_key_needed
from fun_apis.utils import cli_errors_handler, clear_screen, display_superheroes_table
from prompt_toolkit import prompt, HTML
from prompt_toolkit.completion import WordCompleter

def display_help_message() -> None:
    console.print(f"[green]{help_message}")

def exit_script() -> None:
    console.print("[bright_yellow]Have a good day!")
    exit()

def invalid_option(option : str) -> None:
    if option.strip() == "":
        console.print("[orange_red1]Input cannot be empty, run 'help' to check the available commands.")
    else:
        console.print(f"[orange_red1]{option} is invalid, run 'help' to check the available commands.")

@cli_errors_handler
def prompt_animal(api_key : str) -> None:
    animal_name = prompt(HTML("<ansibrightblue>Which Animal are you looking for?</ansibrightblue> "))
    animal(api_key , animal_name)

# @cli_errors_handler
# def prompt_quote(api_key : str) -> None:
#     quote(api_key)

@cli_errors_handler
def prompt_celebrity(api_key : str) -> None:
    celebrity_name = prompt(HTML("<ansimagenta>Who are you looking for ?</ansimagenta> "))
    celebrity(api_key, celebrity_name)

@cli_errors_handler
def prompt_superhero(api_key : str) -> None:
    superhero_id_or_name = prompt(HTML("<ansimagenta>Which sup are looking for ?</ansimagenta> "))
    superhero(api_key, superhero_id_or_name)

options = {
    "1" : display_help_message,
    "help" : display_help_message,
    "2" : configure_api_key,
    "configure" : configure_api_key,
    "3" : clear_screen,
    "clear" : clear_screen,
    "4" : exit_script,
    "exit" : exit_script,
    # STATIC OPTIONS |^|
    "5" : fact,
    "fact" : fact,
    "6" : prompt_animal,
    "animal" : prompt_animal,
    "7" : quote,
    "quote" : quote,
    "8" : prompt_celebrity,
    "celebrity" : prompt_celebrity,
    "9" : prompt_superhero,
    "superhero" : prompt_superhero,
    "10" : display_superheroes_table,
    "superheroes-table" : display_superheroes_table
}

def launch_interactive(option : str) -> None:
    choice = options.get(option.strip().lower(), None)
    if not choice:
        invalid_option(option)
    elif option.lower().strip() in no_api_key_needed:
        choice()
    else:
        if option.lower().strip() in list(options.keys())[8:16]:
            api_key = load_api_key(which_api_key="ninjas_api_key")
            if choice is fact:
                choice(api_key)
            else:
                choice(api_key=api_key) 
        elif option.lower().strip() in ["9","superhero"]:
            api_key = load_api_key(which_api_key="superhero_api_key")
            choice(api_key)

@cli_errors_handler
def interactive_mode() -> None:
    console.print(f"[green bold]{welcome_message}[/green bold]")
    while True:
        cli_prompt_completer = WordCompleter(list(options.keys()),ignore_case=True)
        option = prompt(HTML("<ansibrightcyan>What would you like to do? Select an option by its <u>number</u> or <u>name</u>: </ansibrightcyan>"), completer=cli_prompt_completer) 
        launch_interactive(option)

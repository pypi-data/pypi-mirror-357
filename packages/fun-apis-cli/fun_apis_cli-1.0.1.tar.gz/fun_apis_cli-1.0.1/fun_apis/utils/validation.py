import json
from typing import Dict, Callable, Any
from json import JSONDecodeError
from functools import wraps
from fun_apis.constants import console, SUPERHEROES_JSON_FILE_PATH

def cli_errors_handler(func: Callable[..., Any]) -> Any:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        try:
            return func(*args, **kwargs)
        except (EOFError, KeyboardInterrupt):
            print("Exiting...")
            exit("Have a good day!")
    return wrapper

def verify_superhero (superhero_id_or_name : str):
    try:
        with open(SUPERHEROES_JSON_FILE_PATH, "r") as superheroes_json_file:
            reference : Dict = json.load(superheroes_json_file)
        try:
            sup_id = int(superhero_id_or_name)
            if  1 <= sup_id <= 731:
                return True,sup_id
            else:
                return False,None 
        except ValueError:
            sup_id = [int(ids) for ids in reference if reference[ids]==superhero_id_or_name.title()]
            if not sup_id:
                return False,None
            elif len(sup_id) == 1:
                return True,sup_id[0]      
            return True,sup_id
    except JSONDecodeError as err:
        console.print(f"[red]Broken or invalid JSON file:\"{SUPERHEROES_JSON_FILE_PATH}\"\n{err}")
        return None, False
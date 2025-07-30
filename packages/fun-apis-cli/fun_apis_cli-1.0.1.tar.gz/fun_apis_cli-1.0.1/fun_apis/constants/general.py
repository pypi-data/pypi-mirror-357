import os
from rich.console import Console
from platformdirs import user_config_dir

console = Console()

CONFIG_FILE_PATH = os.path.join(
    user_config_dir(appname="Fun_APIs_CLI", ensure_exists=True) ,'config.json'
)
SUPERHEROES_JSON_FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    'data', 
    'heroes_ids_names.json'
)

valid_apis_keys = ["ninjas_api_key", "superhero_api_key"]
valid_options = valid_apis_keys.copy()
valid_options.append("all")
valid_options_string = f"{"; ".join(valid_options)}"

categories_noun = {
    "alone": "loneliness",
    "amazing": "amazement",
    "best": "excellence",
    "cool": "coolness",
    "famous": "fame",
    "funny": "humor",
    "good": "goodness",
    "great": "greatness",
    "inspirational": "inspiration",
    "legal": "legality",
    "medical": "medicine",
}

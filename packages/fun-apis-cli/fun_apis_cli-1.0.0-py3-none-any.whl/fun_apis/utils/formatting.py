from typing import List, Dict, Union
import json
from fun_apis.constants.general import console, SUPERHEROES_JSON_FILE_PATH
import plotext as plt
from rich.table import Table 

def create_powerstats_barplot(combat : int, intelligence: int, power: int, speed: int, strength: int, sup_name : str) -> None:
    powerstats = ["Combat", "Intelligence", "Power", "Speed", "Strength"]
    powerstats_percentages = [combat, intelligence, power, speed, strength]
    plt.simple_bar(powerstats, powerstats_percentages, width = 50,color="green", title = plt.colorize(f'{sup_name} Powerstats Chart', "magenta"))
    plt.show()

def generate_superheroes_table() -> Table:
    superheroes_ids_names_table = Table(title="[cyan]SuperHeroes IDs and Names", box=None, pad_edge=False)
    for i in range(4):
        superheroes_ids_names_table.add_column()

    sub_tables = []
    for i in range(4):
        table = Table()
        table.add_column("[green]Names", style="red", no_wrap=True)
        table.add_column("[green]IDs", style="blue", no_wrap=True)
        sub_tables.append(table)

    with open(SUPERHEROES_JSON_FILE_PATH, 'r') as ref_file:
        heroes_json : Dict = json.load(ref_file)

    heroes_json_list : List = list(heroes_json.items())
    part_size = len(heroes_json_list) // 4

    parts = [heroes_json_list[:part_size], heroes_json_list[part_size:part_size*2], heroes_json_list[part_size*2:part_size*3],heroes_json_list[part_size*3:]] 

    for row_data in zip(*parts):
        for i, (hero_id, hero_name) in enumerate(row_data):
            sub_tables[i].add_row(hero_name, hero_id)

    superheroes_ids_names_table.add_row(*sub_tables)

    return superheroes_ids_names_table

def display_superheroes_table() -> None:
    console.print(generate_superheroes_table())

def meters_to_freedom_units(meters : Union[int, float]) -> str:
    total_feet = meters * 3.28084  
    feet = int(total_feet)         
    inches = (total_feet - feet) * 12  
    return f"{feet}'{round(inches)}\""
from typing import Union, List, Optional
import requests
from fun_apis.constants import console, categories_noun, Quote
from fun_apis.utils import requests_error_handler

@requests_error_handler
def fetch_quote(api_key : str ) -> Optional[List[Quote]]:
    api_url = 'https://api.api-ninjas.com/v1/quotes'
    response = requests.get(api_url, headers={'X-Api-Key': api_key})
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} {response.text}")

def display_quote(quote : Union[List[Quote], int]) -> None:
    if not quote:
        return 
    quote = quote[0]
    topic = categories_noun.get(quote['category'],quote['category']).capitalize()
    console.print(f'''
    [green bold]"{quote['quote']}"[/green bold]
    said by [cyan i]{quote['author']}[/cyan i] about [red]{topic}[/red]
    ''')

def quote(api_key : str) -> None:
    with console.status("Fetching a quote...", spinner="earth"):
        display_quote(quote=fetch_quote(api_key))
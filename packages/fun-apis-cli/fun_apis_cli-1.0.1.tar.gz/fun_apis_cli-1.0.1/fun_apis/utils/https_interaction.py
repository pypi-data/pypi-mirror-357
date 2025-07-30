from functools import wraps
from typing import Callable, Any, Optional
import json
from fun_apis.constants.general import console
from fun_apis.constants.types import SuperHeroInfo
from requests import Response

def requests_error_handler(func: Callable[..., Any]) -> Any:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        try:
            return func(*args, **kwargs)
        except ConnectionError:
            console.print("[red]No internet connection! Please check your network and try again.[/red]")
            return None
        # except Exception as error:
        #     console.print(f"[red]An error has occured:[/red]\n{error}")
        #     return None
    return wrapper

def response_verifier(response: Response) -> Optional[SuperHeroInfo]:
    if response.status_code == 200:
        json_start = response.text.find("{")
        if json_start == -1:
            raise Exception("Invalid response format: No JSON found.")
        raw_json_text = response.text[json_start:]

        json_response: Optional[SuperHeroInfo] = json.loads(raw_json_text)
        if json_response.get('response') == 'error' and json_response.get('error') == 'access denied':
            raise Exception("Access denied. Please check your API key.[/red]")
        return json_response
    else:
        raise Exception(f"Failed to fetch superhero info. HTTPS Status: {response.status_code}")
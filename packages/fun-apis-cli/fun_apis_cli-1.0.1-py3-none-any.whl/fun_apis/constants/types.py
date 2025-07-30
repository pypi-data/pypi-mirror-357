from typing import Union, Optional, List, Dict, TypedDict

class Fact(TypedDict):
    """
    Represents a single historical or interesting fact.

    Attributes:
        fact (str): A detailed description or statement about a particular piece of information.
    """
    fact: str

class Quote(TypedDict):
    """
    Represents a quotation with its attribution and category.

    Attributes:
        quote (str): The text of the quotation.
        author (str): The person who originally said or wrote the quote.
        category (str): A classification or theme of the quote.
    """
    quote : str
    author : str
    category : str

class AnimalsInfo(TypedDict):
    """
    Provides comprehensive information about an animal species.

    Attributes:
        name (str): The common name of the animal.
        taxonomy (Dict[str, str]): Taxonomic classification of the animal.
        locations (List[str]): Geographic regions where the animal is found.
        characteristics (Dict[str, str]): Detailed information about the animal's traits and behavior.
    """
    name : str
    taxonomy : Dict[str, str]
    locations : List[str]
    characteristics : Dict[str, str]

class CelebrityInfo(TypedDict):
    """
    Contains detailed information about a celebrity.

    Attributes:
        name (str): Full name of the celebrity.
        net_worth (Optional[int]): Estimated net worth in a standard currency.
        gender (Optional[str]): Gender of the celebrity.
        nationality (Optional[str]): Country of origin or citizenship.
        occupation (Optional[List[str]]): Profession(s) of the celebrity.
        height (Optional[float]): Height of the celebrity.
        birthday (Optional[str]): Date of birth.
    """
    name : str
    net_worth : Optional[int]
    gender : Optional[str]
    nationality : Optional[str]
    occupation : Optional[List[str]]
    height : Optional[float]
    birthday : Optional[str]

class SuperHeroInfo(TypedDict):
    """
    Represents comprehensive information about a superhero.

    Attributes:
        appearence (Dict[str, Union[str, List[str]]]): Physical characteristics of the superhero.
        biography (Dict[str, Union[str, List[str]]]): Background and origin story details.
        connections (Dict[str,str]): Affiliations and relationships.
        id (str): Unique identifier for the superhero.
        image (Dict[str,str]): Image-related information.
        name (str): Superhero's name.
        powerstats (Dict[str,str]): Numerical ratings of different superhero abilities.
        response (str): API response status.
        work (Dict[str,str]): Professional or heroic occupation details.
    """
    appearence : Dict[str, Union[str, List[str]]]
    biography : Dict[str, Union[str, List[str]]]
    connections : Dict[str,str]
    id : str
    image : Dict[str,str]
    name : str
    powerstats : Dict[str,str]
    response: str
    work : Dict[str,str]
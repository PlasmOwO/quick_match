import pandas
import requests
from dotenv import load_dotenv
import os

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DDRAGON_VERSION = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]

def get_puuid(player_name : str, player_tag : str) -> str :
    """Fonction to have the PUUID of a player

    Args:
        player_name (str): Name of the player
        player_tag (str): Tag (after the #) of the player

    Returns:
        str: Return the puuid of the player (depends of your current API KEY)
    """
    response = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{player_name}/{player_tag}?api_key={RIOT_API_KEY}")
    player_info = response.json()
    return player_info["puuid"]


def champion_id_to_name(champion_id : int) -> tuple :
    """Transform id of a champion to the real name. Using ddragon data.

    Args:
        champion_id (int): Id of a champion

    Returns:
        tuple: The name of the champion and the id (name with regex)
        Exemple : Kai'sa ; Kaisa
    """
    response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{DDRAGON_VERSION}/data/en_US/champion.json")
    champions_data = response.json()["data"]
    champion_name = next((mapping["name"] for mapping in champions_data.values() if int(mapping["key"]) == champion_id), None)
    champion_id = next((mapping["id"] for mapping in champions_data.values() if int(mapping["key"]) == champion_id), None)
    return (champion_name, champion_id)


def champion_image_from_name(champion_id : str) -> str :
    """From champion id/name (with the regex), get the image from datadragon.

    Args:
        champion_id (str): The name of the champion, without blank space or quote (Kaisa, Velkoz etc...)

    Returns:
        str: The PNG image, src link of the champion
    """
    return f"https://ddragon.leagueoflegends.com/cdn/{DDRAGON_VERSION}/img/champion/{champion_id}.png"

def list_player_matches(puuid : str, nb_matches : int) -> list :
    """List match ID of a player puuid. Using Riot api.

    Args:
        puuid (str): The Puuid of the player
        nb_matches (int): Number of matches to get

    Returns:
        list: Match IDs
    """
    response = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=tourney&start=0&count={nb_matches}&api_key={RIOT_API_KEY}")
    match_list = response.json()
    return match_list



def request_match_data(match_id : str) -> dict :
    """Request game data using Riot API

    Args:
        match_id (str): Id of the match

    Returns:
        dict: Data of the match
    """
    response = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}")
    return response.json()


def get_match_champions(game_data : dict , player_puuid : str) -> dict :
    """Get champions, bans, side and win of a specific match for a player.
    Example :
        {
        'blue_champions': {
            "id": ['Renekton', 'XinZhao', 'Galio', 'Velkoz', 'Soraka'],
            "name" :['Renekton', 'XinZhao', 'Galio', 'Velkoz', 'Soraka']
        }
        'blue_bans': {
            "id": ['Renekton', 'XinZhao', 'Galio', 'Velkoz', 'Soraka'],
            "name" :['Renekton', 'XinZhao', 'Galio', 'Velkoz', 'Soraka']
        },
        'blue_names': ['SCL Kallesyn', 'Bartholomew Kuma', 'Orcybe', 'SCL Filou', 'SCL Likii'],
        'red_champions': {
            "id": ['Renekton', 'XinZhao', 'Galio', 'Velkoz', 'Soraka'],
            "name" :['Renekton', 'XinZhao', 'Galio', 'Velkoz', 'Soraka']
        },
        'red_bans': {
            "id": ['Renekton', 'XinZhao', 'Galio', 'Velkoz', 'Soraka'],
            "name" :['Renekton', 'XinZhao', 'Galio', 'Velkoz', 'Soraka']
        },
        'red_names': ['Killa', 'bvig', 'namelesss', 'Reze', 'Dsoul'], 
        'player_team': 'blue', 
        'win': True
        }

    Args:
        game_data (dict): Data of the match
        player_puuid (str): Player puuid. Usage for finding the team of the player.

    Returns:
        dict: Quick summary about the match.
    """
    match_dict = game_data
    team = "red"
    if match_dict["metadata"]["participants"].index(player_puuid) <= 4 :
        team = "blue"
        
    if team == "red" :
        win = match_dict["info"]["teams"][1]["win"]
    else :
        win = match_dict["info"]["teams"][0]["win"]
    
    champions = {
        "blue_champions" : {
            "id" :[champion_id_to_name(player["championId"])[1] for player in match_dict["info"]["participants"][:5]],
            "name" : [champion_id_to_name(player["championId"])[0] for player in match_dict["info"]["participants"][:5]]
        },
        "blue_bans" : {
            "id" : [champion_id_to_name(ban["championId"])[1] for ban in match_dict["info"]["teams"][0]["bans"]],
            "name" :[champion_id_to_name(ban["championId"])[0] for ban in match_dict["info"]["teams"][0]["bans"]]
        },
        "blue_names" : [player["riotIdGameName"] for player in match_dict["info"]["participants"][:5]],
        "red_champions" : {
            "id" :[champion_id_to_name(player["championId"])[1] for player in match_dict["info"]["participants"][5:10]],
            "name" : [champion_id_to_name(player["championId"])[0] for player in match_dict["info"]["participants"][5:10]]
        },
        "red_bans" : {
            "id" : [champion_id_to_name(ban["championId"])[1] for ban in match_dict["info"]["teams"][1]["bans"]],
            "name" :[champion_id_to_name(ban["championId"])[0] for ban in match_dict["info"]["teams"][1]["bans"]]
        },
        "red_names" : [player["riotIdGameName"] for player in match_dict["info"]["participants"][5:10]],
        "player_team": team,
        "win" : win   
    }
    return champions


def compute_gold_percent_by_player(game_data : dict) -> dict :
    """Retrieve gold percent per player (Player gold / team gold)

    Args:
        game_data (dict): The data of a match

    Returns:
        dict: Dict containing 2 lists (blue and red gold ratio)
    """

    total_gold_blue = sum(participant["goldEarned"] for participant in game_data["info"]["participants"][0:5])
    total_gold_red = sum(participant["goldEarned"] for participant in game_data["info"]["participants"][5:10])
    blue_gold_percentages = [None] *5
    red_gold_percentages = [None] *5
    for idx, participant in enumerate(game_data["info"]["participants"][0:5]):
        blue_gold_percentages[idx] = participant["goldEarned"] / total_gold_blue * 100

    for idx, participant in enumerate(game_data["info"]["participants"][5:10]):
        red_gold_percentages[idx] = participant["goldEarned"] / total_gold_red * 100

    return {
        "blue_gold_percentages": blue_gold_percentages,
        "red_gold_percentages": red_gold_percentages
        }

def compute_dmg_ratio_by_player(game_data : dict) -> dict :
    """Retrieve damage percent per player (Player damage / team damage)

    Args:
        game_data (dict): The data of a match

    Returns:
        dict: Dict containing 2 lists (blue and red damage ratio)
    """

    total_dmg_blue = sum(participant["totalDamageDealtToChampions"] for participant in game_data["info"]["participants"][0:5])
    total_dmg_red = sum(participant["totalDamageDealtToChampions"] for participant in game_data["info"]["participants"][5:10])
    blue_dmg_percentages = [None] *5
    red_dmg_percentages = [None] *5
    for idx, participant in enumerate(game_data["info"]["participants"][0:5]):
        blue_dmg_percentages[idx] = participant["totalDamageDealtToChampions"] / total_dmg_blue * 100

    for idx, participant in enumerate(game_data["info"]["participants"][5:10]):
        red_dmg_percentages[idx] = participant["totalDamageDealtToChampions"] / total_dmg_red * 100

    return {
        "blue_dmg_percentages": blue_dmg_percentages,
        "red_dmg_percentages": red_dmg_percentages
        }

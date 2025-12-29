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


def champion_id_to_name(champion_id : int) -> str :
    """Transform id of a champion to the real name. Using ddragon data.

    Args:
        champion_id (int): Id of a champion

    Returns:
        str: The name of the champion
    """
    response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{DDRAGON_VERSION}/data/en_US/champion.json")
    champions_data = response.json()["data"]
    champion_name = next((mapping["name"] for mapping in champions_data.values() if int(mapping["key"]) == champion_id), None)
    return champion_name

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

def get_match_champions(match_id : str, player_puuid : str) -> dict :
    """Get champions, bans, side and win of a specific match for a player.
    Example :
        {'blue_champions': ['Renekton', 'XinZhao', 'Galio', 'Velkoz', 'Soraka'], 'blue_bans': ['Malphite', 'Sion', 'Qiyana', 'Rakan', 'Alistar'], 'blue_names': ['SCL Kallesyn', 'Bartholomew Kuma', 'Orcybe', 'SCL Filou', 'SCL Likii'], 'red_champions': ['Ahri', 'Gragas', 'Vi', 'Jinx', 'Blitzcrank'], 'red_bans': ['Miss Fortune', 'Mel', 'Orianna', 'Ashe', 'Xayah'], 'red_names': ['Killa', 'bvig', 'namelesss', 'Reze', 'Dsoul'], 'player_team': 'blue', 'win': True}

    Args:
        match_id (str): Id of the match
        player_puuid (str): Player puuid. Usage for finding the team of the player.

    Returns:
        dict: Quick summary about the match.
    """
    response = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}")
    match_dict = response.json()
    team = "red"
    if match_dict["metadata"]["participants"].index(player_puuid) <= 4 :
        team = "blue"
        
    if team == "red" :
        win = match_dict["info"]["teams"][1]["win"]
    else :
        win = match_dict["info"]["teams"][0]["win"]


    champions = {
        "blue_champions" : [player["championName"] for player in match_dict["info"]["participants"][:5]],
        "blue_bans" : [champion_id_to_name(ban["championId"]) for ban in match_dict["info"]["teams"][0]["bans"]],
        "blue_names" : [player["riotIdGameName"] for player in match_dict["info"]["participants"][:5]],
        
        "red_champions" : [player["championName"] for player in match_dict["info"]["participants"][5:10]],
        "red_bans" : [champion_id_to_name(ban["championId"]) for ban in match_dict["info"]["teams"][1]["bans"]],
        "red_names" : [player["riotIdGameName"] for player in match_dict["info"]["participants"][5:10]],
        
        "player_team": team,
        "win" : win
    }
    return champions


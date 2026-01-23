from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from quick_match.functions import api_functions
import requests
from importlib.resources import open_text
import datetime

# -------------------- CSS --------------------

with open_text("quick_match.webapp", "style.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>",unsafe_allow_html=True)


# -------------------- UI FUNCTIONS --------------------

def get_name_class(player_name: str, searched_player: str, default_class: str) -> str:
    if player_name.lower() == searched_player.lower():
        return "name-green"
    return default_class
    
def player_left(name, champion_name, champion_id, searched_player):
    src = api_functions.champion_image_from_name(champion_id)
    name_class = get_name_class(name, searched_player, "name-blue")

    st.markdown(f"""
    <div class="player-row">
        <img class="icon" src={src}>
        <div class="player-text">
            <div class="{name_class}">{name}</div>
            <div class="subtext">{champion_name}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def player_right(name,champion_name, champion_id, searched_player):
    src = api_functions.champion_image_from_name(champion_id)
    name_class = get_name_class(name, searched_player, "name-red")

    st.markdown(f"""
    <div class="player-row right">
        <div class="player-text">
            <div class="{name_class}">{name}</div>
            <div class="subtext">{champion_name}</div>
        </div>
        <img class="icon right" src={src}>
    </div>
    """, unsafe_allow_html=True)
    
    
def bans_left(data):
    bans = data["blue_bans"]["id"]
    st.markdown(f"""
    <div class="bans-row">
        <div class="ban-group">
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[0])}></div>
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[1])}></div>
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[2])}></div>
        </div>
        <div class="ban-group split">
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[3])}></div>
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[4])}></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    
def bans_right(data):
    bans = data["red_bans"]["id"]
    st.markdown(f"""
    <div class="bans-row right">
        <div class="ban-group split">
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[4])}></div>
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[3])}></div>
        </div>
        <div class="ban-group">
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[2])}></div>
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[1])}></div>
            <div class="ban-circle"><img src={api_functions.champion_image_from_name(bans[0])}></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def result_ui(win : bool):
    if win :
        return "Victory", "victory"
    else :
        return "Defeat", "defeat"


# -------------------- LAYOUT --------------------

st.title("Quick Match",text_alignment="center")
st.subheader("Outil pour récupérer la liste des parties compétitives d'un joueur. Très utile pour la préparation de draft.", divider="blue",text_alignment="center")

today = datetime.datetime.now()

with st.form("quick_match_form"):
    summoner_name = st.text_input(label="Summoner name",placeholder="Summoner name")
    summoner_tag = st.text_input(label="Tag",placeholder="Tag")
    date_filter = st.date_input("Date range",
        (datetime.datetime.now(), datetime.datetime.now()),
        format="DD/MM/YYYY",
    )
    game_nb_get = st.number_input("Number of games",min_value=1,max_value=100,value=20,step=1)
    submit = st.form_submit_button('Search')
    
if submit :
    puuid_player = api_functions.get_puuid(summoner_name,summoner_tag)
    list_matches = api_functions.list_player_matches(puuid=puuid_player,nb_matches= game_nb_get)
    
    for match_id in list_matches :

        
        match_data = api_functions.request_match_data(match_id=match_id)
        match_summary = api_functions.get_match_champions(game_data=match_data, player_puuid=puuid_player)
        gold_ratios = api_functions.compute_gold_percent_by_player(match_data)
        dmg_ratios = api_functions.compute_dmg_ratio_by_player(match_data)
        match_result = result_ui(match_summary["win"])

        st.markdown(f"<div class='game-block'>", unsafe_allow_html=True)
        st.markdown(f"""<div class="game-result {match_result[1]}">{match_result[0]}</div>""", unsafe_allow_html=True)
        left_col, right_col = st.columns(2)
        
        with left_col:
            for name, champ_name, champ_id in zip(
                match_summary["blue_names"],
                match_summary["blue_champions"]["name"],
                match_summary["blue_champions"]["id"]
            ):
                player_left(name=name,champion_name = champ_name, champion_id = champ_id, searched_player=summoner_name)
            bans_left(match_summary)
                
        with right_col:
            for name, champ_name, champ_id in zip(
                match_summary["red_names"],
                match_summary["red_champions"]["name"],
                match_summary["red_champions"]["id"]
            ):
                player_right(name=name,champion_name = champ_name, champion_id = champ_id, searched_player=summoner_name)
            bans_right(match_summary)
        st.markdown("</div>", unsafe_allow_html=True)  
        st.markdown("<div class='game-separator'></div>", unsafe_allow_html=True)


# -------------

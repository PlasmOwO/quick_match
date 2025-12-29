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



@st.cache_data(show_spinner=False)
def get_champion_icon(champion: str) -> str:
    if champion == None :
        return ""
    champion = champion.lower()

    urls = [
        f"https://raw.communitydragon.org/latest/game/assets/characters/{champion}/hud/{champion}_circle_0.png",
        f"https://raw.communitydragon.org/latest/game/assets/characters/{champion}/hud/{champion}_circle.png",
        f"https://raw.communitydragon.org/latest/game/assets/characters/{champion}/hud/{champion}_circle_0.{champion}.png",
        f"https://raw.communitydragon.org/latest/game/assets/characters/{champion}/hud/{champion}_circle_0.domina.png",
        f"https://raw.communitydragon.org/latest/game/assets/characters/{champion}/hud/{champion}_circle_1.png",
    ]

    for url in urls:
        try:
            r = requests.head(url, timeout=1)
            if r.status_code == 200:
                return url
        except requests.RequestException:
            pass

    # fallback ultime (icône par défaut ou placeholder)
    return champion

def get_name_class(player_name: str, searched_player: str, default_class: str) -> str:
    if player_name.lower() == searched_player.lower():
        return "name-green"
    return default_class
    
def player_left(name, champion, searched_player):
    src = get_champion_icon(champion)
    name_class = get_name_class(name, searched_player, "name-blue")

    st.markdown(f"""
    <div class="player-row">
        <img class="icon" src={src}>
        <div class="player-text">
            <div class="{name_class}">{name}</div>
            <div class="subtext">{champion}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def player_right(name,champion, searched_player):
    src = get_champion_icon(champion)
    name_class = get_name_class(name, searched_player, "name-red")

    st.markdown(f"""
    <div class="player-row right">
        <div class="player-text">
            <div class="{name_class}">{name}</div>
            <div class="subtext">{champion}</div>
        </div>
        <img class="icon right" src={src}>
    </div>
    """, unsafe_allow_html=True)
    
    
def bans_left(data):
    bans = data["blue_bans"]
    st.markdown(f"""
    <div class="bans-row">
        <div class="ban-group">
            <div class="ban-circle"><img src={get_champion_icon(bans[0])}></div>
            <div class="ban-circle"><img src={get_champion_icon(bans[1])}></div>
            <div class="ban-circle"><img src={get_champion_icon(bans[2])}></div>
        </div>
        <div class="ban-group split">
            <div class="ban-circle"><img src={get_champion_icon(bans[3])}></div>
            <div class="ban-circle"><img src={get_champion_icon(bans[4])}></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    
def bans_right(data):
    bans = data["red_bans"]
    st.markdown(f"""
    <div class="bans-row right">
        <div class="ban-group split">
            <div class="ban-circle"><img src={get_champion_icon(bans[4])}></div>
            <div class="ban-circle"><img src={get_champion_icon(bans[3])}></div>
        </div>
        <div class="ban-group">
            <div class="ban-circle"><img src={get_champion_icon(bans[2])}></div>
            <div class="ban-circle"><img src={get_champion_icon(bans[1])}></div>
            <div class="ban-circle"><img src={get_champion_icon(bans[0])}></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


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
        match_summary = api_functions.get_match_champions(match_id=match_id, player_puuid=puuid_player)
        st.markdown(f"<div class='game-block'>", unsafe_allow_html=True)
        left_col, right_col = st.columns(2)
        
        with left_col:
            for player in range(5) :
                player_left(f"{match_summary["blue_names"][player]}",champion=match_summary["blue_champions"][player], searched_player=summoner_name)
            bans_left(match_summary)
                
        with right_col:
            for player in range(5) :
                player_right(f"{match_summary["red_names"][player]}", champion=match_summary["red_champions"][player],searched_player=summoner_name)
            bans_right(match_summary)
        st.markdown("</div>", unsafe_allow_html=True)  
        st.markdown("<div class='game-separator'></div>", unsafe_allow_html=True)

# -------------

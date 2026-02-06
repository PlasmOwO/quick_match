from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from quick_match.api import api_functions
from dotenv import load_dotenv
from typing import Optional
import os
load_dotenv()

app = FastAPI()
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchDetailsRequest(BaseModel):
    game_data: dict

@app.get("/puuid")
def get_puuid(player_name : str, player_tag : str) : 
    return api_functions.get_puuid(player_name, player_tag)


@app.get("/champion_id_to_name/{champion_id}")
def get_champion_name(champion_id : int) :
    return api_functions.champion_id_to_name(champion_id)

@app.get("/champion_image/")
def get_champion_image(champion_name_id : str) :
    return api_functions.champion_image_from_name(champion_name_id)

@app.get("/champion_image/{champion_nameid}")
def get_champion_image_from_name(champion_id : str):
    return api_functions.champion_image_from_name(champion_id)

@app.get("/list_player_matches/")
def get_list_player_matches(puuid : str, nb_matches : int, start_timestamp : Optional[int] = None, end_timestamp : Optional[int] = None) :
    return api_functions.list_player_matches(puuid, nb_matches, start_timestamp, end_timestamp)

@app.get("/match_data/{match_id}")
def get_match_data(match_id : str) :
    return api_functions.request_match_data(match_id)


#baisse de perfo ici
@app.post("/match_details/")
def get_match_details(request: MatchDetailsRequest, player_puuid: str):
    return api_functions.get_match_champions(request.game_data, player_puuid)

@app.post("/gold_percent_player/")
def get_gold_percent_player(request: MatchDetailsRequest):
    return api_functions.compute_gold_percent_by_player(request.game_data)

@app.post("/dmg_percent_player/")
def get_dmg_percent_player(request: MatchDetailsRequest):
    return api_functions.compute_dmg_ratio_by_player(request.game_data)
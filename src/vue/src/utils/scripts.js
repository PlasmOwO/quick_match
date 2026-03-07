// utils.js

import axios from "axios";

// const RIOT_API_KEY = import.meta.env.VITE_RIOT_API_KEY;
let DDRAGON_VERSION = null;

// Initialise la version DDragon (async)
export async function initDDragonVersion() {
  const res = await axios.get("https://ddragon.leagueoflegends.com/api/versions.json");
  DDRAGON_VERSION = res.data[0];
  return DDRAGON_VERSION
}

// --------------------

// Get PUUID
export async function getPuuid(playerName, playerTag) {
  const res = await fetch(`/.netlify/functions/riot-puuid?player_name=${playerName}&player_tag=${playerTag}`);
  console.log(res);
  const data = await res.json();
  return data.puuid;
}

// --------------------

// Champion id -> name + id
export async function championIdToName(championId) {
  if (!DDRAGON_VERSION) await initDDragonVersion();
  const res = await axios.get(
    `https://ddragon.leagueoflegends.com/cdn/${DDRAGON_VERSION}/data/en_US/champion.json`
  );
  const championsData = res.data.data;

  let championName = null;
  let championKey = null;

  for (const mapping of Object.values(championsData)) {
    if (parseInt(mapping.key) === championId) {
      championName = mapping.name;
      championKey = mapping.id;
      break;
    }
  }

  return [championName, championKey];
}

// --------------------

// Champion image from id
export async function championImageFromName(championId) {
  if (!DDRAGON_VERSION) await initDDragonVersion();
  return `https://ddragon.leagueoflegends.com/cdn/${DDRAGON_VERSION}/img/champion/${championId}.png`;
}

// --------------------

// List player matches
export async function listPlayerMatches(puuid, nbMatches, startTimestamp=null, endTimestamp=null) {
  const params = new URLSearchParams({ puuid, nb_matches: nbMatches });
  if (startTimestamp) params.append("start_timestamp", startTimestamp);
  if (endTimestamp) params.append("end_timestamp", endTimestamp);

  const res = await fetch(`/.netlify/functions/riot-matches?${params.toString()}`);
  console.log(res);
  const json_data = await res.json();
  return json_data; 
}

// --------------------

// Request match data
export async function requestMatchData(matchId) {
  const res = await fetch(`/.netlify/functions/riot-match-data?match_id=${matchId}`);
  console.log(res);
  const json_data = await res.json();
  return json_data;
}

// --------------------

// Get match champions summary
export async function getMatchChampions(gameData, playerPuuid) {
  // Determine team
  const idx = gameData.metadata.participants.indexOf(playerPuuid);
  const team = idx <= 4 ? "blue" : "red";
  const win = team === "blue"
    ? gameData.info.teams[0].win
    : gameData.info.teams[1].win;

  const blueChampions = {
    id: [],
    name: [],
  };
  const redChampions = {
    id: [],
    name: [],
  };
  const blueBans = { id: [], name: [] };
  const redBans = { id: [], name: [] };
  const blueNames = [];
  const redNames = [];

  // Blue champions and names
  for (let i = 0; i < 5; i++) {
    const player = gameData.info.participants[i];
    const [name, id] = await championIdToName(player.championId);
    blueChampions.id.push(id);
    blueChampions.name.push(name);
    blueNames.push(player.riotIdGameName);
  }

  // Red champions and names
  for (let i = 5; i < 10; i++) {
    const player = gameData.info.participants[i];
    const [name, id] = await championIdToName(player.championId);
    redChampions.id.push(id);
    redChampions.name.push(name);
    redNames.push(player.riotIdGameName);
  }

  // Blue bans
  for (const ban of gameData.info.teams[0].bans) {
    const [name, id] = await championIdToName(ban.championId);
    blueBans.id.push(id);
    blueBans.name.push(name);
  }

  // Red bans
  for (const ban of gameData.info.teams[1].bans) {
    const [name, id] = await championIdToName(ban.championId);
    redBans.id.push(id);
    redBans.name.push(name);
  }

  return {
    blue_champions: blueChampions,
    red_champions: redChampions,
    blue_bans: blueBans,
    red_bans: redBans,
    blue_names: blueNames,
    red_names: redNames,
    player_team: team,
    win: win
  };
}

// --------------------

// Compute gold percent by player
export function computeGoldPercentByPlayer(gameData) {
  const totalGoldBlue = gameData.info.participants.slice(0, 5)
    .reduce((acc, p) => acc + p.goldEarned, 0);
  const totalGoldRed = gameData.info.participants.slice(5, 10)
    .reduce((acc, p) => acc + p.goldEarned, 0);

  const blueGoldPercentages = gameData.info.participants.slice(0, 5)
    .map(p => (p.goldEarned / totalGoldBlue) * 100);
  const redGoldPercentages = gameData.info.participants.slice(5, 10)
    .map(p => (p.goldEarned / totalGoldRed) * 100);

  return { blue_gold_percentages: blueGoldPercentages, red_gold_percentages: redGoldPercentages };
}

// --------------------

// Compute damage percent by player
export function computeDmgRatioByPlayer(gameData) {
  const totalDmgBlue = gameData.info.participants.slice(0, 5)
    .reduce((acc, p) => acc + p.totalDamageDealtToChampions, 0);
  const totalDmgRed = gameData.info.participants.slice(5, 10)
    .reduce((acc, p) => acc + p.totalDamageDealtToChampions, 0);

  const blueDmgPercentages = gameData.info.participants.slice(0, 5)
    .map(p => (p.totalDamageDealtToChampions / totalDmgBlue) * 100);
  const redDmgPercentages = gameData.info.participants.slice(5, 10)
    .map(p => (p.totalDamageDealtToChampions / totalDmgRed) * 100);

  return { blue_dmg_percentages: blueDmgPercentages, red_dmg_percentages: redDmgPercentages };
}


//get match start date

export function matchDate(gameData){
  const official_dates = {
    "Etape-1 ; jour 1": new Date(2026,0,24),
    "Etape-1 ; jour 2": new Date(2026,0,25),
    "Etape-1 ; jour 3": new Date(2026,0,31),
    "Etape-1 ; jour 4": new Date(2026,1,1),

    "Etape-2 ; jour 1": new Date(2026,1,28),
    "Etape-2 ; jour 2": new Date(2026,2,1),
    "Etape-2 ; jour 3": new Date(2026,2,7),
    "Etape-2 ; jour 4": new Date(2026,2,8),

    "Etape-3 ; jour 1": new Date(2026,4,2),
    "Etape-3 ; jour 2": new Date(2026,4,3),
    "Etape-3 ; jour 3": new Date(2026,4,9),
    "Etape-3 ; jour 4": new Date(2026,4,10),

    "Etape-4 ; jour 1": new Date(2026,5,27),
    "Etape-4 ; jour 2": new Date(2026,5,28),
    "Etape-4 ; jour 3": new Date(2026,6,4),
    "Etape-4 ; jour 4": new Date(2026,6,5),

    "Etape-5 ; jour 1": new Date(2026,6,18),
    "Etape-5 ; jour 2": new Date(2026,6,19),
    "Etape-5 ; jour 3": new Date(2026,6,25),
    "Etape-5 ; jour 4": new Date(2026,6,26),

    "Etape-6 ; jour 1": new Date(2026,7,15),
    "Etape-6 ; jour 2": new Date(2026,7,16),
    "Etape-6 ; jour 3": new Date(2026,7,22),
    "Etape-6 ; jour 4": new Date(2026,7,23),

    "GA ; jour 1": new Date(2026,3,4),
    "GA ; jour 2": new Date(2026,3,5),
    "GA ; jour 3": new Date(2026,3,6),

    "KOF ; jour 1": new Date(2026,4,30),
    "KOF ; jour 2": new Date(2026,4,31),
  }

  const gameDateObj = new Date(gameData.info.gameCreation)
  const game_date_fr = gameDateObj.toLocaleDateString("fr-FR")
  let label = ""

  for (const [key, date] of Object.entries(official_dates)) {
    const officialDateFR = date.toLocaleDateString("fr-FR")
    console.log(officialDateFR, game_date_fr)
    if (officialDateFR === game_date_fr) {
      label = key
      console.log(date)
      break
    }
  }

  const result = label ? `${game_date_fr} - ${label}` : game_date_fr
  return result
}
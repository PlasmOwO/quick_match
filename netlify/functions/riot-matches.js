// netlify/functions/riot-matches.js
export async function handler(event) {
  const { puuid, nb_matches, start_timestamp, end_timestamp } = event.queryStringParameters;
  const RIOT_API_KEY = process.env.RIOT_API_KEY;

  const params = new URLSearchParams({ type: "tourney", start: 0, count: nb_matches });
  if (start_timestamp) params.append("startTime", start_timestamp);
  if (end_timestamp) params.append("endTime", end_timestamp);

  const res = await fetch(
    `https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/${puuid}/ids?${params.toString()}`,
    { headers: { "X-Riot-Token": RIOT_API_KEY } }
  );
  const data = await res.json();

  return { statusCode: 200, body: JSON.stringify(data) };
}

// netlify/functions/riot-match-data.js
export async function handler(event) {
  const matchId = event.queryStringParameters.match_id;
  const RIOT_API_KEY = process.env.RIOT_API_KEY;


  if (!RIOT_API_KEY) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: "RIOT_API_KEY missing" })
      }
    }

  const res = await fetch(
    `https://europe.api.riotgames.com/lol/match/v5/matches/${matchId}`,
    { headers: { "X-Riot-Token": RIOT_API_KEY } }
  );
  const data = await res.json();

  return { statusCode: 200, body: JSON.stringify(data) };
}

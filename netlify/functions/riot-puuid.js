// netlify/functions/riot-puuid.js
export async function handler(event) {
  const { player_name, player_tag } = event.queryStringParameters;
  const RIOT_API_KEY = process.env.RIOT_API_KEY;

  if (!RIOT_API_KEY) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: "RIOT_API_KEY missing" })
      }
    }

  const res = await fetch(
    `https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/${player_name}/${player_tag}`,
    { headers: { "X-Riot-Token": RIOT_API_KEY } }
  );
  const data = await res.json();

  return {
    statusCode: 200,
    body: JSON.stringify({"puuid" : data.puuid})
  };
}

<script setup>
import { ref } from 'vue'
import DatePicker from 'primevue/datepicker';

const player_name = ref('')
const player_tag = ref('')
const player_puuid = ref('')
const list_matches = ref([])
const number_of_game = ref(5)
const matches_data = ref([])

async function get_puuid()
{
  const response = await fetch(`http://127.0.0.1:8000/puuid?player_name=${player_name.value}&player_tag=${player_tag.value}`)
  const data = await response.json()
  player_puuid.value = data
}

async function get_matches()
{
  const response = await fetch(`http://127.0.0.1:8000/list_player_matches?puuid=${player_puuid.value}&nb_matches=${number_of_game.value}`)
  const data = await response.json()
  list_matches.value = data
}


async function get_match_details(match_data)
{
  const response = await fetch(`http://127.0.0.1:8000/match_details?player_puuid=${player_puuid.value}`,
    {
      method: 'POST',
      headers : {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({game_data : match_data})
    }
  )
  const data = await response.json()
  return data
}

async function get_gold_percent_player(match_data)
{
  const response = await fetch(`http://127.0.0.1:8000/gold_percent_player/`,
    {
      method: 'POST',
      headers : {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({game_data : match_data})
    }
  )

  return await response.json()
}

async function get_dmg_percent_player(match_data)
{
  const response = await fetch(`http://127.0.0.1:8000/dmg_percent_player/`,
    {
      method: 'POST',
      headers : {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({game_data : match_data})
    }
  )

  return await response.json()
}

//Fonction that retrieve data only one time and call function to get specific fields
async function get_match_data()
{
  const allMatchesData = await Promise.all(
    list_matches.value.map(async (match) =>{
      const response = await fetch(`http://127.0.0.1:8000/match_data/${match}`)
      const match_data = await response.json()

      
      const [details, gold, dmg] = await Promise.all([
        get_match_details(match_data),
        get_gold_percent_player(match_data),
        get_dmg_percent_player(match_data)
      ])
      return { details, gold, dmg}
    })
  )
  console.log(allMatchesData)
  return allMatchesData
}



async function handleSubmit(e) {
  e.preventDefault()
  await get_puuid()
  await get_matches()


  const allMatchesData = await get_match_data()

  
  // Associe les données aux matchs
  list_matches.value = list_matches.value.map((match, index) => ({
    ...match,
    ...allMatchesData[index]
  }))
  
  matches_data.value = allMatchesData

}
//flex content-center items-center justify-center
</script>

<template>
  <section class="bg-gray-900 min-h-screen text-white flex items-center justify-center">
    <div class="container flex flex-col gap-4 max-w-1/2 m-auto py-6">
      <h1 class="text-center font-sans text-4xl font-bold">Quick Match</h1>
      <hr>
    <br>
    <form class="bg-gray-900 rounded w-full mx-auto flex flex-col gap-4"  @submit="handleSubmit">
        <input class="bg-gray-800 shadow appearance-none border-3 rounded w-full py-2 px-3 text-gray-400 leading-tight focus:outline-none focus:shadow-outline" v-model="player_name" type="text" placeholder="Summoner name">
        <input class="bg-gray-800 shadow appearance-none border-3 rounded w-full py-2 px-3 text-gray-400 leading-tight focus:outline-none focus:shadow-outline" v-model="player_tag" type="text" placeholder="Summoner tag">
        <DatePicker class="bg-gray-800 shadow appearance-none border-3 rounded w-full  text-gray-400 leading-tight focus:outline-none focus:shadow-outline placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition" v-model="icondisplay" showIcon dark fluid selection-mode="range" placeholder="Select a date" />
        <input class="bg-gray-800 shadow appearance-none border-3 rounded w-full py-2 px-3 text-gray-400 leading-tight focus:outline-none focus:shadow-outline" v-model="number_of_game" type="number" placeholder="Number of game">
      <div class="flex flex-col items-center">
        <button type="submit" class="bg-transparent hover:bg-gray-300 hover:text-gray-800 py-2 px-4 border rounded-2xl">Search</button>
      </div>
    </form>
    <br>
    <!-- Matches Data Section -->
    <div class="w-full y space-y-8" v-if="matches_data.length> 0">
      <div v-for="(match, index) in matches_data" :key="index" class="bg-gray-900 rounded-lg p-8 border border-gray-700">
        <!-- Match Result Header -->
        <h2 class="text-3xl font-bold mb-8 text-center" :class="match.details?.win === false ? 'text-red-500' : 'text-green-500'">
          {{ match.details?.win === false ? 'Defeat' : 'Victory'}}
        </h2>
        
        <!-- Main Grid: Left Team | Stats | Right Team -->
        <div class="grid grid-cols-3 gap-0.1">
          
          <!-- LEFT SIDE: Blue Team -->
          <div class="flex flex-col gap-6">
            <div
              v-for="(championName, pIndex) in match.details?.blue_champions?.name || []"
              :key="`blue-${pIndex}`"
              class="flex items-center justify-between gap-4"
            >
              <div class="flex items-center gap-3 flex-1">
                <!-- Avatar -->
                <div class="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-xs">
                  <img :src="`https://ddragon.leagueoflegends.com/cdn/16.3.1/img/champion/${match.details?.blue_champions?.id?.[pIndex]}.png`">
                </div>

                <!-- Texte -->
                <div class="flex flex-col">
                  <span class="font-semibold" :class="match.details.blue_names[pIndex] ===player_name ? 'text-green-300' : 'text-blue-400'">
                    {{ match.details.blue_names[pIndex] }}
                  </span>
                  <span class="text-gray-400 text-sm">
                    {{ championName }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- CENTER: Stats -->
          <div class="flex flex-col gap-6">
          <!-- Headers -->
          <div class="grid grid-cols-4 gap-4 text-center border-b border-gray-600 pb-4">
            <div class="text-gray-400 text-sm font-semibold">GOLD %</div>
            <div class="text-gray-400 text-sm font-semibold">DMG %</div>
            <div class="text-gray-400 text-sm font-semibold">DMG %</div>
            <div class="text-gray-400 text-sm font-semibold">GOLD %</div>
          </div>

          <!-- Player Stats for BLUE team -->
          <div
            v-for="(dmg, pIndex) in match.dmg?.blue_dmg_percentages || []"
            :key="`blue-stats-${pIndex}`"
            class="grid grid-cols-4 gap-4 text-center items-center"
          >
            <!-- Gold % blue -->
            <div  :class="Math.max(...match.gold?.blue_gold_percentages) == match.gold?.blue_gold_percentages?.[pIndex] ? 'text-amber-300 font-bold' : 'text-white'">
              {{ match.gold?.blue_gold_percentages?.[pIndex]?.toFixed(2) || '0' }}
            </div>

            <!-- Dmg % blue -->
            <div :class="Math.max(...match.dmg?.blue_dmg_percentages) == dmg ? 'text-amber-300 font-bold' : 'text-white'">
              {{ dmg?.toFixed(2) || '0' }}
            </div>

            <!-- Dmg % red -->
            <div :class="Math.max(...match.dmg?.red_dmg_percentages) == match.dmg?.red_dmg_percentages?.[pIndex] ? 'text-amber-300 font-bold' : 'text-white'">
              {{ match.dmg?.red_dmg_percentages?.[pIndex]?.toFixed(2) || '0' }}
            </div>

            <!-- Gold % red -->
            <div :class="Math.max(...match.gold?.red_gold_percentages) == match.gold?.red_gold_percentages?.[pIndex] ? 'text-amber-300 font-bold' : 'text-white'">
              {{ match.gold?.red_gold_percentages?.[pIndex]?.toFixed(2) || '0' }}
            </div>
          </div>
        </div>

          <!-- RIGHT SIDE: Red Team (Mirrored) -->
          <div class="flex flex-col gap-6">
            <div
              v-for="(championName, pIndex) in match.details?.red_champions?.name || []"
              :key="`red-${pIndex}`"
              class="flex items-center justify-between gap-4"
            >

              <div class="flex items-center gap-3 flex-1 justify-end">
                <div class="flex flex-col text-right">
                  <span class="font-semibold" :class="match.details.red_names[pIndex] === player_name ? 'text-green-300' : 'text-red-400'">{{ match.details?.red_names[pIndex] }}</span>
                  <span class="text-gray-400 text-sm">{{ championName }}</span>
                </div>
                <div class="w-12 h-12 rounded-full bg-red-700 flex items-center justify-center text-white font-bold text-xs">
                  <img :src="`https://ddragon.leagueoflegends.com/cdn/16.3.1/img/champion/${match.details?.red_champions?.id?.[pIndex]}.png`">
                </div>
              </div>
            
            </div>
          </div>
          
        </div>

        <!-- Bans Section -->
        <div class="grid grid-cols-3 gap-8 mt-8">
          <!-- Left Items -->
          <div class="flex justify-start gap-2">
            <div v-for="(ban, i) in match.details?.blue_bans?.id" :key="`left-item-${i}`" class="w-8 h-8 bg-gray-700 rounded border border-gray-600">
              <img :src="`https://ddragon.leagueoflegends.com/cdn/16.3.1/img/champion/${ban}.png`" @error="e =>e.target.src = `/missing_ban.jpg`">
            </div>
          </div>
          <!-- Center spacer -->
          <div></div>
          <!-- Right Items -->
          <div class="flex justify-end gap-2">
            <div v-for="(ban, i) in [...(match.details?.red_bans?.id)].reverse()" :key="`right-item-${i}`" class="w-8 h-8 bg-gray-700 rounded border border-gray-600">
              <img :src="`https://ddragon.leagueoflegends.com/cdn/16.3.1/img/champion/${ban}.png`" @error="e =>e.target.src = `/missing_ban.jpg`">
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </section>
</template>


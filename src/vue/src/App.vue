<script setup>
import { ref, watch, onMounted } from 'vue'
import DatePicker from 'primevue/datepicker';
import { matchDate,getPuuid, listPlayerMatches, requestMatchData, initDDragonVersion, championIdToName, championImageFromName, getMatchChampions, computeGoldPercentByPlayer, computeDmgRatioByPlayer} from './utils/scripts.js'
import { computed } from 'vue'
import domtoimage from 'dom-to-image-more'
import jsPDF from 'jspdf'
const player_name = ref('')
const player_tag = ref('')
const player_puuid = ref('')
const list_matches = ref([])
const number_of_game = ref(5)
const matches_data = ref([])
const ddragonVersion = ref('') 
const icondisplay = ref(null) 
const loading = ref(false)

const timestamps = computed(() => {
  if (!icondisplay.value || icondisplay.value.length !== 2 || icondisplay.value[1] == null){
    return{
      start : null,
      end : null
    }
  }


  return {
    start: Math.floor(icondisplay.value[0].getTime() / 1000),
    end: Math.floor(icondisplay.value[1].getTime() / 1000)
  }
})

async function loadDDragonVersion() {
  const version = await initDDragonVersion()
  ddragonVersion.value = version
  console.log("DDragon version loaded:", ddragonVersion.value)
}
const downloadPDF = async () => {
  const elements = document.querySelectorAll('.match-card')
  if (!elements.length) return

  // ✅ ACTIVER MODE EXPORT
  document.body.classList.add('export-mode')

  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'px',
    format: 'a4'
  })

  let first = true

  try {
    // ✅ attendre que tout soit bien rendu (images + fonts)
    await document.fonts.ready

    await Promise.all(
      Array.from(document.images).map(img => {
        if (img.complete) return Promise.resolve()
        return new Promise(res => {
          img.onload = img.onerror = res
        })
      })
    )

    for (let el of elements) {
      el.scrollIntoView({ block: 'center' })

      const dataUrl = await domtoimage.toPng(el, {
        scale: 2,
        bgcolor: '#111827'
      })

      const img = new Image()
      img.src = dataUrl
      await new Promise(res => (img.onload = res))

      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfHeight = (img.height * pdfWidth) / img.width

      if (!first) pdf.addPage()

      pdf.addImage(img, 'PNG', 0, 0, pdfWidth, pdfHeight)

      first = false
    }

    // 👇 preview navigateur
    const blob = pdf.output('blob')
    const url = URL.createObjectURL(blob)
    window.open(url)

  } finally {
    // ✅ TOUJOURS nettoyer (même si erreur)
    document.body.classList.remove('export-mode')
  }
}
loadDDragonVersion()


//DATE TO TIMESTAMP
// const icondisplay = ref(null)

// watch(icondisplay, (newValue) => {
//   if (!newValue || newValue.length === 0) {
//     start_timestamp.value = null
//     end_timestamp.value = null
//     return
//   }

//   const [startDate, endDate] = newValue

//   start_timestamp.value = startDate
//     ? Math.floor(startDate.getTime() / 1000)
//     : null

//   end_timestamp.value = endDate
//     ? Math.floor(endDate.getTime() / 1000)
//     : null
// })

///
// ----------------------------
// Remplace get_puuid
// ----------------------------
async function get_puuid(player_name, player_tag) {
  player_puuid.value = await getPuuid(player_name, player_tag)
}

// ----------------------------
// Remplace get_matches
// ----------------------------
async function get_matches(number_of_game, start_timestamp = null, end_timestamp = null) {
  const params = {
    nb_matches: number_of_game,
    start_timestamp,
    end_timestamp
  }

  list_matches.value = await listPlayerMatches(player_puuid.value, number_of_game, start_timestamp, end_timestamp)
}

// ----------------------------
// Remplace get_match_details
// ----------------------------
async function get_match_details(match_data) {
  return getMatchChampions(match_data, player_puuid.value)
}

// ----------------------------
// Remplace get_gold_percent_player
// ----------------------------
async function get_gold_percent_player(match_data) {
  return computeGoldPercentByPlayer(match_data)
}

// ----------------------------
// Remplace get_dmg_percent_player
// ----------------------------
async function get_dmg_percent_player(match_data) {
  return computeDmgRatioByPlayer(match_data)
}

async function get_match_date(match_data){
  return matchDate(match_data)
}
// ----------------------------
// Remplace get_match_data
// ----------------------------
async function get_match_data() {
  const allMatchesData = await Promise.all(
    list_matches.value.map(async (match) => {
      // On récupère directement les données du match depuis Riot
      const match_data = await requestMatchData(match)

      const [details, gold, dmg,date] = await Promise.all([
        get_match_details(match_data),
        get_gold_percent_player(match_data),
        get_dmg_percent_player(match_data),
        get_match_date(match_data)
      ])

      return { details, gold, dmg , date}
    })
  )
  // console.log(allMatchesData)
  return allMatchesData
}

// ----------------------------
// Remplace handleSubmit
// ----------------------------
async function handleSubmit(e) {
  e.preventDefault()

  loading.value = true

  // On utilise directement les refs Vue
  try {
    await get_puuid(player_name.value, player_tag.value)
    await get_matches(number_of_game.value, timestamps.value.start, timestamps.value.end)

    const allMatchesData = await get_match_data()

    // Associe les données aux matchs
    list_matches.value = list_matches.value.map((match, index) => ({
      ...match,
      ...allMatchesData[index]
    }))

    matches_data.value = allMatchesData
  } catch(error){
    console.error("Erreur", error)
  } finally{
    loading.value = false
  }
}
</script>

<template>
  <section id="page-content" class="bg-gray-900 min-h-screen text-white flex items-center justify-center">
    <div class="absolute top-6 right-6">
    <button
      @click="downloadPDF()"
      class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600">
      Export page
    </button>
  </div>
    <div class="flex flex-col gap-4 w-full px-2 md:px-4 lg:max-w-4xl m-auto py-6">
      <h1 class="text-center font-sans text-2xl md:text-4xl font-bold">Quick Match</h1>
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
    <div v-if="loading" class="w-full h-2 bg-gray-700 rounded overflow-hidden">
      <div class="h-full bg-blue-500 animate-pulse w-full"></div>
    </div>
    <br>
    <!-- Matches Data Section -->
    <div id="match-data" class="w-full y space-y-8" v-if="matches_data.length> 0">
      <div v-for="(match, index) in matches_data" :key="index" class="match-card bg-gray-900 rounded-lg p-8 border border-gray-700">
        <!-- Match Result Header -->
        <p class="text-stone-300 font-mono">{{match?.date}}</p>

        <h2 class="text-xl md:text-3xl font-bold mb-8 text-center font-sans" :class="match.details?.win === false ? 'text-violet-200' : 'text-green-500'">
          {{ match.details?.win === false ? 'Defeat' : 'Victory'}}
        </h2>

        
        <!-- Main Grid: Left Team | Stats | Right Team -->
        <div class="grid grid-cols-2 gap-2 md:grid-cols-3 md:gap-6">
          
          <!-- LEFT SIDE: Blue Team -->
          <div class="flex flex-col gap-2 md:gap-6">
            <div
              v-for="(championName, pIndex) in match.details?.blue_champions?.name || []"
              :key="`blue-${pIndex}`"
              class="flex items-center justify-between gap-4"
            >
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <!-- Avatar -->
                <div class="w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center">
                  <img v-if="ddragonVersion" :src="`https://ddragon.leagueoflegends.com/cdn/${ddragonVersion}/img/champion/${match.details?.blue_champions?.id?.[pIndex]}.png`"
                  class="w-full h-full object-contain">
                </div>

                <!-- Texte -->
                <div class="flex flex-col min-w-0">
                  <span class="font-semibold truncate" :class="match.details.blue_names[pIndex] ===player_name ? 'text-green-300' : 'text-blue-400'">
                    {{ match.details.blue_names[pIndex] }}
                  </span>
                  <span class="text-gray-400 text-sm truncate">
                    {{ championName }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- CENTER: Stats -->
          <div class="hidden md:flex flex-col">

            <!-- Headers (séparés visuellement) -->
            <div class="grid grid-cols-4 text-sm md:text-xs lg:text-sm text-center border-b border-gray-600 pb-1 mb-2 -mt-6">
              <div class="text-gray-400 font-semibold">GOLD %</div>
              <div class="text-gray-400 font-semibold">DMG %</div>
              <div class="text-gray-400 font-semibold">DMG %</div>
              <div class="text-gray-400 font-semibold">GOLD %</div>
            </div>

            <!-- Stats alignées avec joueurs -->
            <div class="flex flex-col gap-2 md:gap-10 lg:gap-8">
              <div
                v-for="(dmg, pIndex) in match.dmg?.blue_dmg_percentages || []"
                :key="`blue-stats-${pIndex}`"
                class="grid grid-cols-4 text-center items-center h-12 md:h-10 text-sm md:text-xs lg:text-sm"
              >
                <!-- Gold % blue -->
                <div :class="Math.max(...match.gold?.blue_gold_percentages) == match.gold?.blue_gold_percentages?.[pIndex] ? 'text-amber-300 font-bold' : 'text-white'">
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
          </div>

          <!-- RIGHT SIDE: Red Team (Mirrored) -->
          <div class="flex flex-col gap-2 md:gap-6">
            <div
              v-for="(championName, pIndex) in match.details?.red_champions?.name || []"
              :key="`red-${pIndex}`"
              class="flex items-center justify-between gap-4"
            >

              <div class="flex items-center gap-3 flex-1 min-w-0 justify-end">
                <div class="flex flex-col text-right min-w-0">
                  <span class="font-semibold truncate" :class="match.details.red_names[pIndex] === player_name ? 'text-green-300' : 'text-red-400'">{{ match.details?.red_names[pIndex] }}</span>
                  <span class="text-gray-400 text-sm truncate">{{ championName }}</span>
                </div>
                <div class="w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center">
                  <img v-if="ddragonVersion" :src="`https://ddragon.leagueoflegends.com/cdn/${ddragonVersion}/img/champion/${match.details?.red_champions?.id?.[pIndex]}.png`"
                  class="w-full h-full object-contain">
                </div>
              </div>
            
            </div>
          </div>
          
        </div>

        <!-- Bans Section -->
        <div class="grid grid-cols-3 gap-8 mt-8">
          <!-- Left Items -->
          <div class="flex justify-start gap-2 flex-wrap">
            <div v-for="(ban, i) in match.details?.blue_bans?.id" :key="`left-item-${i}`" class="w-8 h-8 bg-gray-700 rounded border border-gray-600">
              <img v-if="ddragonVersion" :src="`https://ddragon.leagueoflegends.com/cdn/${ddragonVersion}/img/champion/${ban}.png`" @error="e =>e.target.src = `/missing_ban.jpg`">
            </div>
          </div>
          <!-- Center spacer -->
          <div></div>
          <!-- Right Items -->
          <div class="flex justify-end gap-2 flex-wrap">
            <div v-for="(ban, i) in [...(match.details?.red_bans?.id)].reverse()" :key="`right-item-${i}`" class="w-8 h-8 bg-gray-700 rounded border border-gray-600">
              <img v-if="ddragonVersion" :src="`https://ddragon.leagueoflegends.com/cdn/${ddragonVersion}/img/champion/${ban}.png`" @error="e =>e.target.src = `/missing_ban.jpg`">
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </section>
</template>


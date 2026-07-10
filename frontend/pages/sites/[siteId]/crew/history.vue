<template>
  <div>
    <NuxtLink :to="`/sites/${siteId}/crew`" class="ui-link mb-4 inline-block">← Workers</NuxtLink>
    <UiPageHeader title="Attendance history" subtitle="See which days a worker was present" />

    <UiCard class="mb-5">
      <label class="ui-label" for="worker-search">Worker</label>
      <div ref="searchWrap" class="relative">
        <input
          id="worker-search"
          v-model="search"
          type="text"
          class="ui-input"
          placeholder="Type to search workers…"
          autocomplete="off"
          @focus="dropdownOpen = true"
          @input="onSearchInput"
        />
        <button
          v-if="selectedWorker"
          type="button"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-gray-400 hover:text-gray-600"
          @click="clearWorker"
        >
          Clear
        </button>

        <ul
          v-if="dropdownOpen && filteredWorkers.length"
          class="absolute z-20 mt-1 max-h-48 w-full overflow-auto rounded-lg border border-gray-200 bg-white py-1 shadow-lg"
        >
          <li v-for="w in filteredWorkers" :key="w.id">
            <button
              type="button"
              class="flex w-full items-center gap-3 px-3 py-2.5 text-left text-sm hover:bg-violet-50"
              :class="selectedWorkerId === w.id ? 'bg-violet-50 font-semibold text-violet-800' : 'text-gray-900'"
              @mousedown.prevent="selectWorker(w)"
            >
              <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet-100 text-xs font-bold uppercase text-violet-700">
                {{ w.name.slice(0, 1) }}
              </span>
              <span class="min-w-0 flex-1 truncate">{{ w.name }}</span>
              <span class="shrink-0 text-xs text-gray-500">{{ w.daily_wage }}/day</span>
            </button>
          </li>
        </ul>
        <p v-else-if="dropdownOpen && search && !filteredWorkers.length" class="absolute z-20 mt-1 w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-500 shadow-lg">
          No workers match “{{ search }}”.
        </p>
      </div>
    </UiCard>

    <template v-if="selectedWorker">
      <div class="mb-4 flex items-center justify-between gap-3">
        <div>
          <p class="text-sm font-semibold text-gray-900">{{ selectedWorker.name }}</p>
          <p class="text-xs text-gray-500">{{ monthLabel }} · {{ presentCount }} day{{ presentCount === 1 ? '' : 's' }} present</p>
        </div>
        <div class="flex items-center gap-1">
          <button type="button" class="ui-btn-ghost rounded-lg px-2 py-2" aria-label="Previous month" @click="prevMonth">
            <AppNavIcon name="chevron-down" class="h-5 w-5 rotate-90" />
          </button>
          <button type="button" class="ui-btn-ghost rounded-lg px-2 py-2" aria-label="Next month" @click="nextMonth">
            <AppNavIcon name="chevron-down" class="h-5 w-5 -rotate-90" />
          </button>
        </div>
      </div>

      <p v-if="calendarLoading" class="ui-muted">Loading calendar…</p>
      <p v-else-if="calendarErr" class="text-red-600">{{ calendarErr }}</p>
      <UiCard v-else>
        <div class="mb-3 grid grid-cols-7 gap-1 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">
          <span v-for="d in weekDays" :key="d">{{ d }}</span>
        </div>
        <div class="grid grid-cols-7 gap-1">
          <div
            v-for="(cell, idx) in calendarCells"
            :key="idx"
            class="flex aspect-square items-center justify-center rounded-lg text-sm"
            :class="cellClass(cell)"
          >
            <template v-if="cell.day">
              <span v-if="cell.present" class="flex h-9 w-9 flex-col items-center justify-center rounded-full bg-violet-600 text-white shadow-sm">
                <span class="text-[10px] font-bold leading-none">{{ cell.day }}</span>
                <svg class="mt-0.5 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </span>
              <span v-else class="font-medium text-gray-700">{{ cell.day }}</span>
            </template>
          </div>
        </div>

        <div class="mt-4 flex items-center gap-4 border-t border-gray-100 pt-3 text-xs text-gray-500">
          <span class="flex items-center gap-1.5">
            <span class="flex h-5 w-5 items-center justify-center rounded-full bg-violet-600 text-white">
              <svg class="h-2.5 w-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </span>
            Present
          </span>
          <span>Empty = absent or not logged</span>
        </div>
      </UiCard>
    </template>

    <UiCard v-else class="text-center">
      <p class="text-gray-600">Select a worker above to view their attendance calendar.</p>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'

type Worker = { id: string; name: string; daily_wage: string }
type HistoryDay = { date: string; wage_rate: string }
type HistoryResponse = {
  labour_name: string
  year: number
  month: number
  present_count: number
  days: HistoryDay[]
}
type CalendarCell = { day: number | null; present: boolean; date: string | null }

const route = useRoute()
const siteId = computed(() => String(route.params.siteId || ''))
const api = createApiClient()

const workers = ref<Worker[]>([])
const workersLoading = ref(false)
const search = ref('')
const dropdownOpen = ref(false)
const selectedWorkerId = ref('')
const viewMonth = ref(dayjs())
const presentDates = ref<Set<string>>(new Set())
const presentCount = ref(0)
const calendarLoading = ref(false)
const calendarErr = ref('')
const searchWrap = ref<HTMLElement | null>(null)

const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const selectedWorker = computed(() => workers.value.find((w) => w.id === selectedWorkerId.value) ?? null)

const filteredWorkers = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return workers.value
  return workers.value.filter((w) => w.name.toLowerCase().includes(q))
})

const monthLabel = computed(() => viewMonth.value.format('MMMM YYYY'))

const calendarCells = computed((): CalendarCell[] => {
  const m = viewMonth.value
  const year = m.year()
  const month = m.month()
  const daysInMonth = m.daysInMonth()
  const startOffset = (m.startOf('month').day() + 6) % 7 // Monday-first

  const cells: CalendarCell[] = []
  for (let i = 0; i < startOffset; i++) {
    cells.push({ day: null, present: false, date: null })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = dayjs(new Date(year, month, d)).format('YYYY-MM-DD')
    cells.push({
      day: d,
      present: presentDates.value.has(dateStr),
      date: dateStr,
    })
  }
  return cells
})

function cellClass(cell: CalendarCell) {
  if (!cell.day) return ''
  if (cell.present) return ''
  return 'bg-gray-50/80'
}

function onSearchInput() {
  dropdownOpen.value = true
  if (!search.value.trim()) selectedWorkerId.value = ''
}

function selectWorker(w: Worker) {
  selectedWorkerId.value = w.id
  search.value = w.name
  dropdownOpen.value = false
  loadHistory()
}

function clearWorker() {
  selectedWorkerId.value = ''
  search.value = ''
  presentDates.value = new Set()
  presentCount.value = 0
}

async function loadWorkers() {
  workersLoading.value = true
  try {
    const { data } = await api.get('/labours/', { params: { site_id: siteId.value } })
    workers.value = unwrapResults<Worker>(data)
  } catch {
    workers.value = []
  } finally {
    workersLoading.value = false
  }
}

async function loadHistory() {
  if (!selectedWorkerId.value || !siteId.value) return
  calendarLoading.value = true
  calendarErr.value = ''
  try {
    const { data } = await api.get<HistoryResponse>('/attendance/worker-history/', {
      params: {
        site_id: siteId.value,
        labour_id: selectedWorkerId.value,
        year: viewMonth.value.year(),
        month: viewMonth.value.month() + 1,
      },
    })
    presentDates.value = new Set(data.days.map((d) => d.date))
    presentCount.value = data.present_count
  } catch {
    calendarErr.value = 'Could not load attendance history.'
    presentDates.value = new Set()
    presentCount.value = 0
  } finally {
    calendarLoading.value = false
  }
}

function prevMonth() {
  viewMonth.value = viewMonth.value.subtract(1, 'month')
  if (selectedWorkerId.value) loadHistory()
}

function nextMonth() {
  viewMonth.value = viewMonth.value.add(1, 'month')
  if (selectedWorkerId.value) loadHistory()
}

function closeDropdown() {
  dropdownOpen.value = false
}

onMounted(() => {
  loadWorkers()
  document.addEventListener('click', closeDropdownOnOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdownOnOutside)
})

function closeDropdownOnOutside(e: MouseEvent) {
  if (searchWrap.value && !searchWrap.value.contains(e.target as Node)) {
    closeDropdown()
  }
}

watch(siteId, () => {
  clearWorker()
  loadWorkers()
})

watch(
  () => route.query.labour_id,
  (id) => {
    if (typeof id !== 'string' || !id) return
    const w = workers.value.find((x) => x.id === id)
    if (w) selectWorker(w)
  },
  { immediate: true },
)

watch(workers, (list) => {
  const id = route.query.labour_id
  if (typeof id === 'string' && id && !selectedWorkerId.value) {
    const w = list.find((x) => x.id === id)
    if (w) selectWorker(w)
  }
})
</script>

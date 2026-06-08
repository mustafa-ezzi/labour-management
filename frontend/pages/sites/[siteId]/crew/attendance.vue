<template>
  <div>
    <NuxtLink :to="`/sites/${siteId}/crew`" class="ui-link mb-4 inline-block">← Workers</NuxtLink>
    <UiPageHeader title="Attendance" subtitle="Mark present, half day, or absent for the day" />

    <div class="lg:grid lg:grid-cols-12 lg:gap-8">
      <div class="space-y-4 lg:col-span-4">
        <UiCard>
          <label class="ui-label" for="day">Date</label>
          <input id="day" v-model="day" type="date" class="ui-input" @change="onDayChange" />
        </UiCard>

        <div
          v-if="daySummary"
          class="ui-card grid grid-cols-1 gap-3 sm:grid-cols-3 lg:grid-cols-1"
        >
          <div>
            <p class="ui-label !mb-0">Earned today</p>
            <p class="ui-stat-value lg:!text-gray-900">{{ daySummary.total_earned_today }}</p>
          </div>
          <div>
            <p class="ui-label !mb-0">Paid today</p>
            <p class="ui-stat-value text-green-300 lg:text-green-700">{{ daySummary.total_paid_today }}</p>
          </div>
          <div>
            <p class="ui-label !mb-0">Outstanding</p>
            <p class="ui-stat-value text-amber-300 lg:text-amber-600">{{ daySummary.total_pending_today }}</p>
          </div>
          <p class="text-xs text-white/35 lg:text-gray-400 sm:col-span-3 lg:col-span-1">
            {{ daySummary.total_pending_carried_forward }} carried from before · roster cap
            {{ daySummary.total_roster_daily }}/day
          </p>
        </div>
        <p v-if="summaryErr" class="text-sm text-amber-500/90">{{ summaryErr }}</p>
      </div>

      <div class="mt-6 lg:col-span-8 lg:mt-0">
        <p v-if="loading" class="ui-muted">Loading roster…</p>
        <p v-else-if="error" class="text-red-400">{{ error }}</p>
        <template v-else>
          <ul class="space-y-2 lg:grid lg:grid-cols-2 lg:gap-3 lg:space-y-0">
            <li
              v-for="row in rows"
              :key="row.labour.id"
              class="flex items-center justify-between gap-3 rounded-lg border border-white/[0.07] bg-white/[0.04] px-4 py-3 lg:border-gray-200 lg:bg-white lg:shadow-sm lg:py-4"
            >
              <div class="min-w-0">
                <p class="truncate font-medium text-white lg:text-gray-900">{{ row.labour.name }}</p>
                <p class="text-xs text-white/40 lg:text-gray-500">{{ row.labour.daily_wage }}/day</p>
              </div>
              <label
                class="flex shrink-0 cursor-pointer items-center gap-2 rounded-lg px-2 py-1 text-sm text-white/70 hover:bg-white/[0.06] lg:text-gray-700 lg:hover:bg-gray-100"
              >
                <span class="hidden sm:inline">Present</span>
                <input
                  v-model="row.present"
                  type="checkbox"
                  class="h-5 w-5 rounded border-white/30 text-green-500 focus:ring-green-500"
                />
              </label>
            </li>
          </ul>
          <p v-if="!rows.length" class="mt-4 ui-muted">No active workers on this site.</p>
          <div v-else class="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              class="ui-btn-primary w-full sm:w-auto sm:min-w-[12rem]"
              :disabled="saving"
              @click="saveMarks"
            >
              {{ saving ? 'Saving…' : 'Save attendance' }}
            </button>
          </div>
          <p v-if="saveMsg" class="mt-2 text-center text-sm text-green-400 lg:text-right">{{ saveMsg }}</p>
          <p v-if="saveErr" class="mt-2 text-center text-sm text-red-400 lg:text-right">{{ saveErr }}</p>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
type LabourRow = { id: string; name: string; daily_wage: string; status: string }
type AttRow = { id: string; labour_id: string; present: boolean }
type DaySummary = {
  site_id: string
  date: string
  total_earned_today: string
  total_paid_today: string
  total_pending_today: string
  total_pending_carried_forward: string
  total_roster_daily: string
}

const route = useRoute()
const siteId = computed(() => String(route.params.siteId || ''))
const api = createApiClient()

const day = ref(new Date().toISOString().slice(0, 10))
const loading = ref(false)
const error = ref('')
const saving = ref(false)
const saveMsg = ref('')
const saveErr = ref('')
const daySummary = ref<DaySummary | null>(null)
const summaryErr = ref('')
const rows = ref<{ labour: LabourRow; present: boolean }[]>([])

async function onDayChange() {
  saveMsg.value = ''
  saveErr.value = ''
  await loadDay()
}

async function loadDaySummary(clear = true) {
  summaryErr.value = ''
  if (clear) daySummary.value = null
  if (!siteId.value) return
  try {
    const { data } = await api.get<DaySummary>('/attendance/day-summary/', {
      params: { site_id: siteId.value, date: day.value },
    })
    daySummary.value = data
  } catch {
    summaryErr.value = 'Could not load day totals.'
  }
}

async function loadDay() {
  rows.value = []
  saveMsg.value = ''
  saveErr.value = ''
  if (!siteId.value) return
  loading.value = true
  error.value = ''
  try {
    const [labRes, attRes] = await Promise.all([
      api.get('/labours/', { params: { site_id: siteId.value, status: 'active' } }),
      api.get('/attendance/', { params: { site_id: siteId.value, date: day.value } }),
      loadDaySummary(false),
    ])
    const labours = unwrapResults<LabourRow>(labRes.data)
    const marks = unwrapResults<AttRow>(attRes.data)
    const byLabour: Record<string, boolean> = {}
    for (const m of marks) {
      byLabour[m.labour_id] = m.present
    }
    rows.value = labours.map((l) => ({
      labour: l,
      present: byLabour[l.id] ?? false,
    }))
  } catch {
    error.value = 'Could not load attendance.'
  } finally {
    loading.value = false
  }
}

async function saveMarks() {
  if (!siteId.value || !rows.value.length) return
  saving.value = true
  saveMsg.value = ''
  saveErr.value = ''
  try {
    await api.post('/attendance/bulk-mark/', {
      site_id: siteId.value,
      date: day.value,
      marks: rows.value.map((r) => ({
        labour_id: r.labour.id,
        present: r.present,
      })),
    })
    saveMsg.value = 'Saved.'
    await loadDay()
  } catch {
    saveErr.value = 'Could not save. Try again.'
  } finally {
    saving.value = false
  }
}

watch(siteId, loadDay, { immediate: true })
</script>

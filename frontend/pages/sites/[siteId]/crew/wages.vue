<template>
  <div>
    <NuxtLink :to="`/sites/${siteId}/crew`" class="ui-link mb-4 inline-block">← Workers</NuxtLink>
    <UiPageHeader title="Daily Wages" subtitle="Wage of the day + amount paid — pending is calculated for you">
      <template v-if="rows.length" #action>
        <button type="button" class="ui-btn-secondary text-xs sm:text-sm" @click="fillPaidEqualsWage">
          Paid = wage
        </button>
      </template>
    </UiPageHeader>

    <div class="mb-5 grid gap-4 lg:grid-cols-12 lg:gap-8">
      <UiCard class="lg:col-span-4">
        <label class="ui-label" for="day">Date</label>
        <input id="day" v-model="day" type="date" class="ui-input" @change="onDayChange" />
        <p v-if="daySummary" class="mt-2 text-xs text-gray-400">
          {{ daySummary.total_pending_carried_forward }} carried from before · roster cap
          {{ daySummary.total_roster_daily }}/day
        </p>
      </UiCard>

      <div class="grid grid-cols-3 gap-3 lg:col-span-8">
        <div class="rounded-xl border border-violet-200 bg-violet-50 px-3 py-3 text-center">
          <p class="text-[10px] uppercase tracking-wide text-violet-600">Wage today</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums text-violet-800">{{ formatAmount(totals.wage) }}</p>
        </div>
        <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-3 text-center">
          <p class="text-[10px] uppercase tracking-wide text-emerald-600">Paid today</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums text-emerald-800">{{ formatAmount(totals.paid) }}</p>
        </div>
        <div class="rounded-xl border border-amber-200 bg-amber-50 px-3 py-3 text-center">
          <p class="text-[10px] uppercase tracking-wide text-amber-600">Pending today</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums text-amber-800">{{ formatAmount(totals.pending) }}</p>
        </div>
      </div>
    </div>

    <p v-if="loading" class="ui-muted">Loading roster…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <template v-else>
      <ul class="space-y-2">
        <li
          v-for="row in rows"
          :key="row.labour_id"
          class="overflow-hidden rounded-xl border transition-colors"
          :class="
            row.expanded
              ? 'border-violet-300 bg-white shadow-sm'
              : row.present
                ? 'border-violet-200 bg-violet-50/40'
                : 'border-gray-200 bg-white'
          "
        >
          <!-- Collapsed header: name + rate only -->
          <button
            type="button"
            class="flex w-full items-center gap-3 px-4 py-3.5 text-left"
            @click="toggleExpand(row)"
          >
            <span
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold uppercase"
              :class="
                row.present
                  ? 'bg-violet-600 text-white shadow-sm'
                  : 'border border-gray-300 text-gray-400'
              "
            >
              {{ row.name.slice(0, 1) }}
            </span>

            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-gray-900">{{ row.name }}</p>
              <p class="text-xs text-gray-500">Rate {{ row.daily_wage }}/day</p>
              <p v-if="!row.expanded && (row.present || parseAmount(row.paid) > 0)" class="mt-0.5 text-xs text-gray-400">
                Wage {{ formatAmount(row.wage) }} · Paid {{ formatAmount(row.paid) }}
              </p>
            </div>

            <div class="flex shrink-0 items-center gap-2">
              <span
                v-if="!row.present && parseAmount(row.paid) <= 0"
                class="ui-badge-settled !bg-gray-100 !text-gray-500"
              >
                Absent
              </span>
              <span v-else-if="pendingOf(row) > 0" class="ui-badge-pending">
                {{ formatAmount(pendingOf(row)) }}
              </span>
              <span v-else class="ui-badge-settled">Settled</span>

              <AppNavIcon
                name="chevron-down"
                class="h-4 w-4 text-gray-400 transition-transform duration-200"
                :class="{ 'rotate-180': row.expanded }"
              />
            </div>
          </button>

          <!-- Expanded: wage + paid inputs -->
          <div v-if="row.expanded" class="border-t border-gray-100 bg-gray-50/80 px-4 py-4">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="ui-label" :for="`wage-${row.labour_id}`">Wage today</label>
                <input
                  :id="`wage-${row.labour_id}`"
                  v-model="row.wage"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0"
                  class="ui-input text-right tabular-nums"
                  @input="onWageInput(row)"
                />
              </div>
              <div>
                <label class="ui-label" :for="`paid-${row.labour_id}`">Paid today</label>
                <input
                  :id="`paid-${row.labour_id}`"
                  v-model="row.paid"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0"
                  class="ui-input text-right tabular-nums"
                />
              </div>
            </div>

            <div class="mt-3 flex items-center justify-between text-xs">
              <span class="text-gray-500">
                Pending today:
                <span
                  class="font-semibold"
                  :class="pendingOf(row) > 0 ? 'text-amber-600' : 'text-emerald-600'"
                >
                  {{ formatAmount(pendingOf(row)) }}
                </span>
              </span>
              <button
                v-if="parseAmount(row.wage) > 0"
                type="button"
                class="text-violet-700 hover:underline"
                @click="row.paid = row.wage"
              >
                Paid = wage
              </button>
            </div>

            <p class="mt-2 text-xs text-gray-500">
              Balance to date:
              <span class="font-semibold text-violet-700">{{ formatAmount(row.pendingWage) }}</span>
            </p>
          </div>
        </li>
      </ul>

      <p v-if="!rows.length" class="mt-4 ui-muted">No active workers on this site.</p>
      <div v-else class="sticky bottom-3 mt-6 flex flex-col gap-2 sm:flex-row sm:justify-end">
        <p v-if="saveErr" class="self-center text-sm text-red-600">{{ saveErr }}</p>
        <p v-if="saveMsg" class="self-center text-sm text-violet-700">{{ saveMsg }}</p>
        <button
          type="button"
          class="ui-btn-primary w-full shadow-2xl sm:w-auto sm:min-w-[12rem]"
          :disabled="saving"
          @click="saveAll"
        >
          {{ saving ? 'Saving…' : 'Save all' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
type WageRow = {
  labour_id: string
  name: string
  daily_wage: string
  wage: string
  paid: string
  pendingWage: string
  present: boolean
  expanded: boolean
}
type DailyWagesResponse = {
  results: {
    labour_id: string
    name: string
    daily_wage: string
    wage_today: string
    paid_today: string
    pending_today: string
    pending_wage: string
  }[]
}
type DaySummary = {
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
const rows = ref<WageRow[]>([])

function parseAmount(v: string | number): number {
  const n = typeof v === 'number' ? v : parseFloat(v)
  return Number.isFinite(n) ? n : 0
}

function formatAmount(v: string | number): string {
  return parseAmount(v).toFixed(2)
}

function pendingOf(row: WageRow): number {
  return parseAmount(row.wage) - parseAmount(row.paid)
}

const totals = computed(() => {
  let wage = 0
  let paid = 0
  for (const r of rows.value) {
    wage += parseAmount(r.wage)
    paid += parseAmount(r.paid)
  }
  return { wage, paid, pending: wage - paid }
})

function onWageInput(row: WageRow) {
  row.present = parseAmount(row.wage) > 0
}

function fillPaidEqualsWage() {
  for (const row of rows.value) {
    if (parseAmount(row.wage) > 0) {
      row.paid = row.wage
    }
  }
}

async function toggleExpand(row: WageRow) {
  row.expanded = !row.expanded
  if (row.expanded) {
    await nextTick()
    document.getElementById(`wage-${row.labour_id}`)?.focus()
  }
}

async function loadDaySummary() {
  if (!siteId.value) return
  try {
    const { data } = await api.get<DaySummary>('/attendance/day-summary/', {
      params: { site_id: siteId.value, date: day.value },
    })
    daySummary.value = data
  } catch {
    daySummary.value = null
  }
}

async function loadDay() {
  saveMsg.value = ''
  saveErr.value = ''
  if (!siteId.value) return
  loading.value = true
  error.value = ''
  try {
    const [{ data }] = await Promise.all([
      api.get<DailyWagesResponse>('/attendance/daily-wages/', {
        params: { site_id: siteId.value, date: day.value },
      }),
      loadDaySummary(),
    ])
    rows.value = data.results.map((r) => ({
      labour_id: r.labour_id,
      name: r.name,
      daily_wage: r.daily_wage,
      wage: parseAmount(r.wage_today) > 0 ? r.wage_today : '',
      paid: parseAmount(r.paid_today) > 0 ? r.paid_today : '',
      pendingWage: r.pending_wage,
      present: parseAmount(r.wage_today) > 0,
      expanded: false,
    }))
    focusFromQuery()
  } catch {
    error.value = 'Could not load daily wages.'
  } finally {
    loading.value = false
  }
}

function focusFromQuery() {
  const q = route.query.labour_id
  if (typeof q !== 'string' || !q) return
  const row = rows.value.find((r) => r.labour_id === q)
  if (!row) return
  row.expanded = true
  nextTick(() => {
    document.getElementById(`wage-${row.labour_id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  })
}

async function onDayChange() {
  await loadDay()
}

async function saveAll() {
  if (!siteId.value || !rows.value.length) return
  saving.value = true
  saveMsg.value = ''
  saveErr.value = ''
  try {
    await api.post('/attendance/bulk-wage-entry/', {
      site_id: siteId.value,
      date: day.value,
      entries: rows.value.map((r) => ({
        labour_id: r.labour_id,
        wage_amount: r.wage || 0,
        amount_paid: r.paid || 0,
      })),
    })
    saveMsg.value = 'Saved.'
    await loadDay()
  } catch (e: unknown) {
    const ax = e as { response?: { data?: { entries?: { error: string }[]; detail?: string } } }
    const lines = ax.response?.data?.entries
    saveErr.value = lines?.length
      ? lines.map((x) => x.error).join(' ')
      : ax.response?.data?.detail || 'Could not save. Try again.'
  } finally {
    saving.value = false
  }
}

watch(siteId, loadDay, { immediate: true })
</script>

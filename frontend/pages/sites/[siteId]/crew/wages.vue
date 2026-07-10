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
            row.present
              ? 'border-violet-200 bg-violet-50/50'
              : 'border-gray-200 bg-white'
          "
        >
          <div class="flex flex-wrap items-center gap-3 px-3 py-3 sm:gap-4">
            <button
              type="button"
              class="flex shrink-0 items-center gap-3"
              @click="toggleExpand(row)"
            >
              <span
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold uppercase transition-colors"
                :class="
                  row.present
                    ? 'bg-violet-600 text-white shadow-md shadow-violet-700/30'
                    : 'border border-gray-300 text-gray-400'
                "
              >
                {{ row.name.slice(0, 1) }}
              </span>
            </button>

            <div class="min-w-0 flex-1 cursor-pointer" @click="toggleExpand(row)">
              <p class="truncate text-sm font-semibold text-gray-900">{{ row.name }}</p>
              <p class="text-xs text-gray-500">Rate {{ row.daily_wage }}/day</p>
            </div>

            <div class="flex shrink-0 items-center gap-2">
              <div class="flex flex-col items-center">
                <label class="text-[9px] uppercase tracking-wide text-gray-400" :for="`wage-${row.labour_id}`">Wage</label>
                <input
                  :id="`wage-${row.labour_id}`"
                  v-model="row.wage"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0"
                  class="ui-input w-20 py-1.5 text-right text-sm tabular-nums sm:w-24"
                  @input="onWageInput(row)"
                />
              </div>
              <div class="flex flex-col items-center">
                <label class="text-[9px] uppercase tracking-wide text-gray-400" :for="`paid-${row.labour_id}`">Paid</label>
                <input
                  :id="`paid-${row.labour_id}`"
                  v-model="row.paid"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0"
                  class="ui-input w-20 py-1.5 text-right text-sm tabular-nums sm:w-24"
                />
              </div>
            </div>

            <div class="flex w-16 shrink-0 flex-col items-end">
              <span
                v-if="!row.present && parseAmount(row.paid) <= 0"
                class="rounded-full px-2 py-0.5 text-[10px] font-semibold text-gray-400"
              >
                Absent
              </span>
              <span
                v-else-if="pendingOf(row) > 0"
                class="rounded-full bg-amber-500/15 px-2 py-0.5 text-[10px] font-semibold text-amber-300 bg-amber-100 text-amber-700"
              >
                {{ formatAmount(pendingOf(row)) }}
              </span>
              <span
                v-else
                class="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-semibold text-emerald-300 bg-emerald-100 text-emerald-700"
              >
                Settled
              </span>
            </div>

            <button
              type="button"
              class="shrink-0 text-gray-400 transition-transform text-gray-400"
              :class="{ 'rotate-180': row.expanded }"
              @click="toggleExpand(row)"
            >
              <AppNavIcon name="chevron-down" class="h-4 w-4" />
            </button>
          </div>

          <div v-if="row.expanded" class="border-t border-gray-100 bg-gray-50 px-4 py-3 text-xs border-gray-100 bg-gray-50">
            <p class="text-gray-600">
              Balance to date:
              <span class="font-semibold text-violet-700">{{ formatAmount(row.pendingWage) }}</span>
            </p>
            <p v-if="row.historyLoading" class="mt-1 text-gray-400">Loading history…</p>
            <template v-else-if="row.history && row.history.length">
              <p class="mt-1 text-gray-400">Recent payments:</p>
              <ul class="mt-1 space-y-0.5">
                <li v-for="p in row.history" :key="p.id" class="text-gray-500 text-gray-600">
                  {{ p.payment_date }} — {{ formatAmount(p.amount_paid) }}
                </li>
              </ul>
            </template>
            <p v-else class="mt-1 text-gray-400">No payment history yet.</p>
            <NuxtLink :to="`/sites/${siteId}/crew/${row.labour_id}`" class="ui-link mt-2 inline-block text-xs">
              View worker →
            </NuxtLink>
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
  history: PaymentEntry[] | null
  historyLoading: boolean
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
type PaymentEntry = { id: string; amount_paid: string; payment_date: string }
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
  if (row.expanded && row.history === null && !row.historyLoading) {
    row.historyLoading = true
    try {
      const { data } = await api.get('/labour-payments/', { params: { labour_id: row.labour_id } })
      row.history = unwrapResults<PaymentEntry>(data).slice(0, 5)
    } catch {
      row.history = []
    } finally {
      row.historyLoading = false
    }
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
      history: null,
      historyLoading: false,
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

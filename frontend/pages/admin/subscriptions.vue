<template>
  <div>
    <p class="mb-4 text-sm text-gray-500">
      Renew extends the end date. Cancel marks the plan only — use
      <NuxtLink to="/admin/accounts" class="ui-link">Accounts → Disable</NuxtLink>
      to cut off login.
    </p>

    <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
      <input
        v-model="search"
        type="search"
        class="ui-input flex-1"
        placeholder="Search workspace or owner email…"
        @input="onSearch"
      />
      <div class="flex flex-wrap gap-2">
        <button
          v-for="f in filters"
          :key="f.value"
          type="button"
          class="rounded-lg px-3 py-2 text-xs font-semibold"
          :class="statusFilter === f.value ? 'bg-violet-700 text-white' : 'border border-gray-200 bg-white text-gray-600'"
          @click="setFilter(f.value)"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <p v-if="loading" class="ui-muted">Loading subscriptions…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <p v-else-if="msg" class="mb-3 text-sm text-emerald-700">{{ msg }}</p>

    <UiCard v-if="!loading && !rows.length" class="text-center text-sm text-gray-600">
      No subscriptions found.
    </UiCard>

    <ul v-else-if="!loading" class="space-y-3">
      <li
        v-for="row in rows"
        :key="row.id"
        class="rounded-xl border border-gray-200 bg-white p-4"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="text-sm font-semibold text-gray-900">{{ row.company_name }}</p>
            <p class="text-xs text-gray-500">{{ row.owner_email }} · {{ row.plan?.name }}</p>
            <p class="mt-1 text-xs text-gray-500">
              Ends {{ formatWhen(row.ends_at) }}
              <span v-if="row.days_remaining != null && !row.is_expired">
                · {{ row.days_remaining }}d left
              </span>
            </p>
          </div>
          <span
            class="rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide"
            :class="statusClass(row.status)"
          >
            {{ row.status }}
          </span>
        </div>

        <div class="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            class="ui-btn-primary py-1.5 text-xs"
            :disabled="busyId === row.id"
            @click="renew(row)"
          >
            Renew (+plan days)
          </button>
          <button
            type="button"
            class="ui-btn-secondary py-1.5 text-xs"
            :disabled="busyId === row.id"
            @click="setEndDate(row)"
          >
            Set end date
          </button>
          <button
            type="button"
            class="ui-btn-secondary py-1.5 text-xs"
            :disabled="busyId === row.id"
            @click="changePlan(row)"
          >
            Change plan
          </button>
          <button
            v-if="row.status !== 'cancelled'"
            type="button"
            class="rounded-lg border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-800"
            :disabled="busyId === row.id"
            @click="cancelSub(row)"
          >
            Cancel plan
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

type SubRow = {
  id: string
  company_name: string
  owner_email: string | null
  status: string
  ends_at: string
  days_remaining: number
  is_expired: boolean
  plan: { id: string; key: string; name: string; duration_days: number } | null
}

const api = createApiClient()
const rows = ref<SubRow[]>([])
const loading = ref(true)
const error = ref('')
const msg = ref('')
const busyId = ref('')
const search = ref('')
const statusFilter = ref('')
let searchTimer: ReturnType<typeof setTimeout> | null = null

const filters = [
  { value: '', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'trialing', label: 'Trial' },
  { value: 'expired', label: 'Expired' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'ending', label: 'Ending ≤7d' },
]

function statusClass(s: string) {
  if (s === 'active' || s === 'trialing') return 'bg-emerald-50 text-emerald-700'
  if (s === 'expired' || s === 'past_due') return 'bg-amber-50 text-amber-800'
  if (s === 'cancelled') return 'bg-gray-100 text-gray-600'
  return 'bg-gray-100 text-gray-600'
}

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleDateString()
  } catch {
    return iso
  }
}

function setFilter(v: string) {
  statusFilter.value = v
  load()
}

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => load(), 250)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, string | number> = {}
    if (search.value.trim()) params.q = search.value.trim()
    if (statusFilter.value === 'ending') {
      params.ending_in = 7
    } else if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const { data } = await api.get<{ results: SubRow[] }>('/admin/subscriptions/', { params })
    rows.value = data.results
  } catch {
    error.value = 'Could not load subscriptions.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

async function renew(row: SubRow) {
  busyId.value = row.id
  msg.value = ''
  error.value = ''
  try {
    await api.post(`/admin/subscriptions/${row.id}/renew/`)
    msg.value = `Renewed ${row.company_name}.`
    await load()
  } catch {
    error.value = 'Renew failed.'
  } finally {
    busyId.value = ''
  }
}

async function cancelSub(row: SubRow) {
  if (!confirm('Cancel this plan? The user can still sign in until you disable the account.')) return
  busyId.value = row.id
  msg.value = ''
  try {
    await api.post(`/admin/subscriptions/${row.id}/cancel/`)
    msg.value = `Cancelled plan for ${row.company_name}.`
    await load()
  } catch {
    error.value = 'Cancel failed.'
  } finally {
    busyId.value = ''
  }
}

async function setEndDate(row: SubRow) {
  const raw = prompt('New end date (YYYY-MM-DD)', row.ends_at.slice(0, 10))
  if (!raw) return
  busyId.value = row.id
  msg.value = ''
  try {
    await api.post(`/admin/subscriptions/${row.id}/set-dates/`, {
      ends_at: `${raw}T23:59:59`,
    })
    msg.value = 'End date updated.'
    await load()
  } catch {
    error.value = 'Could not set end date.'
  } finally {
    busyId.value = ''
  }
}

async function changePlan(row: SubRow) {
  const key = prompt('Plan key (trial / monthly / yearly)', row.plan?.key || 'monthly')
  if (!key) return
  busyId.value = row.id
  msg.value = ''
  try {
    await api.post(`/admin/subscriptions/${row.id}/change-plan/`, { plan_key: key.trim() })
    msg.value = 'Plan changed.'
    await load()
  } catch {
    error.value = 'Could not change plan.'
  } finally {
    busyId.value = ''
  }
}

onMounted(load)
</script>

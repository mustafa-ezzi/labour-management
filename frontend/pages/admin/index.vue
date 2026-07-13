<template>
  <div>
    <!-- Global search -->
    <div class="mb-5">
      <input
        v-model="searchQ"
        type="search"
        class="ui-input"
        placeholder="Search users, workspaces, tickets…"
        @input="onSearch"
      />
      <div
        v-if="searchOpen"
        class="mt-2 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg"
      >
        <p v-if="searchLoading" class="px-4 py-3 text-xs text-gray-500">Searching…</p>
        <template v-else-if="hasSearchHits">
          <div v-if="search.users.length" class="border-b border-gray-100 px-3 py-2">
            <p class="px-1 text-[10px] font-bold uppercase tracking-wide text-gray-400">Users</p>
            <NuxtLink
              v-for="u in search.users"
              :key="u.id"
              :to="u.href"
              class="block rounded-lg px-2 py-2 text-sm hover:bg-violet-50"
              @click="searchOpen = false"
            >
              <span class="font-semibold text-gray-900">{{ u.email }}</span>
              <span v-if="u.name" class="text-gray-500"> · {{ u.name }}</span>
            </NuxtLink>
          </div>
          <div v-if="search.companies.length" class="border-b border-gray-100 px-3 py-2">
            <p class="px-1 text-[10px] font-bold uppercase tracking-wide text-gray-400">Workspaces</p>
            <NuxtLink
              v-for="c in search.companies"
              :key="c.id"
              :to="c.href"
              class="block rounded-lg px-2 py-2 text-sm hover:bg-violet-50"
              @click="searchOpen = false"
            >
              <span class="font-semibold text-gray-900">{{ c.name }}</span>
              <span class="text-gray-500"> · {{ c.owner_email }}</span>
            </NuxtLink>
          </div>
          <div v-if="search.tickets.length" class="px-3 py-2">
            <p class="px-1 text-[10px] font-bold uppercase tracking-wide text-gray-400">Tickets</p>
            <NuxtLink
              v-for="t in search.tickets"
              :key="t.id"
              :to="t.href"
              class="block rounded-lg px-2 py-2 text-sm hover:bg-violet-50"
              @click="searchOpen = false"
            >
              <span class="font-semibold text-gray-900">{{ t.subject }}</span>
              <span class="text-gray-500"> · {{ t.status }}</span>
            </NuxtLink>
          </div>
        </template>
        <p v-else class="px-4 py-3 text-xs text-gray-500">No matches.</p>
      </div>
    </div>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <template v-else-if="stats">
      <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
        <p class="text-sm text-gray-500">Whole-app overview</p>
        <div class="flex flex-wrap gap-2">
          <button type="button" class="ui-btn-secondary py-1.5 text-xs" @click="exportCsv('accounts')">
            Export accounts CSV
          </button>
          <button
            type="button"
            class="ui-btn-secondary py-1.5 text-xs"
            @click="exportCsv('subscriptions')"
          >
            Export subscriptions CSV
          </button>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div class="rounded-xl border border-violet-200 bg-violet-50 px-4 py-4">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-violet-600">Users</p>
          <p class="mt-1 text-2xl font-bold tabular-nums text-violet-900">{{ stats.total_users }}</p>
          <p class="mt-0.5 text-xs text-gray-500">{{ stats.active_users }} active</p>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white px-4 py-4">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Workspaces</p>
          <p class="mt-1 text-2xl font-bold tabular-nums text-gray-900">{{ stats.total_companies }}</p>
          <p class="mt-0.5 text-xs text-gray-500">{{ stats.disabled_users }} users disabled</p>
        </div>
        <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-4">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-emerald-700">Active plans</p>
          <p class="mt-1 text-2xl font-bold tabular-nums text-emerald-900">
            {{ stats.active_subscriptions }}
          </p>
          <p class="mt-0.5 text-xs text-gray-500">{{ stats.expiring_this_week }} ending ≤7d</p>
        </div>
        <div class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-4">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-amber-700">Est. MRR</p>
          <p class="mt-1 text-xl font-bold tabular-nums text-amber-900">
            {{ stats.mrr_currency }} {{ stats.estimated_mrr }}
          </p>
          <p class="mt-0.5 text-xs text-gray-500">
            {{ stats.open_support_tickets }} open tickets
            <span v-if="stats.unread_support_tickets">
              · {{ stats.unread_support_tickets }} unread
            </span>
          </p>
        </div>
      </div>

      <!-- Signups chart -->
      <UiCard class="mt-5">
        <p class="text-sm font-semibold text-gray-900">Signups (30 days)</p>
        <p class="mt-0.5 text-xs text-gray-500">New user accounts per day</p>
        <div class="mt-4 flex h-28 items-end gap-0.5 sm:gap-1">
          <div
            v-for="point in stats.signups_last_30_days"
            :key="point.date"
            class="min-w-0 flex-1 rounded-t bg-violet-500/80 transition-all hover:bg-violet-600"
            :style="{ height: barHeight(point.count) }"
            :title="`${point.date}: ${point.count}`"
          />
        </div>
        <div class="mt-2 flex justify-between text-[10px] text-gray-400">
          <span>{{ stats.signups_last_30_days[0]?.date }}</span>
          <span>{{ signupTotal }} total</span>
          <span>{{ stats.signups_last_30_days.at(-1)?.date }}</span>
        </div>
      </UiCard>

      <div class="mt-5 grid gap-4 lg:grid-cols-2">
        <!-- Expiring -->
        <UiCard>
          <div class="mb-3 flex items-center justify-between">
            <p class="text-sm font-semibold text-gray-900">Expiring soon</p>
            <NuxtLink to="/admin/subscriptions" class="ui-link text-xs">All →</NuxtLink>
          </div>
          <ul v-if="stats.expiring_soon?.length" class="divide-y divide-gray-100">
            <li
              v-for="row in stats.expiring_soon"
              :key="row.id"
              class="flex items-center justify-between gap-2 py-2 text-sm"
            >
              <div class="min-w-0">
                <p class="truncate font-medium text-gray-900">{{ row.company_name }}</p>
                <p class="truncate text-xs text-gray-500">{{ row.plan?.name }} · {{ row.status }}</p>
              </div>
              <p class="shrink-0 text-xs tabular-nums text-amber-700">
                {{ formatDate(row.ends_at) }}
              </p>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500">Nothing ending in the next 14 days.</p>
        </UiCard>

        <!-- Recent audit -->
        <UiCard>
          <div class="mb-3 flex items-center justify-between">
            <p class="text-sm font-semibold text-gray-900">Recent admin actions</p>
            <NuxtLink to="/admin/audit" class="ui-link text-xs">Audit →</NuxtLink>
          </div>
          <ul v-if="stats.recent_audit?.length" class="divide-y divide-gray-100">
            <li v-for="row in stats.recent_audit" :key="row.id" class="py-2">
              <p class="text-sm font-medium text-gray-900">{{ row.summary || row.action }}</p>
              <p class="text-[11px] text-gray-400">
                {{ row.actor_email || 'system' }} · {{ formatWhen(row.created_at) }}
              </p>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500">No actions yet.</p>
        </UiCard>
      </div>

      <!-- Open tickets -->
      <UiCard class="mt-5">
        <div class="mb-3 flex items-center justify-between">
          <p class="text-sm font-semibold text-gray-900">Open support</p>
          <NuxtLink to="/admin/support" class="ui-link text-xs">Inbox →</NuxtLink>
        </div>
        <ul v-if="stats.recent_tickets?.length" class="divide-y divide-gray-100">
          <li v-for="t in stats.recent_tickets" :key="t.id">
            <NuxtLink
              :to="`/admin/support/${t.id}`"
              class="flex items-center justify-between gap-2 py-2 hover:bg-violet-50/50"
            >
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-gray-900">
                  <span
                    v-if="t.admin_unread"
                    class="mr-1 inline-block h-2 w-2 rounded-full bg-violet-600"
                  />
                  {{ t.subject }}
                </p>
                <p class="truncate text-xs text-gray-500">{{ t.company?.name }}</p>
              </div>
              <span class="shrink-0 text-[10px] font-bold uppercase text-gray-400">{{ t.status }}</span>
            </NuxtLink>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500">No open tickets.</p>
      </UiCard>

      <div class="mt-5 flex flex-wrap gap-2">
        <NuxtLink to="/admin/accounts" class="ui-btn-primary py-2 text-xs">Accounts</NuxtLink>
        <NuxtLink to="/admin/subscriptions" class="ui-btn-secondary py-2 text-xs">Subscriptions</NuxtLink>
        <NuxtLink to="/admin/support" class="ui-btn-secondary py-2 text-xs">Support</NuxtLink>
        <NuxtLink to="/admin/plans" class="ui-btn-secondary py-2 text-xs">Plans</NuxtLink>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

type SignupPoint = { date: string; count: number }

type Dashboard = {
  total_users: number
  active_users: number
  disabled_users: number
  total_companies: number
  open_support_tickets: number
  unread_support_tickets: number
  active_subscriptions: number
  expired_subscriptions: number
  expiring_this_week: number
  estimated_mrr: string
  mrr_currency: string
  signups_last_30_days: SignupPoint[]
  expiring_soon: Array<{
    id: string
    company_name: string
    status: string
    ends_at: string
    plan: { name: string } | null
  }>
  recent_audit: Array<{
    id: string
    action: string
    summary: string
    created_at: string
    actor_email: string | null
  }>
  recent_tickets: Array<{
    id: string
    subject: string
    status: string
    admin_unread: boolean
    company: { name: string } | null
  }>
}

type SearchResult = {
  users: Array<{ id: string; email: string; name: string; href: string }>
  companies: Array<{ id: string; name: string; owner_email: string | null; href: string }>
  tickets: Array<{ id: string; subject: string; status: string; href: string }>
}

const api = createApiClient()

const stats = ref<Dashboard | null>(null)
const loading = ref(true)
const error = ref('')

const searchQ = ref('')
const searchOpen = ref(false)
const searchLoading = ref(false)
const search = ref<SearchResult>({ users: [], companies: [], tickets: [] })
let searchTimer: ReturnType<typeof setTimeout> | null = null

const hasSearchHits = computed(
  () =>
    search.value.users.length + search.value.companies.length + search.value.tickets.length > 0,
)

const signupTotal = computed(() =>
  (stats.value?.signups_last_30_days || []).reduce((a, p) => a + p.count, 0),
)

const maxSignup = computed(() =>
  Math.max(1, ...(stats.value?.signups_last_30_days || []).map((p) => p.count)),
)

function barHeight(count: number) {
  const pct = Math.round((count / maxSignup.value) * 100)
  return `${Math.max(count > 0 ? 8 : 2, pct)}%`
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString()
  } catch {
    return iso
  }
}

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  const q = searchQ.value.trim()
  if (q.length < 2) {
    searchOpen.value = false
    return
  }
  searchTimer = setTimeout(async () => {
    searchLoading.value = true
    searchOpen.value = true
    try {
      const { data } = await api.get<SearchResult>('/admin/search/', { params: { q } })
      search.value = data
    } catch {
      search.value = { users: [], companies: [], tickets: [] }
    } finally {
      searchLoading.value = false
    }
  }, 250)
}

async function exportCsv(kind: 'accounts' | 'subscriptions') {
  const path =
    kind === 'accounts' ? '/admin/exports/accounts/' : '/admin/exports/subscriptions/'
  try {
    const { data } = await api.get(path, { responseType: 'blob' })
    const url = URL.createObjectURL(data as Blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${kind}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    error.value = `Could not export ${kind}.`
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get<Dashboard>('/admin/dashboard/')
    stats.value = data
  } catch {
    error.value = 'Could not load admin dashboard. Confirm you signed in as App Admin.'
  } finally {
    loading.value = false
  }
})
</script>

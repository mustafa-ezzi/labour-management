<template>
  <div>
    <p class="mb-4 text-sm text-gray-500">
      Inbox for user tickets. Reply here; renew plans from Subscriptions if needed.
    </p>

    <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
      <input
        v-model="search"
        type="search"
        class="ui-input flex-1"
        placeholder="Search subject, workspace, email…"
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

    <p v-if="meta" class="mb-3 text-xs text-gray-500">
      {{ meta.open_count }} open/pending · {{ meta.unread_count }} unread
    </p>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <UiCard v-else-if="!rows.length" class="text-center text-sm text-gray-600">
      No tickets.
    </UiCard>

    <ul v-else class="divide-y divide-gray-100 overflow-hidden rounded-xl border border-gray-200 bg-white">
      <li v-for="row in rows" :key="row.id">
        <NuxtLink
          :to="`/admin/support/${row.id}`"
          class="flex items-start gap-3 px-4 py-3 hover:bg-violet-50/50"
        >
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-gray-900">
              <span
                v-if="row.admin_unread"
                class="mr-1 inline-block h-2 w-2 rounded-full bg-violet-600"
              />
              {{ row.subject }}
            </p>
            <p class="mt-0.5 truncate text-xs text-gray-500">
              {{ row.company?.name }} · {{ row.created_by?.email }}
            </p>
          </div>
          <div class="shrink-0 text-right">
            <span
              class="rounded px-2 py-0.5 text-[10px] font-bold uppercase"
              :class="statusClass(row.status)"
            >
              {{ row.status }}
            </span>
            <p class="mt-1 text-[10px] text-gray-400">{{ formatWhen(row.updated_at) }}</p>
          </div>
        </NuxtLink>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

type TicketRow = {
  id: string
  subject: string
  status: string
  admin_unread: boolean
  updated_at: string
  company: { id: string; name: string } | null
  created_by: { email: string | null } | null
}

const api = createApiClient()
const rows = ref<TicketRow[]>([])
const meta = ref<{ open_count: number; unread_count: number } | null>(null)
const loading = ref(true)
const error = ref('')
const search = ref('')
const statusFilter = ref('openish')
let searchTimer: ReturnType<typeof setTimeout> | null = null

const filters = [
  { value: 'openish', label: 'Open' },
  { value: '', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
]

function statusClass(s: string) {
  if (s === 'open') return 'bg-violet-50 text-violet-700'
  if (s === 'pending') return 'bg-amber-50 text-amber-800'
  if (s === 'resolved') return 'bg-emerald-50 text-emerald-700'
  return 'bg-gray-100 text-gray-600'
}

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString()
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
    const params: Record<string, string> = {}
    if (search.value.trim()) params.q = search.value.trim()
    if (statusFilter.value) params.status = statusFilter.value
    const { data } = await api.get<{
      results: TicketRow[]
      open_count: number
      unread_count: number
    }>('/admin/support/tickets/', { params })
    rows.value = data.results
    meta.value = { open_count: data.open_count, unread_count: data.unread_count }
  } catch {
    error.value = 'Could not load support inbox.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

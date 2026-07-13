<template>
  <div>
    <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex-1">
        <input
          v-model="search"
          type="search"
          class="ui-input"
          placeholder="Search email, name, workspace…"
          @input="onSearch"
        />
      </div>
      <div class="flex gap-2">
        <button
          type="button"
          class="rounded-lg px-3 py-2 text-xs font-semibold"
          :class="statusFilter === '' ? 'bg-violet-700 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          @click="setStatus('')"
        >
          All
        </button>
        <button
          type="button"
          class="rounded-lg px-3 py-2 text-xs font-semibold"
          :class="statusFilter === 'active' ? 'bg-violet-700 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          @click="setStatus('active')"
        >
          Active
        </button>
        <button
          type="button"
          class="rounded-lg px-3 py-2 text-xs font-semibold"
          :class="statusFilter === 'disabled' ? 'bg-violet-700 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          @click="setStatus('disabled')"
        >
          Disabled
        </button>
      </div>
    </div>

    <p v-if="loading" class="ui-muted">Loading accounts…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <UiCard v-else-if="!rows.length" class="text-center text-sm text-gray-600">
      No accounts found.
    </UiCard>
    <ul v-else class="divide-y divide-gray-100 overflow-hidden rounded-xl border border-gray-200 bg-white">
      <li v-for="row in rows" :key="row.id">
        <NuxtLink
          :to="`/admin/accounts/${row.id}`"
          class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-violet-50/50"
        >
          <span
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold uppercase"
            :class="row.is_active ? 'bg-violet-600 text-white' : 'bg-gray-200 text-gray-500'"
          >
            {{ (row.first_name || row.email || '?').slice(0, 1) }}
          </span>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-gray-900">
              {{ displayName(row) }}
            </p>
            <p class="truncate text-xs text-gray-500">
              {{ row.email }}
              <span v-if="row.company"> · {{ row.company.name }}</span>
            </p>
          </div>
          <div class="shrink-0 text-right">
            <span
              class="inline-block rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide"
              :class="
                row.is_active
                  ? 'bg-emerald-50 text-emerald-700'
                  : 'bg-amber-50 text-amber-700'
              "
            >
              {{ row.status }}
            </span>
            <p class="mt-1 text-[10px] text-gray-400">{{ row.subscription_plan }}</p>
          </div>
        </NuxtLink>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

type AccountRow = {
  id: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  status: string
  subscription_plan: string
  company: { id: string; name: string } | null
}

const api = createApiClient()
const rows = ref<AccountRow[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const statusFilter = ref('')
let searchTimer: ReturnType<typeof setTimeout> | null = null

function displayName(row: AccountRow) {
  const n = `${row.first_name || ''} ${row.last_name || ''}`.trim()
  return n || row.email
}

function setStatus(s: string) {
  statusFilter.value = s
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
    const { data } = await api.get<{ results: AccountRow[] }>('/admin/accounts/', {
      params: {
        q: search.value.trim() || undefined,
        status: statusFilter.value || undefined,
      },
    })
    rows.value = data.results
  } catch {
    error.value = 'Could not load accounts.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

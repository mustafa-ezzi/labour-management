<template>
  <div>
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <UiPageHeader title="Support" subtitle="Message LabourPro Admin" />
      <NuxtLink to="/support/new" class="ui-btn-primary py-2 text-xs">New ticket</NuxtLink>
    </div>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <UiCard v-else-if="!rows.length" class="text-center text-sm text-gray-600">
      No tickets yet.
      <NuxtLink to="/support/new" class="ui-link mt-2 block">Open your first ticket</NuxtLink>
    </UiCard>

    <ul v-else class="divide-y divide-gray-100 overflow-hidden rounded-xl border border-gray-200 bg-white">
      <li v-for="row in rows" :key="row.id">
        <NuxtLink
          :to="`/support/${row.id}`"
          class="flex items-start gap-3 px-4 py-3 transition-colors hover:bg-violet-50/50"
        >
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-gray-900">
              <span v-if="row.user_unread" class="mr-1 inline-block h-2 w-2 rounded-full bg-violet-600" />
              {{ row.subject }}
            </p>
            <p class="mt-0.5 text-xs text-gray-500">
              {{ formatWhen(row.updated_at) }}
              <span v-if="row.message_count"> · {{ row.message_count }} messages</span>
            </p>
          </div>
          <span
            class="shrink-0 rounded px-2 py-0.5 text-[10px] font-bold uppercase"
            :class="statusClass(row.status)"
          >
            {{ row.status }}
          </span>
        </NuxtLink>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

type TicketRow = {
  id: string
  subject: string
  status: string
  updated_at: string
  user_unread: boolean
  message_count: number | null
}

const api = createApiClient()
const rows = ref<TicketRow[]>([])
const loading = ref(true)
const error = ref('')

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

onMounted(async () => {
  try {
    const { data } = await api.get<{ results: TicketRow[] }>('/support/tickets/')
    rows.value = data.results
  } catch {
    error.value = 'Could not load support tickets.'
  } finally {
    loading.value = false
  }
})
</script>

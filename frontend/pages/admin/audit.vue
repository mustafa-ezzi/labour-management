<template>
  <div>
    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <UiCard v-else-if="!rows.length" class="text-center text-sm text-gray-600">
      No admin actions logged yet.
    </UiCard>
    <ul v-else class="overflow-hidden rounded-xl border border-gray-200 bg-white divide-y divide-gray-100">
      <li v-for="row in rows" :key="row.id" class="px-4 py-3">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="text-sm font-semibold text-gray-900">{{ row.action }}</p>
            <p class="mt-0.5 text-xs text-gray-500">{{ row.summary || '—' }}</p>
            <p class="mt-0.5 text-[11px] text-gray-400">{{ row.actor_email || 'system' }}</p>
          </div>
          <p class="shrink-0 text-[11px] tabular-nums text-gray-400">
            {{ formatWhen(row.created_at) }}
          </p>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

type AuditRow = {
  id: string
  action: string
  summary: string
  actor_email: string | null
  created_at: string
}

const api = createApiClient()
const rows = ref<AuditRow[]>([])
const loading = ref(true)
const error = ref('')

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get<{ results: AuditRow[] }>('/admin/audit/')
    rows.value = data.results
  } catch {
    error.value = 'Could not load audit log.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <UiPageHeader title="Workers" subtitle="Active and inactive labour on this site">
      <template #action>
        <NuxtLink :to="`/sites/${siteId}/crew/new`" data-tour="crew-add-btn" class="ui-btn-primary">Add worker</NuxtLink>
      </template>
    </UiPageHeader>

    <div class="mb-5 grid grid-cols-2 gap-3">
      <NuxtLink
        :to="`/sites/${siteId}/crew/wages`"
        class="flex items-center gap-3 rounded-xl border border-violet-200 bg-violet-50 px-4 py-3 transition-all hover:border-violet-300 hover:bg-violet-100"
      >
        <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-violet-600 text-white shadow-md">
          <AppNavIcon name="wages" class="h-5 w-5" />
        </span>
        <div class="min-w-0 flex-1">
          <p class="text-sm font-semibold text-gray-900">Daily Wages</p>
          <p class="text-[11px] text-gray-500">Attendance + pay</p>
        </div>
      </NuxtLink>
      <NuxtLink
        :to="`/sites/${siteId}/crew/history`"
        class="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3 transition-all hover:border-violet-200 hover:bg-violet-50/50"
      >
        <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-violet-100 text-violet-700">
          <AppNavIcon name="attendance" class="h-5 w-5" />
        </span>
        <div class="min-w-0 flex-1">
          <p class="text-sm font-semibold text-gray-900">History</p>
          <p class="text-[11px] text-gray-500">Present days calendar</p>
        </div>
      </NuxtLink>
    </div>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <ul v-else-if="labours.length" class="divide-y divide-gray-100 overflow-hidden rounded-xl border border-gray-200 bg-white">
      <li v-for="l in labours" :key="l.id">
        <NuxtLink
          :to="`/sites/${siteId}/crew/${l.id}`"
          class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-violet-50/40"
        >
          <span
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold uppercase"
            :class="
              l.status === 'active'
                ? 'bg-violet-600 text-white'
                : 'border border-gray-300 text-gray-400'
            "
          >
            {{ l.name.slice(0, 1) }}
          </span>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-gray-900">{{ l.name }}</p>
            <p class="ui-muted mt-0.5 text-xs">
              {{ l.daily_wage }}/day ·
              <span
                :class="
                  l.status === 'active' ? 'text-violet-700' : 'text-amber-600'
                "
              >
                {{ l.status }}
              </span>
            </p>
          </div>
          <div class="shrink-0 text-right">
            <p class="text-[10px] uppercase tracking-wide text-gray-400">
              {{ parseFloat(l.pending_wage) > 0 ? 'Due' : 'Settled' }}
            </p>
            <p
              class="text-sm font-bold tabular-nums"
              :class="parseFloat(l.pending_wage) > 0 ? 'text-amber-600' : 'text-emerald-600'"
            >
              {{ l.pending_wage }}
            </p>
          </div>
        </NuxtLink>
      </li>
    </ul>
    <UiCard v-else class="text-center">
      <p class="text-gray-600">No workers on this site yet</p>
      <NuxtLink :to="`/sites/${siteId}/crew/new`" class="ui-btn-primary mt-4 inline-flex">Add worker</NuxtLink>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
type LabourRow = {
  id: string
  name: string
  daily_wage: string
  status: string
  pending_wage: string
}

const route = useRoute()
const siteId = computed(() => String(route.params.siteId || ''))
const api = createApiClient()
const labours = ref<LabourRow[]>([])
const loading = ref(false)
const error = ref('')

async function loadLabour() {
  error.value = ''
  loading.value = true
  labours.value = []
  try {
    const { data } = await api.get('/labours/', { params: { site_id: siteId.value } })
    labours.value = unwrapResults<LabourRow>(data)
  } catch {
    error.value = 'Could not load workers.'
  } finally {
    loading.value = false
  }
}

watch(siteId, loadLabour, { immediate: true })
</script>

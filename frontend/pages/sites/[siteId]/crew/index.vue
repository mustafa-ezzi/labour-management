<template>
  <div>
    <UiPageHeader title="Workers" subtitle="Active and inactive labour on this site">
      <template #action>
        <NuxtLink :to="`/sites/${siteId}/crew/new`" class="ui-btn-primary">Add worker</NuxtLink>
      </template>
    </UiPageHeader>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-400">{{ error }}</p>
    <ul v-else-if="labours.length" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <li v-for="l in labours" :key="l.id">
        <NuxtLink
          :to="`/sites/${siteId}/crew/${l.id}`"
          class="ui-card-hover flex h-full items-center justify-between gap-3"
        >
          <div class="min-w-0">
            <p class="truncate font-medium text-white lg:text-gray-900">{{ l.name }}</p>
            <p class="ui-muted mt-0.5">
              {{ l.daily_wage }} / day ·
              <span
                :class="
                  l.status === 'active' ? 'text-green-400 lg:text-green-700' : 'text-amber-400 lg:text-amber-600'
                "
              >
                {{ l.status }}
              </span>
            </p>
          </div>
          <div class="shrink-0 text-right">
            <p class="text-[10px] uppercase tracking-wide text-white/35 lg:text-gray-400">Due</p>
            <p class="text-sm font-bold tabular-nums text-amber-300 lg:text-amber-600">{{ l.pending_wage }}</p>
          </div>
        </NuxtLink>
      </li>
    </ul>
    <UiCard v-else class="text-center">
      <p class="text-white/70 lg:text-gray-600">No workers on this site yet</p>
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

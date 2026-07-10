<template>
  <div>
    <UiPageHeader title="Sites" subtitle="Construction projects and locations">
      <template #action>
        <NuxtLink to="/sites/new" class="ui-btn-primary">Add site</NuxtLink>
      </template>
    </UiPageHeader>

    <NuxtLink
      v-if="resumePath"
      :to="resumePath"
      class="ui-card-hover mb-5 block px-4 py-3"
    >
      <p class="text-xs font-semibold uppercase tracking-widest text-violet-700">Continue</p>
      <p class="mt-1 text-sm font-medium text-gray-900">Open last active site →</p>
    </NuxtLink>

    <p v-if="pending" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <ul v-else-if="sites.length" class="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <li v-for="s in sites" :key="s.id">
        <NuxtLink :to="`/sites/${s.id}`" class="ui-list-row">
          <span class="ui-icon-chip h-9 w-9">
            <AppNavIcon name="site" class="h-4 w-4" />
          </span>
          <div class="min-w-0 flex-1">
            <p class="font-semibold text-gray-900">{{ s.name }}</p>
            <p v-if="s.location" class="ui-muted mt-0.5 truncate text-xs">{{ s.location }}</p>
            <p class="mt-0.5 text-xs text-gray-400">{{ s.from_date }} → {{ s.to_date }}</p>
          </div>
          <div class="shrink-0 text-right">
            <p class="text-[10px] uppercase tracking-wide text-gray-400">Days</p>
            <p class="text-sm font-bold text-violet-700">{{ s.total_work_days }}</p>
          </div>
        </NuxtLink>
      </li>
    </ul>
    <UiCard v-else class="text-center">
      <p class="text-gray-600">No sites yet</p>
      <p class="ui-muted mt-1">Create your first site to add crew and attendance.</p>
      <NuxtLink to="/sites/new" class="ui-btn-primary mt-4 inline-flex">Add site</NuxtLink>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

type Site = {
  id: string
  name: string
  from_date: string
  to_date: string
  location: string
  total_work_days: number
}

const resumePath = useResumeSitePath()


const api = createApiClient()
const sites = ref<Site[]>([])
const pending = ref(true)
const error = ref('')

async function load() {
  pending.value = true
  error.value = ''
  try {
    const { data } = await api.get<{ results?: Site[] } | Site[]>('/sites/')
    sites.value = Array.isArray(data) ? data : data.results ?? []
  } catch {
    error.value = 'Could not load sites.'
  } finally {
    pending.value = false
  }
}

onMounted(load)
</script>

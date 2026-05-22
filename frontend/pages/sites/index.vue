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
      <p class="text-xs font-semibold uppercase tracking-widest text-green-400/80 lg:text-green-700">Continue</p>
      <p class="mt-1 text-sm font-medium text-white lg:text-gray-900">Open last active site →</p>
    </NuxtLink>

    <p v-if="pending" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-400">{{ error }}</p>
    <ul v-else-if="sites.length" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <li v-for="s in sites" :key="s.id">
        <NuxtLink :to="`/sites/${s.id}`" class="ui-card-hover block h-full">
          <p class="font-medium text-white lg:text-gray-900">{{ s.name }}</p>
          <p v-if="s.location" class="ui-muted mt-1 truncate">{{ s.location }}</p>
          <p class="mt-2 text-xs text-white/35 lg:text-gray-400">{{ s.from_date }} → {{ s.to_date }}</p>
          <p class="mt-1 text-xs font-medium text-green-400/70 lg:text-green-700">{{ s.total_work_days }} calendar days</p>
          <p class="mt-2 text-[10px] font-semibold uppercase text-white/30 lg:text-gray-400">Open site workspace →</p>
        </NuxtLink>
      </li>
    </ul>
    <UiCard v-else class="text-center">
      <p class="text-white/70">No sites yet</p>
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

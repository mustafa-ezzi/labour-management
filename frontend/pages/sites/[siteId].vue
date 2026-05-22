<template>
  <div>
    <header class="mb-4 border-b border-white/10 pb-3 lg:mb-5">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div class="min-w-0">
          <NuxtLink to="/sites" class="ui-link text-xs">← All sites</NuxtLink>
          <h1 class="ui-page-title mt-1 truncate">{{ heading }}</h1>
          <p class="ui-muted mt-0.5 text-xs">All crew, attendance, pay, and materials below are for this site only.</p>
        </div>
        <nav class="flex flex-wrap gap-2 shrink-0" aria-label="Site sections">
          <NuxtLink
            v-for="l in siteSectionLinks"
            :key="l.to"
            :to="l.to"
            class="rounded-lg border border-white/15 px-3 py-2 text-xs font-semibold text-white/75 transition-colors hover:border-green-400/40 hover:bg-white/5 lg:border-gray-300 lg:text-gray-700 lg:hover:bg-gray-100"
            active-class="!border-green-500/50 !bg-green-500/10 !text-green-200 lg:!border-green-400 lg:!bg-green-50 lg:!text-green-800"
          >
            {{ l.label }}
          </NuxtLink>
        </nav>
      </div>
    </header>
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const route = useRoute()
const api = createApiClient()

const siteId = computed(() => String(route.params.siteId || ''))
const heading = ref('Site')

const siteSectionLinks = computed(() => {
  const id = siteId.value
  return [
    { to: `/sites/${id}`, label: 'Overview' },
    { to: `/sites/${id}/crew`, label: 'Crew' },
    { to: `/sites/${id}/materials`, label: 'Materials' },
  ]
})

async function loadSiteName() {
  if (!siteId.value) {
    return
  }
  persistSiteId(siteId.value)
  try {
    const { data } = await api.get<{ name: string }>(`/sites/${siteId.value}/`)
    heading.value = data.name
  } catch {
    heading.value = 'Site'
  }
}

watch(siteId, loadSiteName, { immediate: true })
</script>

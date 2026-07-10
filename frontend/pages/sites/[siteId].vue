<template>
  <div>
    <header class="mb-5 flex items-center gap-3 border-b border-gray-200 pb-3">
      <NuxtLink
        to="/sites"
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-800"
        aria-label="All sites"
      >
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </NuxtLink>
      <div class="min-w-0">
        <p class="text-[10px] font-semibold uppercase tracking-widest text-gray-400">Site</p>
        <h1 class="truncate text-lg font-bold leading-tight text-gray-900">
          {{ heading }}
        </h1>
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

async function loadSiteName() {
  if (!siteId.value) return
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

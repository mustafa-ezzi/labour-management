<template>
  <div>
    <p v-if="pending" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-400">{{ error }}</p>
    <div v-else-if="site" class="space-y-5">
      <UiCard class="text-sm space-y-2">
        <p v-if="site.location">
          <span class="text-white/40 lg:text-gray-500">Location</span>
          <span class="ml-2 text-white/80 lg:text-gray-800">{{ site.location }}</span>
        </p>
        <p>
          <span class="text-white/40 lg:text-gray-500">Duration</span>
          <span class="ml-2 text-white/80 lg:text-gray-800">{{ site.from_date }} → {{ site.to_date }}</span>
        </p>
        <p>
          <span class="text-white/40 lg:text-gray-500">Calendar days</span>
          <span class="ml-2 font-semibold text-green-300 lg:text-green-700">{{ site.total_work_days }}</span>
        </p>
      </UiCard>

      <div>
        <h2 class="ui-label mb-3">Go to</h2>
        <div class="grid gap-3 sm:grid-cols-2">
          <NuxtLink :to="`/sites/${siteId}/crew`" class="ui-card-hover block p-4">
            <p class="font-semibold text-white lg:text-gray-900">Crew</p>
            <p class="ui-muted mt-1">Workers, attendance, wage payments</p>
          </NuxtLink>
          <NuxtLink :to="`/sites/${siteId}/materials`" class="ui-card-hover block p-4">
            <p class="font-semibold text-white lg:text-gray-900">Materials</p>
            <p class="ui-muted mt-1">Stock definitions &amp; daily usage</p>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
type Site = {
  id: string
  name: string
  location: string
  from_date: string
  to_date: string
  total_work_days: number
}

const route = useRoute()
const siteId = computed(() => String(route.params.siteId || ''))
const api = createApiClient()
const site = ref<Site | null>(null)
const pending = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get<Site>(`/sites/${siteId.value}/`)
    site.value = data
  } catch {
    error.value = 'Site not found.'
  } finally {
    pending.value = false
  }
})
</script>

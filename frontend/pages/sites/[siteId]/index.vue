<template>
  <div>
    <p v-if="pending" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <div v-else-if="site" class="space-y-6">
      <p v-if="siteMeta" class="text-xs text-gray-500">{{ siteMeta }}</p>

      <!-- Row 1: Workers + Materials -->
      <div class="grid grid-cols-2 gap-4">
        <NuxtLink
          :to="`/sites/${siteId}/crew`"
          class="flex flex-col items-center gap-2 rounded-xl border border-gray-200 bg-white py-5 transition-colors hover:border-violet-200 hover:bg-violet-50/50"
        >
          <span class="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100 text-violet-700">
            <AppNavIcon name="crew" class="h-7 w-7" />
          </span>
          <span class="text-sm font-semibold text-gray-900">Workers</span>
        </NuxtLink>
        <NuxtLink
          :to="`/sites/${siteId}/materials`"
          class="flex flex-col items-center gap-2 rounded-xl border border-gray-200 bg-white py-5 transition-colors hover:border-violet-200 hover:bg-violet-50/50"
        >
          <span class="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100 text-violet-700">
            <AppNavIcon name="materials" class="h-7 w-7" />
          </span>
          <span class="text-sm font-semibold text-gray-900">Materials</span>
        </NuxtLink>
      </div>

      <!-- Row 2: Daily wages + Log usage -->
      <div class="grid grid-cols-2 gap-4">
        <NuxtLink
          :to="`/sites/${siteId}/crew/wages`"
          class="flex flex-col items-center gap-2 rounded-xl border border-violet-200 bg-violet-50 py-5 transition-colors hover:border-violet-300 hover:bg-violet-100/60"
        >
          <span class="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-600 text-white shadow-md shadow-violet-700/25">
            <AppNavIcon name="wages" class="h-7 w-7" />
          </span>
          <span class="text-center text-sm font-semibold leading-tight text-gray-900">Daily wages</span>
          <span class="text-[11px] text-gray-500">Attendance + pay</span>
        </NuxtLink>
        <NuxtLink
          :to="`/sites/${siteId}/materials/usage`"
          class="flex flex-col items-center gap-2 rounded-xl border border-gray-200 bg-white py-5 transition-colors hover:border-violet-200 hover:bg-violet-50/50"
        >
          <span class="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100 text-violet-700">
            <AppNavIcon name="log" class="h-7 w-7" />
          </span>
          <span class="text-center text-sm font-semibold leading-tight text-gray-900">Log usage</span>
          <span class="text-[11px] text-gray-500">Materials used today</span>
        </NuxtLink>
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
  to_date: string | null
  total_work_days: number
}

const route = useRoute()
const siteId = computed(() => String(route.params.siteId || ''))
const api = createApiClient()
const site = ref<Site | null>(null)
const pending = ref(true)
const error = ref('')

const siteMeta = computed(() => {
  if (!site.value) return ''
  const parts: string[] = []
  if (site.value.location) parts.push(site.value.location)
  parts.push(`Started ${site.value.from_date}`)
  parts.push(`${site.value.total_work_days} days`)
  return parts.join(' · ')
})

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

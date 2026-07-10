<template>
  <div>
    <p v-if="pending" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <div v-else-if="site" class="space-y-6">
      <p v-if="siteMeta" class="text-xs text-gray-500">
        {{ siteMeta }}
      </p>

      <div>
        <h2 class="ui-label mb-3">Today’s tasks</h2>
        <div class="grid gap-3 sm:grid-cols-3">
          <NuxtLink
            v-for="t in tasks"
            :key="t.to"
            :to="t.to"
            class="group flex flex-col gap-3 rounded-xl border border-violet-500/20 bg-violet-50 p-4 transition-all hover:border-violet-400/50 hover:bg-violet-500/[0.12] border-violet-200 bg-violet-50 hover:border-violet-300 hover:bg-violet-100"
          >
            <span
              class="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-600 text-white shadow-md"
              style="box-shadow: 0 2px 12px rgba(124,58,237,0.4)"
            >
              <AppNavIcon :name="t.icon" class="h-5 w-5" />
            </span>
            <div>
              <p class="font-semibold text-gray-900">{{ t.label }}</p>
              <p class="ui-muted mt-0.5 text-xs">{{ t.desc }}</p>
            </div>
          </NuxtLink>
        </div>
      </div>

      <div>
        <h2 class="ui-label mb-3">Browse</h2>
        <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
          <NuxtLink :to="`/sites/${siteId}/crew`" class="ui-list-row">
            <span class="ui-icon-chip h-9 w-9">
              <AppNavIcon name="crew" class="h-4 w-4" />
            </span>
            <div class="min-w-0 flex-1">
              <p class="font-medium text-gray-900">Workers</p>
              <p class="ui-muted text-xs">Roster, wages, payment history</p>
            </div>
            <AppNavIcon name="chevron-down" class="h-4 w-4 shrink-0 -rotate-90 text-gray-400" />
          </NuxtLink>
          <NuxtLink :to="`/sites/${siteId}/materials`" class="ui-list-row">
            <span class="ui-icon-chip h-9 w-9">
              <AppNavIcon name="materials" class="h-4 w-4" />
            </span>
            <div class="min-w-0 flex-1">
              <p class="font-medium text-gray-900">Materials</p>
              <p class="ui-muted text-xs">Definitions and total costs</p>
            </div>
            <AppNavIcon name="chevron-down" class="h-4 w-4 shrink-0 -rotate-90 text-gray-400" />
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

const siteMeta = computed(() => {
  if (!site.value) return ''
  const parts: string[] = []
  if (site.value.location) parts.push(site.value.location)
  parts.push(`${site.value.from_date} → ${site.value.to_date}`)
  parts.push(`${site.value.total_work_days} days`)
  return parts.join(' · ')
})

const tasks = computed(() => [
  {
    to: `/sites/${siteId.value}/crew/wages`,
    label: 'Daily wages',
    desc: 'Attendance + pay, one page',
    icon: 'wages',
  },
  {
    to: `/sites/${siteId.value}/materials/usage`,
    label: 'Log usage',
    desc: 'Record materials used',
    icon: 'log',
  },
  {
    to: `/sites/${siteId.value}/materials/pay`,
    label: 'Pay materials',
    desc: 'Settle usage costs',
    icon: 'pay',
  },
])

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

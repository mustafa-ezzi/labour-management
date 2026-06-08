<template>
  <div>
    <p v-if="pending" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-400">{{ error }}</p>
    <div v-else-if="site" class="space-y-6">
      <p v-if="siteMeta" class="text-xs text-white/45 lg:text-gray-500">
        {{ siteMeta }}
      </p>

      <div>
        <h2 class="ui-label mb-3">Today’s tasks</h2>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <NuxtLink
            v-for="t in tasks"
            :key="t.to"
            :to="t.to"
            class="group flex flex-col gap-3 rounded-xl border border-green-500/20 bg-green-500/[0.07] p-4 transition-all hover:border-green-400/50 hover:bg-green-500/[0.12] lg:border-green-200 lg:bg-green-50 lg:hover:border-green-400 lg:hover:bg-green-100"
          >
            <span
              class="flex h-10 w-10 items-center justify-center rounded-lg bg-green-600 text-white shadow-md"
              style="box-shadow: 0 2px 12px rgba(22,163,74,0.4)"
            >
              <AppNavIcon :name="t.icon" class="h-5 w-5" />
            </span>
            <div>
              <p class="font-semibold text-white lg:text-gray-900">{{ t.label }}</p>
              <p class="ui-muted mt-0.5 text-xs">{{ t.desc }}</p>
            </div>
          </NuxtLink>
        </div>
      </div>

      <div>
        <h2 class="ui-label mb-3">Browse</h2>
        <div class="grid gap-3 sm:grid-cols-2">
          <NuxtLink
            :to="`/sites/${siteId}/crew`"
            class="ui-card-hover flex items-center gap-3 p-4"
          >
            <AppNavIcon name="crew" class="h-5 w-5 text-white/55 lg:text-gray-500" />
            <div>
              <p class="font-medium text-white lg:text-gray-900">Workers</p>
              <p class="ui-muted text-xs">Roster, wages, payment history</p>
            </div>
          </NuxtLink>
          <NuxtLink
            :to="`/sites/${siteId}/materials`"
            class="ui-card-hover flex items-center gap-3 p-4"
          >
            <AppNavIcon name="materials" class="h-5 w-5 text-white/55 lg:text-gray-500" />
            <div>
              <p class="font-medium text-white lg:text-gray-900">Materials</p>
              <p class="ui-muted text-xs">Definitions and total costs</p>
            </div>
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
    to: `/sites/${siteId.value}/crew/attendance`,
    label: 'Mark attendance',
    desc: "Today's roster",
    icon: 'attendance',
  },
  {
    to: `/sites/${siteId.value}/crew/pay`,
    label: 'Pay crew',
    desc: 'Settle pending wages',
    icon: 'pay',
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

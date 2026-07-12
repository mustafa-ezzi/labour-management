<template>
  <div>
    <p v-if="pending" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <div v-else-if="site" class="space-y-5">
      <p v-if="siteMeta" class="text-xs text-gray-500">{{ siteMeta }}</p>

      <!-- Summary stats -->
      <div class="grid grid-cols-2 gap-3">
        <div class="rounded-xl border border-violet-200 bg-violet-50 px-3 py-3">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-violet-600">Workers</p>
          <p class="mt-0.5 text-xl font-bold tabular-nums text-violet-900">{{ workerCount }}</p>
          <p class="mt-0.5 text-[11px] text-gray-500">{{ activeWorkerCount }} active</p>
        </div>
        <div class="rounded-xl border border-amber-200 bg-amber-50 px-3 py-3">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-amber-700">Wages due</p>
          <p class="mt-0.5 text-xl font-bold tabular-nums text-amber-900">{{ formatAmount(pendingWages) }}</p>
          <p class="mt-0.5 text-[11px] text-gray-500">Outstanding to crew</p>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white px-3 py-3">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Materials</p>
          <p class="mt-0.5 text-xl font-bold tabular-nums text-gray-900">{{ materialCount }}</p>
          <p class="mt-0.5 text-[11px] text-gray-500">
            Due {{ formatAmount(pendingMaterials) }}
          </p>
        </div>
        <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-3">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-emerald-700">Today</p>
          <p class="mt-0.5 text-xl font-bold tabular-nums text-emerald-900">{{ presentToday }} present</p>
          <p class="mt-0.5 text-[11px] text-gray-500">
            Earned {{ formatAmount(earnedToday) }} · Paid {{ formatAmount(paidToday) }}
          </p>
        </div>
      </div>

      <!-- Quick actions -->
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

      <!-- Shortcuts -->
      <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
        <NuxtLink
          :to="`/sites/${siteId}/crew/history`"
          class="flex items-center gap-3 border-b border-gray-100 px-4 py-3 transition-colors hover:bg-violet-50/40"
        >
          <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-violet-100 text-violet-700">
            <AppNavIcon name="attendance" class="h-4 w-4" />
          </span>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-semibold text-gray-900">Attendance history</p>
            <p class="text-[11px] text-gray-500">Calendar of present days per worker</p>
          </div>
          <span class="text-gray-300">›</span>
        </NuxtLink>
        <NuxtLink
          :to="`/sites/${siteId}/materials/pay`"
          class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-violet-50/40"
        >
          <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-100 text-amber-700">
            <AppNavIcon name="pay" class="h-4 w-4" />
          </span>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-semibold text-gray-900">Pay materials</p>
            <p class="text-[11px] text-gray-500">
              {{ parseAmount(pendingMaterials) > 0 ? `${formatAmount(pendingMaterials)} pending` : 'All settled' }}
            </p>
          </div>
          <span class="text-gray-300">›</span>
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

type LabourRow = { id: string; status: string; pending_wage: string }
type MaterialRow = { id: string; pending_amount: string }
type DaySummary = {
  total_earned_today: string
  total_paid_today: string
}
type DailyWagesResponse = {
  results: Array<{ wage_today: string }>
}

const route = useRoute()
const siteId = computed(() => String(route.params.siteId || ''))
const api = createApiClient()
const site = ref<Site | null>(null)
const pending = ref(true)
const error = ref('')

const workerCount = ref(0)
const activeWorkerCount = ref(0)
const pendingWages = ref(0)
const materialCount = ref(0)
const pendingMaterials = ref(0)
const presentToday = ref(0)
const earnedToday = ref(0)
const paidToday = ref(0)

const siteMeta = computed(() => {
  if (!site.value) return ''
  const parts: string[] = []
  if (site.value.location) parts.push(site.value.location)
  parts.push(`Started ${site.value.from_date}`)
  parts.push(`${site.value.total_work_days} days`)
  return parts.join(' · ')
})

function todayIso() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

onMounted(async () => {
  try {
    const today = todayIso()
    const [siteRes, laboursRes, materialsRes, summaryRes, wagesRes] = await Promise.all([
      api.get<Site>(`/sites/${siteId.value}/`),
      api.get('/labours/', { params: { site_id: siteId.value } }),
      api.get('/materials/', { params: { site_id: siteId.value } }),
      api.get<DaySummary>('/attendance/day-summary/', {
        params: { site_id: siteId.value, date: today },
      }).catch(() => null),
      api.get<DailyWagesResponse>('/attendance/daily-wages/', {
        params: { site_id: siteId.value, date: today },
      }).catch(() => null),
    ])

    site.value = siteRes.data

    const labours = unwrapResults<LabourRow>(laboursRes.data)
    workerCount.value = labours.length
    activeWorkerCount.value = labours.filter((l) => l.status === 'active').length
    pendingWages.value = labours.reduce((sum, l) => sum + parseAmount(l.pending_wage), 0)

    const materials = unwrapResults<MaterialRow>(materialsRes.data)
    materialCount.value = materials.length
    pendingMaterials.value = materials.reduce((sum, m) => sum + parseAmount(m.pending_amount), 0)

    if (summaryRes?.data) {
      earnedToday.value = parseAmount(summaryRes.data.total_earned_today)
      paidToday.value = parseAmount(summaryRes.data.total_paid_today)
    }

    const wageRows = wagesRes?.data?.results ?? []
    presentToday.value = wageRows.filter((r) => parseAmount(r.wage_today) > 0).length
  } catch {
    error.value = 'Site not found.'
  } finally {
    pending.value = false
  }
})
</script>

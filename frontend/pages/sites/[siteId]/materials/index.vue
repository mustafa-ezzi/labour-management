<template>
  <div>
    <UiPageHeader title="Materials" subtitle="Definitions and totals from usage entries">
      <template #action>
        <div class="flex flex-wrap gap-2">
          <NuxtLink
            :to="`/sites/${siteId}/materials/new`"
            class="ui-btn-secondary"
          >
            Add material
          </NuxtLink>
          <NuxtLink
            :to="`/sites/${siteId}/materials/usage`"
            class="ui-btn-primary inline-flex items-center gap-2"
          >
            <AppNavIcon name="log" class="h-4 w-4" />
            Log usage
          </NuxtLink>
        </div>
      </template>
    </UiPageHeader>

    <div class="mb-5 grid grid-cols-2 gap-3">
      <NuxtLink
        :to="`/sites/${siteId}/materials/usage`"
        class="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3 transition-all hover:border-violet-400/40 hover:bg-violet-50 border-gray-200 bg-white hover:border-violet-300 hover:bg-violet-50"
      >
        <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-600 text-white">
          <AppNavIcon name="log" class="h-4 w-4" />
        </span>
        <div class="min-w-0">
          <p class="text-sm font-semibold text-gray-900">Log usage</p>
          <p class="text-[11px] text-gray-500">Today’s consumption</p>
        </div>
      </NuxtLink>
      <NuxtLink
        :to="`/sites/${siteId}/materials/pay`"
        class="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3 transition-all hover:border-violet-400/40 hover:bg-violet-50 border-gray-200 bg-white hover:border-violet-300 hover:bg-violet-50"
      >
        <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-600 text-white">
          <AppNavIcon name="pay" class="h-4 w-4" />
        </span>
        <div class="min-w-0">
          <p class="text-sm font-semibold text-gray-900">Pay</p>
          <p class="text-[11px] text-gray-500">Settle pending costs</p>
        </div>
      </NuxtLink>
    </div>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <template v-else-if="materials.length">
      <div class="mb-4 grid gap-3 sm:grid-cols-2">
        <div class="rounded-lg border border-violet-500/25 bg-violet-50 px-4 py-3 lg:border-violet-300 lg:bg-violet-50">
          <p class="text-xs font-semibold uppercase tracking-widest text-violet-700">
            Total logged cost
          </p>
          <p class="mt-1 text-2xl font-black tabular-nums text-violet-900">
            {{ fmtMoney(siteTotalCost) }}
          </p>
        </div>
        <div class="rounded-lg border border-amber-500/25 bg-amber-50 px-4 py-3 lg:border-amber-300 lg:bg-amber-50">
          <p class="text-xs font-semibold uppercase tracking-widest text-amber-700">
            Pending payment
          </p>
          <p class="mt-1 text-2xl font-black tabular-nums text-amber-900">
            {{ fmtMoney(siteTotalPending) }}
          </p>
        </div>
      </div>

      <ul class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <li v-for="m in materials" :key="m.id">
          <NuxtLink :to="`/sites/${siteId}/materials/${m.id}`" class="ui-card-hover flex h-full flex-col gap-3">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <p class="truncate font-semibold text-gray-900">{{ m.name }}</p>
                <p class="ui-muted mt-0.5">
                  {{ m.unit_of_measure }} · {{ fmtMoney(m.rate_per_unit) }}/{{ m.unit_of_measure }}
                </p>
              </div>
              <span
                class="shrink-0 rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide"
                :class="
                  m.usage_count > 0
                    ? 'bg-violet-500/15 text-violet-300 lg:bg-violet-100 lg:text-violet-700'
                    : 'bg-gray-100 text-gray-400 lg:bg-gray-100 text-gray-400'
                "
              >
                {{ m.usage_count }} {{ m.usage_count === 1 ? 'entry' : 'entries' }}
              </span>
            </div>

            <div class="grid grid-cols-3 gap-2 border-t border-gray-100 pt-3 lg:border-gray-100">
              <div>
                <p class="text-[10px] font-semibold uppercase tracking-widest text-gray-400">
                  Qty
                </p>
                <p class="mt-0.5 text-sm font-bold tabular-nums text-gray-900">
                  {{ fmtQty(m.total_quantity_used) }}
                </p>
              </div>
              <div>
                <p class="text-[10px] font-semibold uppercase tracking-widest text-gray-400">
                  Cost
                </p>
                <p class="mt-0.5 text-sm font-bold tabular-nums text-violet-700">
                  {{ fmtMoney(m.total_amount_spent) }}
                </p>
              </div>
              <div>
                <p class="text-[10px] font-semibold uppercase tracking-widest text-gray-400">
                  Due
                </p>
                <p
                  class="mt-0.5 text-sm font-bold tabular-nums"
                  :class="parseAmount(m.pending_amount) > 0 ? 'text-amber-600' : 'text-gray-400'"
                >
                  {{ fmtMoney(m.pending_amount) }}
                </p>
              </div>
            </div>

            <div v-if="m.latest_usage_date" class="text-xs text-gray-400">
              Last used: {{ m.latest_usage_date }}
              <span v-if="Number(m.average_daily_usage) > 0" class="ml-2">
                · avg {{ fmtQty(m.average_daily_usage) }} {{ m.unit_of_measure }}/day
              </span>
            </div>
          </NuxtLink>
        </li>
      </ul>
    </template>
    <UiCard v-else class="text-center">
      <p class="text-gray-600">No materials on this site yet</p>
      <NuxtLink
        :to="`/sites/${siteId}/materials/new`"
        class="ui-btn-primary mt-4 inline-flex"
      >
        Add material
      </NuxtLink>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
type Material = {
  id: string
  name: string
  unit_of_measure: string
  rate_per_unit: string
  total_quantity_used: string
  total_amount_spent: string
  total_amount_paid: string
  pending_amount: string
  latest_usage_date: string | null
  usage_count: number
  average_daily_usage: string
}

const route = useRoute()
const siteId = computed(() => String(route.params.siteId || ''))
const api = createApiClient()
const materials = ref<Material[]>([])
const loading = ref(false)
const error = ref('')

const siteTotalCost = computed(() =>
  materials.value.reduce((sum, m) => sum + Number(m.total_amount_spent), 0),
)

const siteTotalPending = computed(() =>
  materials.value.reduce((sum, m) => sum + parseAmount(m.pending_amount), 0),
)

function fmtMoney(val: string | number) {
  return 'PKR ' + Number(val).toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function fmtQty(val: string | number) {
  const n = Number(val)
  return n % 1 === 0 ? String(n) : n.toFixed(3).replace(/\.?0+$/, '')
}

async function loadMaterials() {
  if (!siteId.value) return
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/materials/', { params: { site_id: siteId.value } })
    materials.value = Array.isArray(data) ? data : (data.results ?? [])
  } catch {
    error.value = 'Could not load materials.'
  } finally {
    loading.value = false
  }
}

watch(siteId, loadMaterials, { immediate: true })
</script>

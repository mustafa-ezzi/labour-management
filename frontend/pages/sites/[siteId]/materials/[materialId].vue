<template>
  <div>
    <NuxtLink :to="`/sites/${route.params.siteId}/materials`" class="ui-link mb-4 inline-block">
      ← Materials
    </NuxtLink>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="loadErr" class="text-red-400">{{ loadErr }}</p>
    <template v-else-if="material">
      <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 class="text-xl font-bold text-white lg:text-gray-900">{{ material.name }}</h1>
          <p class="ui-muted mt-0.5">
            {{ material.unit_of_measure }} · {{ fmtMoney(material.rate_per_unit) }} per {{ material.unit_of_measure }}
          </p>
        </div>
        <div class="flex shrink-0 flex-wrap gap-2">
          <NuxtLink
            :to="`/sites/${route.params.siteId}/materials/pay?material_id=${material.id}`"
            class="ui-btn-secondary py-2 text-xs"
          >
            Pay balance
          </NuxtLink>
          <NuxtLink
            :to="`/sites/${route.params.siteId}/materials/usage?material_id=${material.id}`"
            class="ui-btn-primary py-2 text-xs"
          >
            + Log usage
          </NuxtLink>
        </div>
      </div>

      <div class="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <UiCard>
          <p class="ui-label !mb-0">Total qty</p>
          <p class="ui-stat-value mt-1 lg:!text-gray-900">
            {{ fmtQty(material.total_quantity_used) }}
            <span class="text-sm font-normal text-white/50 lg:text-gray-500">{{ material.unit_of_measure }}</span>
          </p>
        </UiCard>
        <UiCard>
          <p class="ui-label !mb-0">Total cost</p>
          <p class="mt-1 text-lg font-bold tabular-nums text-green-300 lg:text-xl lg:text-green-700">
            {{ fmtMoney(material.total_amount_spent) }}
          </p>
        </UiCard>
        <UiCard>
          <p class="ui-label !mb-0">Paid</p>
          <p class="mt-1 text-lg font-bold tabular-nums text-white lg:text-gray-900">
            {{ fmtMoney(material.total_amount_paid) }}
          </p>
        </UiCard>
        <UiCard>
          <p class="ui-label !mb-0">Pending</p>
          <p class="mt-1 text-lg font-bold tabular-nums text-amber-300 lg:text-amber-600">
            {{ fmtMoney(material.pending_amount) }}
          </p>
        </UiCard>
        <UiCard>
          <p class="ui-label !mb-0">Entries</p>
          <p class="ui-stat-value mt-1 lg:!text-gray-900">{{ material.usage_count }}</p>
        </UiCard>
        <UiCard>
          <p class="ui-label !mb-0">Avg/day</p>
          <p class="ui-stat-value mt-1 lg:!text-gray-900">
            {{ fmtQty(material.average_daily_usage) }}
            <span class="text-sm font-normal text-white/50 lg:text-gray-500">{{ material.unit_of_measure }}</span>
          </p>
        </UiCard>
      </div>

      <div class="lg:grid lg:grid-cols-12 lg:gap-8">
        <div class="lg:col-span-4">
          <UiCard class="space-y-4">
            <p class="text-sm font-semibold text-white/80 lg:text-gray-700">Edit material</p>
            <div>
              <label class="ui-label" for="name">Name</label>
              <input id="name" v-model="form.name" required class="ui-input" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="ui-label" for="uom">Unit</label>
                <input id="uom" v-model="form.unitOfMeasure" required class="ui-input" />
              </div>
              <div>
                <label class="ui-label" for="rate">Rate</label>
                <input id="rate" v-model="form.ratePerUnit" type="number" min="0" step="0.01" required class="ui-input" />
              </div>
            </div>
            <div>
              <label class="ui-label" for="notes">Notes</label>
              <input id="notes" v-model="form.notes" class="ui-input" />
            </div>
            <p v-if="saveErr" class="rounded-lg border border-red-400/20 bg-red-500/10 px-3 py-2 text-sm text-red-300">
              {{ saveErr }}
            </p>
            <p v-if="saveMsg" class="text-sm text-green-400 lg:text-green-700">{{ saveMsg }}</p>
            <button type="button" class="ui-btn-primary w-full" :disabled="saving" @click="save">{{ saving ? 'Saving…' : 'Save changes' }}</button>
            <button type="button" class="ui-btn-danger w-full" @click="remove">Delete material</button>
          </UiCard>
        </div>

        <div class="mt-6 lg:col-span-8 lg:mt-0">
          <div class="mb-3 flex items-center justify-between">
            <p class="text-sm font-semibold text-white/70 lg:text-gray-700">Usage history</p>
            <p class="ui-muted">{{ usageEntries.length }} entries</p>
          </div>

          <p v-if="loadingHistory" class="ui-muted">Loading…</p>
          <template v-else>
            <div v-if="usageEntries.length" class="space-y-2">
              <div
                v-for="entry in usageEntries"
                :key="entry.id"
                class="rounded-lg border border-white/[0.07] bg-white/[0.04] px-4 py-3 lg:border-gray-200 lg:bg-white lg:shadow-sm"
              >
                <div class="flex items-center justify-between gap-3">
                  <div class="flex-1">
                    <div class="flex flex-wrap items-center gap-3">
                      <p class="text-sm font-semibold text-white lg:text-gray-900">{{ entry.usage_date }}</p>
                      <p class="font-mono text-sm text-white/70 lg:text-gray-600">
                        {{ fmtQty(entry.quantity_used) }} {{ material.unit_of_measure }}
                        × {{ fmtMoney(material.rate_per_unit) }}
                        =
                        <span class="font-bold text-green-300 lg:text-green-700">{{ fmtMoney(entry.calculated_amount) }}</span>
                      </p>
                      <p class="mt-1 text-xs text-white/45 lg:text-gray-500">
                        Paid {{ fmtMoney(entry.amount_paid) }} · Due
                        <span
                          class="font-semibold"
                          :class="parseAmount(entry.pending_amount) > 0 ? 'text-amber-300 lg:text-amber-600' : 'text-green-400 lg:text-green-700'"
                        >
                          {{ fmtMoney(entry.pending_amount) }}
                        </span>
                      </p>
                    </div>
                    <p v-if="entry.notes" class="mt-0.5 text-xs text-white/40 lg:text-gray-400">{{ entry.notes }}</p>
                  </div>
                  <button
                    type="button"
                    class="shrink-0 text-xs text-red-300/60 hover:text-red-300 hover:underline lg:text-red-400/70 lg:hover:text-red-500"
                    @click="deleteUsage(entry.id)"
                  >
                    Remove
                  </button>
                </div>
              </div>

              <div class="rounded-lg border border-green-500/20 bg-green-500/[0.06] px-4 py-3 lg:border-green-200 lg:bg-green-50">
                <p class="text-xs font-semibold uppercase tracking-widest text-green-300 lg:text-green-600">Running total</p>
                <p class="mt-1 text-xl font-black tabular-nums text-green-300 lg:text-green-700">{{ fmtMoney(runningTotal) }}</p>
                <p class="ui-muted mt-0.5">{{ fmtQty(totalQty) }} {{ material.unit_of_measure }} total</p>
              </div>
            </div>

            <UiCard v-else class="text-center">
              <p class="text-white/50 lg:text-gray-500">No usage entries yet</p>
              <NuxtLink :to="`/sites/${route.params.siteId}/materials/usage?material_id=${material.id}`" class="ui-btn-primary mt-4 inline-flex">
                Log first usage
              </NuxtLink>
            </UiCard>

            <div v-if="payments.length" class="mt-8">
              <p class="mb-3 text-sm font-semibold text-white/70 lg:text-gray-700">Payment history</p>
              <div class="space-y-2">
                <div
                  v-for="p in payments"
                  :key="p.id"
                  class="rounded-lg border border-white/[0.07] bg-white/[0.04] px-4 py-3 lg:border-gray-200 lg:bg-white lg:shadow-sm"
                >
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <p class="text-sm font-semibold text-white lg:text-gray-900">{{ p.payment_date }}</p>
                      <p class="text-xs text-white/45 lg:text-gray-500">
                        {{ p.payment_type }} · balance after {{ fmtMoney(p.remaining_amount) }}
                      </p>
                      <p v-if="p.notes" class="mt-0.5 text-xs text-white/40 lg:text-gray-400">{{ p.notes }}</p>
                    </div>
                    <p class="text-sm font-bold tabular-nums text-green-300 lg:text-green-700">
                      {{ fmtMoney(p.amount_paid) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
type MaterialDetail = {
  id: string
  site_id: string
  name: string
  unit_of_measure: string
  rate_per_unit: string
  notes: string
  total_quantity_used: string
  total_amount_spent: string
  total_amount_paid: string
  pending_amount: string
  latest_usage_date: string | null
  usage_count: number
  average_daily_usage: string
}
type UsageEntry = {
  id: string
  usage_date: string
  quantity_used: string
  calculated_amount: string
  amount_paid: string
  pending_amount: string
  notes: string
}
type MaterialPaymentRow = {
  id: string
  payment_date: string
  amount_paid: string
  payment_type: string
  remaining_amount: string
  notes: string
}

const route = useRoute()
const router = useRouter()
const api = createApiClient()

const materialId = computed(() => String(route.params.materialId || ''))
const siteIdStr = computed(() => String(route.params.siteId || ''))

const material = ref<MaterialDetail | null>(null)
const usageEntries = ref<UsageEntry[]>([])
const payments = ref<MaterialPaymentRow[]>([])
const loading = ref(true)
const loadErr = ref('')
const loadingHistory = ref(false)

const form = ref({ name: '', unitOfMeasure: '', ratePerUnit: '', notes: '' })
const saving = ref(false)
const saveErr = ref('')
const saveMsg = ref('')

const runningTotal = computed(() =>
  usageEntries.value.reduce((sum, e) => sum + Number(e.calculated_amount), 0),
)
const totalQty = computed(() => usageEntries.value.reduce((sum, e) => sum + Number(e.quantity_used), 0))

function fmtMoney(val: string | number) {
  return 'PKR ' + Number(val).toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
function fmtQty(val: string | number) {
  const n = Number(val)
  return n % 1 === 0 ? String(n) : n.toFixed(3).replace(/\.?0+$/, '')
}

async function loadMaterial() {
  loading.value = true
  loadErr.value = ''
  try {
    const { data } = await api.get<MaterialDetail>(`/materials/${materialId.value}/`)
    if (data.site_id !== siteIdStr.value) {
      loadErr.value = 'This material belongs to another site.'
      material.value = null
      return
    }
    material.value = data
    form.value = {
      name: data.name,
      unitOfMeasure: data.unit_of_measure,
      ratePerUnit: data.rate_per_unit,
      notes: data.notes,
    }
  } catch {
    loadErr.value = 'Material not found.'
    material.value = null
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  loadingHistory.value = true
  try {
    const [usageRes, payRes] = await Promise.all([
      api.get('/material-usage/', { params: { material_id: materialId.value } }),
      api.get('/material-payments/', { params: { material_id: materialId.value } }),
    ])
    usageEntries.value = Array.isArray(usageRes.data)
      ? usageRes.data
      : (usageRes.data.results ?? [])
    payments.value = Array.isArray(payRes.data) ? payRes.data : (payRes.data.results ?? [])
  } finally {
    loadingHistory.value = false
  }
}

async function save() {
  if (!material.value) return
  saving.value = true
  saveErr.value = ''
  saveMsg.value = ''
  try {
    await api.patch(`/materials/${material.value.id}/`, {
      name: form.value.name,
      unit_of_measure: form.value.unitOfMeasure,
      rate_per_unit: form.value.ratePerUnit,
      notes: form.value.notes,
      site_id: material.value.site_id,
    })
    saveMsg.value = 'Changes saved.'
    await loadMaterial()
  } catch {
    saveErr.value = 'Could not save changes.'
  } finally {
    saving.value = false
  }
}

async function remove() {
  if (!material.value) return
  if (!confirm(`Delete "${material.value.name}" and all its usage history?`)) return
  try {
    await api.delete(`/materials/${material.value.id}/`)
    await router.push(`/sites/${siteIdStr.value}/materials`)
  } catch {
    saveErr.value = 'Could not delete material.'
  }
}

async function deleteUsage(id: string) {
  if (!confirm('Remove this usage entry?')) return
  try {
    await api.delete(`/material-usage/${id}/`)
    await Promise.all([loadHistory(), loadMaterial()])
  } catch {
    saveErr.value = 'Could not remove entry.'
  }
}

async function init() {
  await loadMaterial()
  if (material.value) await loadHistory()
}

watch([materialId, siteIdStr], init, { immediate: true })
</script>

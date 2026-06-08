<template>
  <div>
    <NuxtLink :to="`/sites/${siteId}/materials`" class="ui-link mb-4 inline-block">← Materials</NuxtLink>
    <UiPageHeader title="Log usage" subtitle="Daily consumption — amounts calculated automatically" />

    <div class="lg:grid lg:grid-cols-12 lg:gap-8">
      <div class="space-y-4 lg:col-span-4">
        <UiCard>
          <label class="ui-label" for="udate">Date</label>
          <input id="udate" v-model="usageDate" type="date" class="ui-input" @change="onDateChange" />
        </UiCard>

        <UiCard v-if="daySummary">
          <p class="ui-label !mb-3">Today's material cost</p>
          <p class="text-2xl font-black tabular-nums text-white lg:text-gray-900">
            {{ fmtMoney(daySummary.total_cost) }}
          </p>
          <div class="mt-3 grid grid-cols-2 gap-3 border-t border-white/[0.07] pt-3 lg:border-gray-100">
            <div>
              <p class="text-[10px] font-semibold uppercase text-white/40 lg:text-gray-400">Paid</p>
              <p class="text-sm font-bold tabular-nums text-white lg:text-gray-800">
                {{ fmtMoney(daySummary.total_paid) }}
              </p>
            </div>
            <div>
              <p class="text-[10px] font-semibold uppercase text-white/40 lg:text-gray-400">Pending</p>
              <p class="text-sm font-bold tabular-nums text-amber-300 lg:text-amber-600">
                {{ fmtMoney(daySummary.total_pending) }}
              </p>
            </div>
          </div>
          <p class="ui-muted mt-2">{{ daySummary.entry_count }} entries for this date</p>
          <NuxtLink
            v-if="parseAmount(daySummary.total_pending) > 0"
            :to="`/sites/${siteId}/materials/pay`"
            class="ui-btn-secondary mt-3 w-full text-center text-xs"
          >
            Pay pending
          </NuxtLink>
        </UiCard>

        <UiCard v-if="materials.length">
          <p class="mb-3 text-sm font-semibold text-white/80 lg:text-gray-700">Add usage entry</p>

          <div class="space-y-3">
            <div>
              <label class="ui-label" for="material">Material</label>
              <select id="material" v-model="form.materialId" class="ui-select" @change="onMaterialChange">
                <option value="">Select material</option>
                <option v-for="m in materials" :key="m.id" :value="m.id">
                  {{ m.name }} ({{ m.unit_of_measure }})
                </option>
              </select>
            </div>

            <div v-if="selectedMaterial">
              <label class="ui-label" :for="`qty-${selectedMaterial.id}`">
                Quantity used ({{ selectedMaterial.unit_of_measure }})
              </label>
              <input
                :id="`qty-${selectedMaterial.id}`"
                v-model="form.quantity"
                type="number"
                min="0.001"
                step="any"
                class="ui-input"
                placeholder="0"
                @input="onQtyInput"
              />
            </div>

            <div
              v-if="selectedMaterial && form.quantity && Number(form.quantity) > 0"
              class="rounded-lg border border-green-500/25 bg-green-500/[0.07] px-4 py-3 lg:border-green-200 lg:bg-green-50"
            >
              <p class="text-[10px] font-semibold uppercase tracking-widest text-green-300 lg:text-green-600">
                Formula
              </p>
              <p class="mt-1 font-mono text-sm text-white lg:text-gray-800">
                {{ fmtQty(form.quantity) }} {{ selectedMaterial.unit_of_measure }}
                × {{ fmtMoney(selectedMaterial.rate_per_unit) }}
              </p>
              <p class="mt-2 text-xl font-black tabular-nums text-green-300 lg:text-green-700">
                = {{ fmtMoney(calculatedAmount) }}
              </p>
            </div>

            <div>
              <label class="ui-label" for="fnotes">Notes (optional)</label>
              <input id="fnotes" v-model="form.notes" class="ui-input" placeholder="e.g. Foundation work" />
            </div>

            <p v-if="formErr" class="rounded-lg border border-red-400/20 bg-red-500/10 px-3 py-2 text-sm text-red-300">
              {{ formErr }}
            </p>
            <p v-if="formSuccess" class="text-sm text-green-400 lg:text-green-700">{{ formSuccess }}</p>

            <button
              type="button"
              class="ui-btn-primary w-full"
              :disabled="saving || !form.materialId || !form.quantity || Number(form.quantity) <= 0"
              @click="saveEntry"
            >
              {{ saving ? 'Saving…' : `Save — ${fmtMoney(calculatedAmount)}` }}
            </button>
          </div>
        </UiCard>
        <p v-else-if="!loadingMaterials && siteId" class="ui-muted">
          No materials on this site.
          <NuxtLink :to="`/sites/${siteId}/materials/new`" class="ui-link">Add one</NuxtLink>
        </p>
      </div>

      <div class="mt-6 lg:col-span-8 lg:mt-0">
        <p v-if="loadingEntries" class="ui-muted">Loading entries…</p>
        <template v-else>
          <div v-if="entries.length" class="space-y-2">
            <div
              v-for="entry in entries"
              :key="entry.id"
              class="rounded-lg border border-white/[0.07] bg-white/[0.04] px-4 py-3 lg:border-gray-200 lg:bg-white lg:shadow-sm"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="font-semibold text-white lg:text-gray-900">{{ entry.material_name }}</p>
                    <span
                      class="rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide bg-white/[0.07] text-white/50 lg:bg-gray-100 lg:text-gray-500"
                    >
                      {{ entry.unit_of_measure }}
                    </span>
                  </div>
                  <p class="mt-1 font-mono text-sm text-white/70 lg:text-gray-600">
                    {{ fmtQty(entry.quantity_used) }} {{ entry.unit_of_measure }}
                    × {{ fmtMoney(entry.rate_per_unit) }}
                    = <span class="font-bold text-green-300 lg:text-green-700">{{ fmtMoney(entry.calculated_amount) }}</span>
                  </p>
                  <p class="mt-1 text-xs text-white/45 lg:text-gray-500">
                    Due {{ fmtMoney(entry.pending_amount) }}
                  </p>
                  <p v-if="entry.notes" class="mt-0.5 text-xs text-white/40 lg:text-gray-400">{{ entry.notes }}</p>
                </div>
                <button
                  type="button"
                  class="shrink-0 text-xs text-red-300/60 hover:text-red-300 hover:underline lg:text-red-400/70 lg:hover:text-red-500"
                  @click="deleteEntry(entry.id)"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
          <UiCard v-else-if="siteId" class="text-center">
            <p class="text-white/50 lg:text-gray-500">No entries for {{ usageDate }}</p>
          </UiCard>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
type Material = { id: string; name: string; unit_of_measure: string; rate_per_unit: string }
type UsageEntry = {
  id: string
  material_name: string
  unit_of_measure: string
  rate_per_unit: string
  usage_date: string
  quantity_used: string
  calculated_amount: string
  amount_paid: string
  pending_amount: string
  notes: string
}
type DaySummary = {
  total_cost: string
  total_paid: string
  total_pending: string
  entry_count: number
}

const route = useRoute()
const api = createApiClient()
const siteId = computed(() => String(route.params.siteId || ''))

const materials = ref<Material[]>([])
const entries = ref<UsageEntry[]>([])
const daySummary = ref<DaySummary | null>(null)
const usageDate = ref(new Date().toISOString().slice(0, 10))
const loadingMaterials = ref(false)
const loadingEntries = ref(false)

const form = ref({ materialId: '', quantity: '', notes: '' })
const saving = ref(false)
const formErr = ref('')
const formSuccess = ref('')

const selectedMaterial = computed(() => materials.value.find((m) => m.id === form.value.materialId))
const calculatedAmount = computed(() => {
  if (!selectedMaterial.value || !form.value.quantity) return 0
  return Number(selectedMaterial.value.rate_per_unit) * Number(form.value.quantity)
})

function fmtMoney(val: string | number) {
  return 'PKR ' + Number(val).toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
function fmtQty(val: string | number) {
  const n = Number(val)
  return n % 1 === 0 ? String(n) : n.toFixed(3).replace(/\.?0+$/, '')
}

function onQtyInput() {
  formSuccess.value = ''
  formErr.value = ''
}

function onMaterialChange() {
  form.value.quantity = ''
  formSuccess.value = ''
  formErr.value = ''
}

function preselectMaterialFromQuery() {
  const q = route.query.material_id
  if (typeof q !== 'string' || !q) return
  form.value.materialId = q
}

async function loadMaterials() {
  if (!siteId.value) return
  loadingMaterials.value = true
  try {
    const { data } = await api.get('/materials/', { params: { site_id: siteId.value } })
    materials.value = Array.isArray(data) ? data : (data.results ?? [])
    preselectMaterialFromQuery()
  } finally {
    loadingMaterials.value = false
  }
}

async function loadEntries() {
  if (!siteId.value) return
  loadingEntries.value = true
  try {
    const [entriesRes, summaryRes] = await Promise.all([
      api.get('/material-usage/', {
        params: { site_id: siteId.value, usage_date: usageDate.value },
      }),
      api.get('/material-usage/day-summary/', {
        params: { site_id: siteId.value, usage_date: usageDate.value },
      }),
    ])
    const d = entriesRes.data
    entries.value = Array.isArray(d) ? d : (d.results ?? [])
    daySummary.value = summaryRes.data
  } finally {
    loadingEntries.value = false
  }
}

async function onDateChange() {
  await loadEntries()
}

async function saveEntry() {
  if (!form.value.materialId || !form.value.quantity || Number(form.value.quantity) <= 0) return
  saving.value = true
  formErr.value = ''
  formSuccess.value = ''
  try {
    await api.post('/material-usage/', {
      material_id: form.value.materialId,
      usage_date: usageDate.value,
      quantity_used: form.value.quantity,
      notes: form.value.notes,
    })
    const mat = selectedMaterial.value!
    formSuccess.value = `Saved ${fmtQty(form.value.quantity)} ${mat.unit_of_measure} of ${mat.name} = ${fmtMoney(calculatedAmount.value)}`
    form.value.quantity = ''
    form.value.notes = ''
    await loadEntries()
  } catch {
    formErr.value = 'Could not save entry.'
  } finally {
    saving.value = false
  }
}

async function deleteEntry(id: string) {
  if (!confirm('Remove this usage entry?')) return
  try {
    await api.delete(`/material-usage/${id}/`)
    await loadEntries()
  } catch {
    formErr.value = 'Could not remove entry.'
  }
}

async function init() {
  form.value = { materialId: '', quantity: '', notes: '' }
  await loadMaterials()
  preselectMaterialFromQuery()
  await loadEntries()
}

watch(siteId, init, { immediate: true })

watch(
  () => route.query.material_id,
  () => {
    preselectMaterialFromQuery()
  },
)
</script>

<template>
  <div>
    <h1 class="mb-5 text-xl font-bold text-gray-900">Add material</h1>
    <UiCard>
      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="ui-label" for="name">Material name</label>
          <input id="name" v-model="name" required class="ui-input" placeholder="e.g. Cement" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="ui-label" for="uom">Unit of measure</label>
            <input
              id="uom"
              v-model="unitOfMeasure"
              required
              class="ui-input"
              placeholder="KG, Bags…"
              list="uom-suggestions"
            />
            <datalist id="uom-suggestions">
              <option v-for="u in uomSuggestions" :key="u" :value="u" />
            </datalist>
          </div>
          <div>
            <label class="ui-label" for="rate">Rate per unit (PKR)</label>
            <input id="rate" v-model="ratePerUnit" type="number" min="0" step="0.01" required class="ui-input" />
          </div>
        </div>
        <div v-if="ratePerUnit" class="rounded-lg border border-violet-500/20 bg-violet-500/[0.06] px-4 py-3 border-violet-200 bg-violet-50">
          <p class="text-xs font-semibold uppercase tracking-widest text-violet-300 text-violet-600">Cost preview</p>
          <p class="mt-1 font-mono text-sm text-gray-800">
            1 {{ unitOfMeasure || 'unit' }} × {{ fmtMoney(ratePerUnit) }} =
            <span class="font-bold text-violet-700">{{ fmtMoney(ratePerUnit) }}</span>
          </p>
        </div>
        <div>
          <label class="ui-label" for="notes">Notes (optional)</label>
          <input id="notes" v-model="notes" class="ui-input" />
        </div>
        <p v-if="err" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
          {{ err }}
        </p>
        <button type="submit" class="ui-btn-primary w-full" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save material' }}
        </button>
      </form>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const api = createApiClient()
const siteId = computed(() => String(route.params.siteId || ''))

const name = ref('')
const unitOfMeasure = ref('')
const ratePerUnit = ref('')
const notes = ref('')
const saving = ref(false)
const err = ref('')
const uomSuggestions = ['KG', 'Bags', 'Liters', 'Tons', 'm³', 'Pieces', 'Nos']

function fmtMoney(val: string | number) {
  return 'PKR ' + Number(val).toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function submit() {
  if (!siteId.value) return
  saving.value = true
  err.value = ''
  try {
    await api.post('/materials/', {
      site_id: siteId.value,
      name: name.value,
      unit_of_measure: unitOfMeasure.value,
      rate_per_unit: ratePerUnit.value,
      notes: notes.value,
    })
    await router.push(`/sites/${siteId.value}/materials`)
  } catch {
    err.value = 'Could not save material.'
  } finally {
    saving.value = false
  }
}
</script>

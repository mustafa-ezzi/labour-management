<template>
  <div>
    <NuxtLink :to="`/sites/${route.params.siteId}/crew/${route.params.labourId}`" class="ui-link mb-4 inline-block">
      ← Worker
    </NuxtLink>
    <h1 class="mb-1 text-xl font-bold text-gray-900">Payments</h1>
    <p v-if="labourName" class="ui-muted mb-5">{{ labourName }} · pending {{ pending }}</p>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="err" class="text-red-600">{{ err }}</p>
    <template v-else>
      <UiCard class="mb-6 space-y-3">
        <p class="text-sm font-semibold text-gray-800">Record payment</p>
        <div>
          <label class="ui-label" for="amt">Amount</label>
          <input id="amt" v-model="amount" type="number" min="0" step="0.01" required class="ui-input" />
        </div>
        <div>
          <label class="ui-label" for="pdate">Date</label>
          <input id="pdate" v-model="payDate" type="date" required class="ui-input" />
        </div>
        <div>
          <label class="ui-label" for="notes">Notes</label>
          <input id="notes" v-model="notes" class="ui-input" placeholder="Optional" />
        </div>
        <p v-if="formErr" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
          {{ formErr }}
        </p>
        <button type="button" class="ui-btn-primary w-full" :disabled="submitting" @click="addPayment">
          {{ submitting ? 'Saving…' : 'Add payment' }}
        </button>
      </UiCard>

      <ul v-if="payments.length" class="space-y-2">
        <li
          v-for="p in payments"
          :key="p.id"
          class="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-3 border-gray-200 bg-white shadow-sm"
        >
          <div>
            <p class="font-semibold text-gray-900">{{ p.amount_paid }}</p>
            <p class="mt-0.5 text-xs text-gray-500 text-gray-400">{{ p.payment_date }} · {{ p.payment_type }}</p>
            <p v-if="p.notes" class="text-xs text-gray-500">{{ p.notes }}</p>
          </div>
          <button
            type="button"
            class="text-xs text-red-600/70 hover:text-red-600 hover:underline hover:text-red-600"
            @click="deletePayment(p.id)"
          >
            Remove
          </button>
        </li>
      </ul>
      <p v-else class="ui-muted">No payments yet.</p>
    </template>
  </div>
</template>

<script setup lang="ts">
type Labour = { id: string; name: string; pending_wage: string; site_id: string }
type Payment = {
  id: string
  amount_paid: string
  payment_date: string
  payment_type: string
  remaining_amount: string
  notes: string
}

const route = useRoute()
const api = createApiClient()
const labourPk = computed(() => String(route.params.labourId || ''))

const labourName = ref('')
const pending = ref('')
const payments = ref<Payment[]>([])
const loading = ref(true)
const err = ref('')
const amount = ref('')
const payDate = ref(new Date().toISOString().slice(0, 10))
const notes = ref('')
const submitting = ref(false)
const formErr = ref('')

async function load() {
  loading.value = true
  err.value = ''
  try {
    const lid = labourPk.value
    const [{ data: l }, { data: plist }] = await Promise.all([
      api.get<Labour>(`/labours/${lid}/`),
      api.get('/labour-payments/', { params: { labour_id: lid } }),
    ])
    if (l.site_id !== route.params.siteId) {
      err.value = 'Worker is not on this site.'
      return
    }
    labourName.value = l.name
    pending.value = l.pending_wage
    payments.value = unwrapResults<Payment>(plist)
  } catch {
    err.value = 'Could not load payments.'
  } finally {
    loading.value = false
  }
}

async function addPayment() {
  submitting.value = true
  formErr.value = ''
  try {
    await api.post('/labour-payments/', {
      labour_id: labourPk.value,
      amount_paid: amount.value,
      payment_date: payDate.value,
      notes: notes.value,
    })
    amount.value = ''
    notes.value = ''
    await load()
  } catch (e: unknown) {
    const ax = e as { response?: { data?: Record<string, unknown> } }
    const d = ax.response?.data
    if (d?.amount_paid) {
      formErr.value = Array.isArray(d.amount_paid) ? String(d.amount_paid[0]) : String(d.amount_paid)
    } else {
      formErr.value = 'Could not save payment (check amount vs pending).'
    }
  } finally {
    submitting.value = false
  }
}

async function deletePayment(id: string) {
  if (!confirm('Remove this payment?')) return
  try {
    await api.delete(`/labour-payments/${id}/`)
    await load()
  } catch {
    err.value = 'Could not remove payment.'
  }
}

watch(labourPk, load, { immediate: true })
</script>

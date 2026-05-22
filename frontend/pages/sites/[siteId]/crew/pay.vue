<template>
  <div>
    <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h2 class="text-lg font-semibold text-white lg:text-gray-900">Pay workers</h2>
      <button
        v-if="rows.length"
        type="button"
        class="ui-btn-secondary text-xs sm:text-sm"
        @click="fillSelectedFull"
      >
        Fill full pending
      </button>
    </div>

    <div class="mb-5 grid gap-4 lg:grid-cols-12 lg:gap-8">
      <UiCard class="space-y-4 lg:col-span-4">
        <div>
          <label class="ui-label" for="pdate">Payment date</label>
          <input id="pdate" v-model="payDate" type="date" class="ui-input" />
        </div>
        <div>
          <label class="ui-label" for="notes">Notes (optional)</label>
          <input id="notes" v-model="notes" class="ui-input" placeholder="e.g. Weekly wages" />
        </div>
      </UiCard>

      <div
        v-if="selectedCount > 0"
        class="ui-card lg:col-span-8 lg:sticky lg:top-24 lg:self-start"
      >
        <p class="ui-label !mb-3">Payment summary</p>
        <div class="grid grid-cols-2 gap-4 sm:grid-cols-3">
          <div>
            <p class="text-xs text-white/40 lg:text-gray-500">Workers selected</p>
            <p class="ui-stat-value !text-base lg:!text-gray-900">{{ selectedCount }}</p>
          </div>
          <div>
            <p class="text-xs text-white/40 lg:text-gray-500">Total payable</p>
            <p class="ui-stat-value !text-base lg:!text-gray-900">{{ formatAmount(totalPayable) }}</p>
          </div>
          <div class="col-span-2 sm:col-span-1">
            <p class="text-xs text-white/40 lg:text-gray-500">Amount paying</p>
            <p class="ui-stat-value !text-base text-green-300 lg:!text-green-700">{{ formatAmount(totalPaying) }}</p>
          </div>
        </div>
        <p v-if="totalPaying > totalPayable" class="mt-2 text-sm text-red-400">
          Paying more than total outstanding for selected workers.
        </p>
        <button
          type="button"
          class="ui-btn-primary mt-4 w-full"
          :disabled="submitting || selectedCount === 0 || totalPaying <= 0 || totalPaying > totalPayable"
          @click="submitPayments"
        >
          {{ submitting ? 'Processing…' : `Pay ${selectedCount} worker${selectedCount === 1 ? '' : 's'}` }}
        </button>
        <p v-if="formErr" class="mt-2 text-sm text-red-400">{{ formErr }}</p>
        <p v-if="successMsg" class="mt-2 text-sm text-green-400">{{ successMsg }}</p>
      </div>
    </div>

    <p v-if="loading" class="ui-muted">Loading workers…</p>
    <p v-else-if="loadErr" class="text-red-400">{{ loadErr }}</p>
    <template v-else>
      <div
        v-if="rows.length"
        class="mb-3 flex items-center gap-3 rounded-lg border border-white/[0.07] bg-white/[0.04] px-4 py-3 lg:border-gray-200 lg:bg-white lg:shadow-sm"
      >
        <label class="flex cursor-pointer items-center gap-2 text-sm text-white/70 lg:text-gray-700">
          <input
            v-model="allSelected"
            type="checkbox"
            class="h-5 w-5 rounded border-white/30 text-green-500 lg:border-gray-400"
            @change="toggleSelectAll"
          />
          Select all with balance
        </label>
        <span class="text-xs text-white/35 lg:text-gray-400">{{ rowsWithBalance.length }} owing</span>
      </div>

      <ul class="space-y-2 lg:grid lg:grid-cols-2 lg:gap-3 lg:space-y-0">
        <li
          v-for="row in rows"
          :key="row.labour.id"
          class="flex flex-col gap-3 rounded-lg border px-4 py-3 sm:flex-row sm:items-center"
          :class="
            row.selected
              ? 'border-green-500/30 bg-green-500/[0.07] lg:border-green-300 lg:bg-green-50'
              : 'border-white/[0.07] bg-white/[0.04] lg:border-gray-200 lg:bg-white lg:shadow-sm'
          "
        >
          <label class="flex min-w-0 flex-1 cursor-pointer items-center gap-3">
            <input
              v-model="row.selected"
              type="checkbox"
              class="h-5 w-5 shrink-0 rounded border-white/30 text-green-500"
              :disabled="row.pendingNum <= 0"
              @change="onRowSelect(row)"
            />
            <div class="min-w-0">
              <p class="truncate font-medium text-white lg:text-gray-900">{{ row.labour.name }}</p>
              <p class="text-xs text-white/40 lg:text-gray-500">
                Pending
                <span class="font-semibold text-amber-300/90 lg:text-amber-600">{{ formatAmount(row.pendingNum) }}</span>
              </p>
            </div>
          </label>
          <div class="flex items-center gap-2 sm:w-40">
            <label class="sr-only" :for="`amt-${row.labour.id}`">Amount for {{ row.labour.name }}</label>
            <input
              :id="`amt-${row.labour.id}`"
              v-model="row.amount"
              type="number"
              min="0"
              :max="row.pendingNum"
              step="0.01"
              class="ui-input py-2 text-right tabular-nums"
              :disabled="!row.selected"
              placeholder="0"
              @input="onAmountInput(row)"
            />
          </div>
        </li>
      </ul>
      <UiCard v-if="!rows.length" class="mt-4 text-center">
        <p class="text-white/60 lg:text-gray-600">No active workers on this site.</p>
      </UiCard>
      <UiCard v-else-if="!rowsWithBalance.length" class="mt-4 text-center">
        <p class="text-white/60 lg:text-gray-600">Everyone is paid up on this site.</p>
      </UiCard>
    </template>
  </div>
</template>

<script setup lang="ts">
type LabourRow = {
  id: string
  name: string
  daily_wage: string
  pending_wage: string
}

type PayRow = {
  labour: LabourRow
  selected: boolean
  amount: string
  pendingNum: number
}

const api = createApiClient()
const route = useRoute()
const siteId = computed(() => String(route.params.siteId || ''))

const payDate = ref(new Date().toISOString().slice(0, 10))
const notes = ref('')
const rows = ref<PayRow[]>([])
const loading = ref(false)
const loadErr = ref('')
const submitting = ref(false)
const formErr = ref('')
const successMsg = ref('')
const allSelected = ref(false)

const rowsWithBalance = computed(() => rows.value.filter((r) => r.pendingNum > 0))
const selectedRows = computed(() => rows.value.filter((r) => r.selected))
const selectedCount = computed(() => selectedRows.value.length)
const totalPayable = computed(() => selectedRows.value.reduce((sum, r) => sum + r.pendingNum, 0))
const totalPaying = computed(() => selectedRows.value.reduce((sum, r) => sum + parseAmount(r.amount), 0))

function onRowSelect(row: PayRow) {
  if (row.selected) {
    if (!row.amount || parseAmount(row.amount) <= 0) {
      row.amount = String(row.pendingNum)
    }
  } else {
    row.amount = ''
  }
  syncSelectAll()
}

function onAmountInput(row: PayRow) {
  if (parseAmount(row.amount) > 0 && !row.selected) {
    row.selected = true
  }
  syncSelectAll()
}

function syncSelectAll() {
  const owing = rowsWithBalance.value
  allSelected.value = owing.length > 0 && owing.every((r) => r.selected)
}

function toggleSelectAll() {
  const check = allSelected.value
  for (const row of rowsWithBalance.value) {
    row.selected = check
    row.amount = check ? String(row.pendingNum) : ''
  }
}

function fillSelectedFull() {
  for (const row of selectedRows.value) {
    row.amount = String(row.pendingNum)
  }
}

function preselectFromQuery() {
  const q = route.query.labour_id
  if (typeof q !== 'string' || !q) return
  const row = rows.value.find((r) => r.labour.id === q)
  if (row && row.pendingNum > 0) {
    row.selected = true
    row.amount = String(row.pendingNum)
    syncSelectAll()
  }
}

async function loadWorkers() {
  rows.value = []
  successMsg.value = ''
  formErr.value = ''
  allSelected.value = false
  if (!siteId.value) return
  loading.value = true
  loadErr.value = ''
  try {
    const { data } = await api.get('/labours/', {
      params: { site_id: siteId.value, status: 'active' },
    })
    const labours = unwrapResults<LabourRow>(data)
    rows.value = labours.map((l) => ({
      labour: l,
      selected: false,
      amount: '',
      pendingNum: parseAmount(l.pending_wage),
    }))
    preselectFromQuery()
  } catch {
    loadErr.value = 'Could not load workers.'
  } finally {
    loading.value = false
  }
}

async function submitPayments() {
  const toPay = selectedRows.value.filter((r) => parseAmount(r.amount) > 0)
  if (!toPay.length) {
    formErr.value = 'Enter an amount for at least one selected worker.'
    return
  }
  submitting.value = true
  formErr.value = ''
  successMsg.value = ''
  try {
    const { data } = await api.post<{ created: number; total_paid: string }>(
      '/labour-payments/bulk-pay/',
      {
        payment_date: payDate.value,
        notes: notes.value,
        payments: toPay.map((r) => ({
          labour_id: r.labour.id,
          amount_paid: r.amount,
        })),
      },
    )
    successMsg.value = `Paid ${data.created} worker(s) — total ${formatAmount(data.total_paid)}.`
    await loadWorkers()
  } catch (e: unknown) {
    const ax = e as { response?: { data?: { payments?: { error: string }[]; detail?: string } } }
    const lines = ax.response?.data?.payments
    if (lines?.length) {
      formErr.value = lines.map((x) => x.error).join(' ')
    } else {
      formErr.value = ax.response?.data?.detail || 'Could not save payments.'
    }
  } finally {
    submitting.value = false
  }
}

watch(siteId, loadWorkers, { immediate: true })

watch(
  () => route.query.labour_id,
  () => {
    if (rows.value.length) {
      preselectFromQuery()
    }
  },
)
</script>

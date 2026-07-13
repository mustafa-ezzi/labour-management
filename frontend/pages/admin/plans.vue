<template>
  <div>
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <p class="text-sm text-gray-500">Trial / monthly / yearly catalog. Prices are informational (manual renew).</p>
      <button type="button" class="ui-btn-primary py-2 text-xs" @click="showCreate = !showCreate">
        {{ showCreate ? 'Cancel' : 'Add plan' }}
      </button>
    </div>

    <UiCard v-if="showCreate" class="mb-5">
      <p class="mb-3 text-sm font-semibold text-gray-900">New plan</p>
      <form class="grid gap-3 sm:grid-cols-2" @submit.prevent="createPlan">
        <div>
          <label class="ui-label" for="key">Key</label>
          <input id="key" v-model="form.key" required class="ui-input" placeholder="monthly" />
        </div>
        <div>
          <label class="ui-label" for="name">Name</label>
          <input id="name" v-model="form.name" required class="ui-input" placeholder="Monthly" />
        </div>
        <div>
          <label class="ui-label" for="price">Price</label>
          <input id="price" v-model="form.price" class="ui-input" placeholder="0" />
        </div>
        <div>
          <label class="ui-label" for="days">Duration (days)</label>
          <input id="days" v-model.number="form.duration_days" type="number" min="1" required class="ui-input" />
        </div>
        <div class="sm:col-span-2">
          <button type="submit" class="ui-btn-primary" :disabled="busy">Create</button>
        </div>
      </form>
    </UiCard>

    <p v-if="msg" class="mb-3 text-sm text-emerald-700">{{ msg }}</p>
    <p v-if="error" class="mb-3 text-sm text-red-600">{{ error }}</p>
    <p v-if="loading" class="ui-muted">Loading plans…</p>

    <ul v-else class="divide-y divide-gray-100 overflow-hidden rounded-xl border border-gray-200 bg-white">
      <li v-for="plan in plans" :key="plan.id" class="px-4 py-3">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="text-sm font-semibold text-gray-900">{{ plan.name }}</p>
            <p class="text-xs text-gray-500">
              {{ plan.key }} · {{ plan.duration_days }} days · {{ plan.currency }} {{ plan.price }}
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span
              class="rounded px-2 py-0.5 text-[10px] font-bold uppercase"
              :class="plan.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-500'"
            >
              {{ plan.is_active ? 'active' : 'inactive' }}
            </span>
            <button
              type="button"
              class="ui-btn-secondary py-1.5 text-xs"
              :disabled="busy"
              @click="toggleActive(plan)"
            >
              {{ plan.is_active ? 'Deactivate' : 'Activate' }}
            </button>
          </div>
        </div>
        <div class="mt-3 grid gap-2 sm:grid-cols-4">
          <input v-model="edits[plan.id].name" class="ui-input text-sm" placeholder="Name" />
          <input v-model="edits[plan.id].price" class="ui-input text-sm" placeholder="Price" />
          <input v-model.number="edits[plan.id].duration_days" type="number" min="1" class="ui-input text-sm" />
          <button type="button" class="ui-btn-primary py-2 text-xs" :disabled="busy" @click="savePlan(plan)">
            Save
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

type Plan = {
  id: string
  key: string
  name: string
  price: string
  currency: string
  duration_days: number
  is_active: boolean
}

const api = createApiClient()
const plans = ref<Plan[]>([])
const edits = reactive<Record<string, { name: string; price: string; duration_days: number }>>({})
const loading = ref(true)
const busy = ref(false)
const error = ref('')
const msg = ref('')
const showCreate = ref(false)
const form = reactive({
  key: '',
  name: '',
  price: '0',
  duration_days: 30,
})

function syncEdits(list: Plan[]) {
  for (const p of list) {
    edits[p.id] = {
      name: p.name,
      price: p.price,
      duration_days: p.duration_days,
    }
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get<{ results: Plan[] }>('/admin/plans/')
    plans.value = data.results
    syncEdits(data.results)
  } catch {
    error.value = 'Could not load plans.'
  } finally {
    loading.value = false
  }
}

async function createPlan() {
  busy.value = true
  error.value = ''
  msg.value = ''
  try {
    await api.post('/admin/plans/', { ...form })
    showCreate.value = false
    form.key = ''
    form.name = ''
    form.price = '0'
    form.duration_days = 30
    msg.value = 'Plan created.'
    await load()
  } catch {
    error.value = 'Could not create plan.'
  } finally {
    busy.value = false
  }
}

async function savePlan(plan: Plan) {
  busy.value = true
  error.value = ''
  msg.value = ''
  try {
    await api.patch(`/admin/plans/${plan.id}/`, edits[plan.id])
    msg.value = 'Plan updated.'
    await load()
  } catch {
    error.value = 'Could not save plan.'
  } finally {
    busy.value = false
  }
}

async function toggleActive(plan: Plan) {
  busy.value = true
  error.value = ''
  try {
    await api.patch(`/admin/plans/${plan.id}/`, { is_active: !plan.is_active })
    await load()
  } catch {
    error.value = 'Could not update plan.'
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

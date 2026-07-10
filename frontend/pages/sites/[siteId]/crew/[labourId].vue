<template>
  <div>
    <NuxtLink :to="`/sites/${route.params.siteId}/crew`" class="ui-link mb-4 inline-block">
      ← Workers
    </NuxtLink>
    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="loadErr" class="text-red-600">{{ loadErr }}</p>
    <template v-else-if="labour">
      <div class="mb-4 flex items-start justify-between gap-3">
        <div>
          <h1 class="text-xl font-bold text-gray-900">{{ labour.name }}</h1>
          <p class="ui-muted mt-0.5">
            Wage {{ labour.daily_wage }} · Earned {{ labour.earned_total }} · Paid
            {{ labour.paid_total }}
          </p>
          <p class="mt-0.5 text-sm font-semibold text-violet-700">Pending {{ labour.pending_wage }}</p>
        </div>
        <div class="flex shrink-0 flex-col gap-2 sm:flex-row">
          <NuxtLink
            :to="`/sites/${route.params.siteId}/crew/wages?labour_id=${labour.id}`"
            class="ui-btn-primary py-2 text-xs"
          >
            Daily wage
          </NuxtLink>
          <NuxtLink
            :to="`/sites/${route.params.siteId}/crew/history?labour_id=${labour.id}`"
            class="ui-btn-secondary py-2 text-xs"
          >
            Attendance
          </NuxtLink>
          <NuxtLink
            :to="`/sites/${route.params.siteId}/crew/${labour.id}/payments`"
            class="ui-btn-secondary py-2 text-xs"
          >
            Payments
          </NuxtLink>
        </div>
      </div>
      <form class="space-y-4" @submit.prevent="save">
        <div>
          <label class="ui-label" for="name">Name</label>
          <input id="name" v-model="name" required class="ui-input" />
        </div>
        <div>
          <label class="ui-label" for="wage">Daily wage</label>
          <input id="wage" v-model="dailyWage" type="number" min="0" step="0.01" required class="ui-input" />
        </div>
        <div>
          <label class="ui-label" for="phone">Phone</label>
          <input id="phone" v-model="phone" class="ui-input" />
        </div>
        <div>
          <label class="ui-label" for="status">Status</label>
          <select id="status" v-model="status" class="ui-select">
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
        <p v-if="saveErr" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
          {{ saveErr }}
        </p>
        <button type="submit" class="ui-btn-primary w-full" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save changes' }}
        </button>
      </form>
      <button type="button" class="ui-btn-danger mt-3 w-full" @click="remove">
        Delete worker
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
type Labour = {
  id: string
  site_id: string
  name: string
  daily_wage: string
  phone_number: string
  status: string
  earned_total: string
  paid_total: string
  pending_wage: string
}

const route = useRoute()
const router = useRouter()
const api = createApiClient()
const labourId = computed(() => String(route.params.labourId || ''))

const labour = ref<Labour | null>(null)
const loading = ref(true)
const loadErr = ref('')
const name = ref('')
const dailyWage = ref('')
const phone = ref('')
const status = ref<'active' | 'inactive'>('active')
const saving = ref(false)
const saveErr = ref('')

async function load() {
  loading.value = true
  loadErr.value = ''
  try {
    const { data } = await api.get<Labour>(`/labours/${labourId.value}/`)
    if (data.site_id !== route.params.siteId) {
      loadErr.value = 'Worker is not on this site.'
      labour.value = null
      return
    }
    labour.value = data
    name.value = data.name
    dailyWage.value = data.daily_wage
    phone.value = data.phone_number || ''
    status.value = (data.status as 'active' | 'inactive') || 'active'
  } catch {
    loadErr.value = 'Worker not found.'
    labour.value = null
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!labour.value) return
  saving.value = true
  saveErr.value = ''
  try {
    await api.patch(`/labours/${labour.value.id}/`, {
      site_id: labour.value.site_id,
      name: name.value,
      daily_wage: dailyWage.value,
      phone_number: phone.value,
      status: status.value,
    })
    await load()
  } catch {
    saveErr.value = 'Could not save changes.'
  } finally {
    saving.value = false
  }
}

async function remove() {
  if (!labour.value) return
  if (!confirm('Delete this worker and their attendance/payment records?')) return
  try {
    await api.delete(`/labours/${labour.value.id}/`)
    await router.push(`/sites/${route.params.siteId}/crew`)
  } catch {
    saveErr.value = 'Could not delete.'
  }
}

watch(labourId, load, { immediate: true })
</script>

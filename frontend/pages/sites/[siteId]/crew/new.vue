<template>
  <div>
    <h1 class="mb-5 text-xl font-bold text-gray-900">Add worker</h1>
    <form class="space-y-4" @submit.prevent="submit">
      <div>
        <label class="ui-label" for="name">Name</label>
        <input id="name" v-model="name" required class="ui-input" placeholder="Worker name" />
      </div>
      <div>
        <label class="ui-label" for="wage">Daily wage</label>
        <input
          id="wage"
          v-model="dailyWage"
          type="number"
          min="0"
          step="0.01"
          required
          class="ui-input"
          placeholder="0.00"
        />
      </div>
      <div>
        <label class="ui-label" for="phone">Phone (optional)</label>
        <input id="phone" v-model="phone" class="ui-input" placeholder="+92 300 1234567" />
      </div>
      <div>
        <label class="ui-label" for="status">Status</label>
        <select id="status" v-model="status" class="ui-select">
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
      <p v-if="err" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
        {{ err }}
      </p>
      <button type="submit" class="ui-btn-primary w-full" :disabled="saving">
        {{ saving ? 'Saving…' : 'Save worker' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const api = createApiClient()
const siteId = computed(() => String(route.params.siteId || ''))

const name = ref('')
const dailyWage = ref('2000')
const phone = ref('')
const status = ref<'active' | 'inactive'>('active')
const saving = ref(false)
const err = ref('')

async function submit() {
  if (!siteId.value) return
  saving.value = true
  err.value = ''
  try {
    await api.post('/labours/', {
      site_id: siteId.value,
      name: name.value,
      daily_wage: dailyWage.value,
      phone_number: phone.value,
      status: status.value,
    })
    await router.push(`/sites/${siteId.value}/crew`)
  } catch {
    err.value = 'Could not save worker.'
  } finally {
    saving.value = false
  }
}
</script>

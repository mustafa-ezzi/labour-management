<template>
  <div class="lg:max-w-xl">
    <p class="mb-4">
      <NuxtLink to="/sites" class="ui-link">← Sites</NuxtLink>
    </p>
    <UiPageHeader title="New site" />
    <form class="ui-card space-y-4" @submit.prevent="submit">
      <div>
        <label class="ui-label" for="name">Name</label>
        <input id="name" v-model="name" required class="ui-input" />
      </div>
      <div>
        <label class="ui-label" for="location">Location</label>
        <input id="location" v-model="location" class="ui-input" />
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="ui-label" for="from">From</label>
          <input id="from" v-model="fromDate" type="date" required class="ui-input" />
        </div>
        <div>
          <label class="ui-label" for="to">To</label>
          <input id="to" v-model="toDate" type="date" required class="ui-input" />
        </div>
      </div>
      <p v-if="err" class="text-sm text-red-600">{{ err }}</p>
      <button type="submit" class="ui-btn-primary w-full" :disabled="loading">
        {{ loading ? 'Saving…' : 'Save site' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const name = ref('')
const location = ref('')
const fromDate = ref('')
const toDate = ref('')
const loading = ref(false)
const err = ref('')
const api = createApiClient()
const router = useRouter()

async function submit() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.post<{ id: string }>('/sites/', {
      name: name.value,
      location: location.value,
      from_date: fromDate.value,
      to_date: toDate.value,
    })
    persistSiteId(data.id)
    await router.push(`/sites/${data.id}`)
  } catch {
    err.value = 'Could not save. Check dates (end after start).'
  } finally {
    loading.value = false
  }
}
</script>

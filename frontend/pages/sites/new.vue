<template>
  <div class="lg:max-w-xl">
    <button
      type="button"
      class="mb-4 flex h-9 w-9 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-800"
      aria-label="Go back"
      @click="goBack"
    >
      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
      </svg>
    </button>
    <UiPageHeader title="New site" subtitle="Add a construction site to manage crew and materials" />
    <form class="ui-card space-y-4" @submit.prevent="submit">
      <div>
        <label class="ui-label" for="name">Site name</label>
        <input id="name" v-model="name" required class="ui-input" placeholder="e.g. Downtown Highrise" />
      </div>
      <div>
        <label class="ui-label" for="location">Location</label>
        <input id="location" v-model="location" class="ui-input" placeholder="e.g. Korangi, Karachi" />
      </div>
      <div>
        <label class="ui-label" for="start">Starting date</label>
        <input id="start" v-model="startDate" type="date" required class="ui-input" />
        <p class="mt-1 text-xs text-gray-500">When work begins on this site. Day count starts from here.</p>
      </div>
      <p v-if="err" class="ui-error-banner">{{ err }}</p>
      <button type="submit" class="ui-btn-primary w-full" :disabled="loading">
        {{ loading ? 'Saving…' : 'Save site' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const { goBack } = useSmartBack()
const name = ref('')
const location = ref('')
const startDate = ref(new Date().toISOString().slice(0, 10))
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
      from_date: startDate.value,
    })
    persistSiteId(data.id)
    await router.push(`/sites/${data.id}`)
  } catch {
    err.value = 'Could not save site. Check the starting date and try again.'
  } finally {
    loading.value = false
  }
}
</script>

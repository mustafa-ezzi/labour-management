<template>
  <div class="lg:max-w-xl">
    <p class="mb-4">
      <NuxtLink to="/sites" class="ui-link">← Sites</NuxtLink>
    </p>
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

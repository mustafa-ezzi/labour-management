<template>
  <div>
    <NuxtLink to="/support" class="ui-link mb-4 inline-block">← Support</NuxtLink>
    <UiPageHeader title="New ticket" subtitle="Describe your issue or renew request" />

    <p v-if="error" class="mb-3 ui-error-banner">{{ error }}</p>

    <UiCard>
      <form class="space-y-3" @submit.prevent="submit">
        <div>
          <label class="ui-label" for="subject">Subject</label>
          <input id="subject" v-model="form.subject" required maxlength="255" class="ui-input" />
        </div>
        <div>
          <label class="ui-label" for="body">Message</label>
          <textarea id="body" v-model="form.body" required rows="5" class="ui-input" />
        </div>
        <button type="submit" class="ui-btn-primary w-full sm:w-auto" :disabled="busy">
          {{ busy ? 'Sending…' : 'Send ticket' }}
        </button>
      </form>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const api = createApiClient()
const router = useRouter()
const busy = ref(false)
const error = ref('')
const form = reactive({ subject: '', body: '' })

async function submit() {
  busy.value = true
  error.value = ''
  try {
    const { data } = await api.post<{ id: string }>('/support/tickets/', {
      subject: form.subject,
      body: form.body,
    })
    await router.replace(`/support/${data.id}`)
  } catch {
    error.value = 'Could not create ticket.'
  } finally {
    busy.value = false
  }
}
</script>

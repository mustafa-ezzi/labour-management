<template>
  <div>
    <div class="mb-7">
      <h1 class="text-2xl font-black tracking-tight text-white">Create account</h1>
      <p class="ui-muted mt-1">Set up your company workspace in seconds</p>
    </div>

    <form class="space-y-4" @submit.prevent="submit">
      <div>
        <label class="ui-label" for="company">Company name</label>
        <input
          id="company"
          v-model="companyName"
          type="text"
          required
          class="ui-input"
          placeholder="Acme Construction"
        />
      </div>
      <div>
        <label class="ui-label" for="email">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          required
          class="ui-input"
          placeholder="you@company.com"
        />
      </div>
      <div>
        <label class="ui-label" for="password">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          minlength="8"
          required
          class="ui-input"
          placeholder="Min. 8 characters"
        />
      </div>
      <p v-if="error" class="rounded-lg border border-red-400/20 bg-red-500/10 px-3 py-2 text-sm text-red-300">
        {{ error }}
      </p>
      <button type="submit" class="ui-btn-primary mt-1 w-full py-3" :disabled="loading">
        {{ loading ? 'Creating…' : 'Create account' }}
      </button>
    </form>

    <p class="ui-muted mt-6 text-center">
      Already have an account?
      <NuxtLink to="/login" class="ui-link">Sign in</NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const companyName = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const auth = useAuthStore()
const router = useRouter()

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const api = createApiClient()
    const { data } = await api.post('/auth/register/', {
      company_name: companyName.value,
      email: email.value,
      password: password.value,
    })
    auth.setTokens(data.access, data.refresh)
    await router.push('/dashboard')
  } catch (e: unknown) {
    const err = e as { response?: { data?: Record<string, unknown> } }
    const d = err.response?.data
    if (d && typeof d === 'object') {
      const first = Object.values(d).flat()[0]
      error.value = Array.isArray(first) ? String(first[0]) : String(first || 'Could not register.')
    } else {
      error.value = 'Could not register.'
    }
  } finally {
    loading.value = false
  }
}
</script>

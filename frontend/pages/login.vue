<template>
  <div>
    <div class="mb-7">
      <h1 class="text-2xl font-black tracking-tight text-white">Sign in</h1>
      <p class="ui-muted mt-1">Welcome back — your crew awaits</p>
    </div>

    <form class="space-y-4" @submit.prevent="submit">
      <div>
        <label class="ui-label" for="email">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          autocomplete="email"
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
          autocomplete="current-password"
          required
          class="ui-input"
          placeholder="••••••••"
        />
      </div>
      <p v-if="error" class="rounded-lg border border-red-400/20 bg-red-500/10 px-3 py-2 text-sm text-red-300">
        {{ error }}
      </p>
      <button type="submit" class="ui-btn-primary mt-1 w-full py-3" :disabled="loading">
        {{ loading ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>

    <p class="ui-muted mt-6 text-center">
      No account?
      <NuxtLink to="/register" class="ui-link">Create one</NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { hasStoredAuth } from '~/utils/auth-storage'

definePageMeta({ layout: 'default' })

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const auth = useAuthStore()
const router = useRouter()

onMounted(() => {
  auth.hydrateFromStorage()
  if (auth.isLoggedIn || hasStoredAuth()) {
    router.replace('/dashboard')
  }
})

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const api = createApiClient()
    const { data } = await api.post('/auth/login/', {
      email: email.value,
      password: password.value,
    })
    auth.setTokens(data.access, data.refresh)
    await router.push('/dashboard')
  } catch {
    error.value = 'Invalid email or password.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <div class="mb-7">
      <h1 class="text-2xl font-black tracking-tight text-gray-900">
        {{ wantAdmin ? 'Admin sign in' : 'Sign in' }}
      </h1>
      <p class="ui-muted mt-1">
        {{
          wantAdmin
            ? 'Use your LabourPro App Admin email (createsuperuser account).'
            : 'Welcome back — sign in to your account'
        }}
      </p>
    </div>

    <p v-if="wantAdmin" class="mb-4 rounded-lg border border-violet-200 bg-violet-50 px-3 py-2 text-sm text-violet-900">
      Customer accounts cannot open <strong>/admin</strong>. Sign in with the App Admin account.
    </p>

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
          placeholder="admin@labourpro.com"
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
      <p v-if="error" class="ui-error-banner">
        {{ error }}
      </p>
      <button type="submit" class="ui-btn-primary mt-1 w-full py-3" :disabled="loading">
        {{ loading ? 'Signing in…' : wantAdmin ? 'Sign in to Admin' : 'Sign in' }}
      </button>
    </form>

    <p v-if="!wantAdmin" class="ui-muted mt-6 text-center">
      No account?
      <NuxtLink to="/register" class="ui-link">Create one</NuxtLink>
    </p>
    <p v-else class="ui-muted mt-6 text-center">
      Not Admin?
      <NuxtLink to="/login" class="ui-link">Customer sign in</NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { hasStoredAuth } from '~/utils/auth-storage'

definePageMeta({ layout: 'default' })

const route = useRoute()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const auth = useAuthStore()
const router = useRouter()

const wantAdmin = computed(
  () => route.query.admin === '1' || String(route.query.next || '').startsWith('/admin'),
)

const nextPath = computed(() => {
  const n = route.query.next
  return typeof n === 'string' && n.startsWith('/') ? n : ''
})

onMounted(() => {
  auth.hydrateFromStorage()
  if (!(auth.isLoggedIn || hasStoredAuth())) return

  if (wantAdmin.value) {
    if (auth.isAppAdmin) {
      router.replace(nextPath.value || '/admin')
      return
    }
    // Signed in as customer while trying to open Admin — clear so Admin can sign in
    auth.clear()
    return
  }

  router.replace(auth.isAppAdmin ? '/admin' : '/dashboard')
})

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const api = createApiClient()
    const { data } = await api.post<{
      access: string
      refresh: string
      is_app_admin?: boolean
    }>('/auth/login/', {
      email: email.value.trim().toLowerCase(),
      password: password.value,
    })
    auth.setTokens(data.access, data.refresh)
    if (data.is_app_admin) {
      auth.setAppAdminVerified(true)
    }

    const isAdmin = Boolean(data.is_app_admin) || auth.isAppAdmin

    if (wantAdmin.value) {
      if (!isAdmin) {
        auth.clear()
        error.value =
          'This account is not App Admin. Create one with: python manage.py createsuperuser'
        return
      }
      await router.push(nextPath.value || '/admin')
      return
    }

    await router.push(isAdmin ? '/admin' : '/dashboard')
  } catch (e: unknown) {
    const detail =
      e && typeof e === 'object' && 'response' in e
        ? (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : null
    error.value =
      typeof detail === 'string' && detail.toLowerCase().includes('disabled')
        ? detail
        : 'Invalid email or password.'
  } finally {
    loading.value = false
  }
}
</script>

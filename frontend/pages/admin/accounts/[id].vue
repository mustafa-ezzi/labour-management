<template>
  <div>
    <NuxtLink to="/admin/accounts" class="ui-link mb-4 inline-block">← Accounts</NuxtLink>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="loadErr" class="text-red-600">{{ loadErr }}</p>

    <template v-else-if="account">
      <div class="mb-5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 class="text-xl font-bold text-gray-900">{{ displayName }}</h2>
          <p class="text-sm text-gray-500">{{ account.email }}</p>
          <span
            class="mt-2 inline-block rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide"
            :class="
              account.is_active
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-amber-50 text-amber-700'
            "
          >
            {{ account.status }}
          </span>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-if="account.is_active"
            type="button"
            class="ui-btn-secondary py-2 text-xs"
            :disabled="busy"
            @click="disableAccount"
          >
            Disable
          </button>
          <button
            v-else
            type="button"
            class="ui-btn-primary py-2 text-xs"
            :disabled="busy"
            @click="enableAccount"
          >
            Enable
          </button>
        </div>
      </div>

      <p v-if="msg" class="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
        {{ msg }}
      </p>
      <p v-if="actionErr" class="mb-4 ui-error-banner">{{ actionErr }}</p>

      <div class="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div class="rounded-xl border border-gray-200 bg-white px-3 py-3">
          <p class="text-[10px] font-semibold uppercase text-gray-400">Sites</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums">{{ account.counts.sites }}</p>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white px-3 py-3">
          <p class="text-[10px] font-semibold uppercase text-gray-400">Workers</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums">{{ account.counts.workers }}</p>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white px-3 py-3">
          <p class="text-[10px] font-semibold uppercase text-gray-400">Materials</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums">{{ account.counts.materials }}</p>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white px-3 py-3">
          <p class="text-[10px] font-semibold uppercase text-gray-400">Plan</p>
          <p class="mt-0.5 text-sm font-bold capitalize">{{ account.subscription_plan }}</p>
        </div>
      </div>

      <UiCard class="mb-5">
        <p class="mb-3 text-sm font-semibold text-gray-900">Edit profile</p>
        <form class="space-y-3" @submit.prevent="save">
          <div>
            <label class="ui-label" for="email">Email</label>
            <input id="email" v-model="form.email" type="email" required class="ui-input" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="ui-label" for="first">First name</label>
              <input id="first" v-model="form.first_name" class="ui-input" />
            </div>
            <div>
              <label class="ui-label" for="last">Last name</label>
              <input id="last" v-model="form.last_name" class="ui-input" />
            </div>
          </div>
          <div>
            <label class="ui-label" for="company">Workspace name</label>
            <input id="company" v-model="form.company_name" class="ui-input" />
          </div>
          <button type="submit" class="ui-btn-primary w-full sm:w-auto" :disabled="busy">
            {{ busy ? 'Saving…' : 'Save changes' }}
          </button>
        </form>
      </UiCard>

      <UiCard class="mb-5 text-sm text-gray-600">
        <p><span class="font-semibold text-gray-800">Joined:</span> {{ formatWhen(account.date_joined) }}</p>
        <p class="mt-1"><span class="font-semibold text-gray-800">Last login:</span> {{ formatWhen(account.last_login) }}</p>
      </UiCard>

      <div class="rounded-xl border border-red-200 bg-red-50 p-4">
        <p class="text-sm font-bold text-red-800">Danger zone</p>
        <p class="mt-1 text-xs text-red-700">
          Permanently deletes this user and all sites, workers, attendance, materials, and payments.
          This cannot be undone.
        </p>
        <div class="mt-3">
          <label class="ui-label" for="confirm">
            Type <strong>{{ confirmHint }}</strong> to confirm
          </label>
          <input id="confirm" v-model="deleteConfirm" class="ui-input border-red-200" />
        </div>
        <button
          type="button"
          class="ui-btn-danger mt-3 w-full sm:w-auto"
          :disabled="busy || deleteConfirm !== confirmHint"
          @click="deleteAccount"
        >
          Delete entire account
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

type Account = {
  id: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  status: string
  subscription_plan: string
  date_joined: string | null
  last_login: string | null
  company: { id: string; name: string } | null
  counts: { sites: number; workers: number; materials: number; companies: number }
}

const route = useRoute()
const router = useRouter()
const api = createApiClient()

const account = ref<Account | null>(null)
const loading = ref(true)
const loadErr = ref('')
const actionErr = ref('')
const msg = ref('')
const busy = ref(false)
const deleteConfirm = ref('')

const form = reactive({
  email: '',
  first_name: '',
  last_name: '',
  company_name: '',
})

const userId = computed(() => String(route.params.id || ''))

const displayName = computed(() => {
  if (!account.value) return ''
  const n = `${account.value.first_name || ''} ${account.value.last_name || ''}`.trim()
  return n || account.value.email
})

const confirmHint = computed(() => account.value?.company?.name || 'DELETE')

function formatWhen(iso: string | null) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

function fillForm(a: Account) {
  form.email = a.email
  form.first_name = a.first_name || ''
  form.last_name = a.last_name || ''
  form.company_name = a.company?.name || ''
}

async function load() {
  loading.value = true
  loadErr.value = ''
  try {
    const { data } = await api.get<Account>(`/admin/accounts/${userId.value}/`)
    account.value = data
    fillForm(data)
  } catch {
    loadErr.value = 'Account not found.'
    account.value = null
  } finally {
    loading.value = false
  }
}

async function save() {
  busy.value = true
  actionErr.value = ''
  msg.value = ''
  try {
    const { data } = await api.patch<Account>(`/admin/accounts/${userId.value}/`, {
      email: form.email,
      first_name: form.first_name,
      last_name: form.last_name,
      company_name: form.company_name,
    })
    account.value = data
    fillForm(data)
    msg.value = 'Account updated.'
  } catch (e: unknown) {
    const detail =
      e && typeof e === 'object' && 'response' in e
        ? (e as { response?: { data?: Record<string, unknown> } }).response?.data
        : null
    if (detail && typeof detail.email === 'object') {
      actionErr.value = String((detail.email as string[])[0] || 'Could not save.')
    } else {
      actionErr.value = 'Could not save changes.'
    }
  } finally {
    busy.value = false
  }
}

async function disableAccount() {
  if (!confirm('Disable this account? They will not be able to sign in.')) return
  busy.value = true
  actionErr.value = ''
  msg.value = ''
  try {
    const { data } = await api.post<Account>(`/admin/accounts/${userId.value}/disable/`)
    account.value = data
    msg.value = 'Account disabled.'
  } catch {
    actionErr.value = 'Could not disable account.'
  } finally {
    busy.value = false
  }
}

async function enableAccount() {
  busy.value = true
  actionErr.value = ''
  msg.value = ''
  try {
    const { data } = await api.post<Account>(`/admin/accounts/${userId.value}/enable/`)
    account.value = data
    msg.value = 'Account enabled.'
  } catch {
    actionErr.value = 'Could not enable account.'
  } finally {
    busy.value = false
  }
}

async function deleteAccount() {
  if (deleteConfirm.value !== confirmHint.value) return
  if (!confirm('Delete this account and ALL related data forever?')) return
  busy.value = true
  actionErr.value = ''
  try {
    await api.delete(`/admin/accounts/${userId.value}/`, {
      data: { confirm: deleteConfirm.value },
    })
    await router.replace('/admin/accounts')
  } catch (e: unknown) {
    const detail =
      e && typeof e === 'object' && 'response' in e
        ? (e as { response?: { data?: { detail?: string; hint?: string } } }).response?.data
        : null
    actionErr.value = detail?.detail || detail?.hint || 'Could not delete account.'
  } finally {
    busy.value = false
  }
}

watch(userId, load, { immediate: true })
</script>

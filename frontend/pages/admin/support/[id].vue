<template>
  <div>
    <NuxtLink to="/admin/support" class="ui-link mb-4 inline-block">← Inbox</NuxtLink>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <template v-else-if="ticket">
      <div class="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 class="text-lg font-bold text-gray-900">{{ ticket.subject }}</h2>
          <p class="mt-1 text-xs text-gray-500">
            {{ ticket.company?.name }} · {{ ticket.created_by?.email }}
          </p>
        </div>
        <span
          class="rounded px-2 py-0.5 text-[10px] font-bold uppercase"
          :class="statusClass(ticket.status)"
        >
          {{ ticket.status }}
        </span>
      </div>

      <div class="mb-5 grid gap-3 lg:grid-cols-3">
        <div class="lg:col-span-2 space-y-3">
          <ul class="space-y-3">
            <li
              v-for="msg in ticket.messages"
              :key="msg.id"
              class="rounded-xl border px-4 py-3"
              :class="
                msg.is_admin_reply
                  ? 'border-violet-200 bg-violet-50'
                  : 'border-gray-200 bg-white'
              "
            >
              <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">
                {{ msg.is_admin_reply ? 'Admin' : msg.sender_email || 'User' }}
                · {{ formatWhen(msg.created_at) }}
              </p>
              <p class="mt-1 whitespace-pre-wrap text-sm text-gray-800">{{ msg.body }}</p>
            </li>
          </ul>

          <UiCard>
            <p v-if="msgErr" class="mb-2 text-sm text-red-600">{{ msgErr }}</p>
            <form class="space-y-3" @submit.prevent="reply">
              <textarea
                v-model="body"
                required
                rows="3"
                class="ui-input"
                placeholder="Reply as Admin…"
              />
              <button type="submit" class="ui-btn-primary" :disabled="busy">
                {{ busy ? 'Sending…' : 'Send reply' }}
              </button>
            </form>
          </UiCard>
        </div>

        <div class="space-y-3">
          <UiCard>
            <p class="text-sm font-semibold text-gray-900">Status</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <button
                v-for="s in statuses"
                :key="s"
                type="button"
                class="rounded-lg px-2.5 py-1.5 text-xs font-semibold"
                :class="
                  ticket.status === s
                    ? 'bg-violet-700 text-white'
                    : 'border border-gray-200 bg-white text-gray-600'
                "
                :disabled="busy"
                @click="setStatus(s)"
              >
                {{ s }}
              </button>
            </div>
          </UiCard>

          <UiCard v-if="ticket.subscription">
            <p class="text-sm font-semibold text-gray-900">Subscription</p>
            <p class="mt-1 text-sm text-gray-700 capitalize">
              {{ ticket.subscription.plan?.name }} · {{ ticket.subscription.status }}
            </p>
            <p class="mt-1 text-xs text-gray-500">
              Ends {{ formatDate(ticket.subscription.ends_at) }}
            </p>
            <NuxtLink to="/admin/subscriptions" class="ui-link mt-2 inline-block text-xs">
              Open subscriptions →
            </NuxtLink>
          </UiCard>

          <UiCard>
            <p class="text-sm font-semibold text-gray-900">Account</p>
            <p class="mt-1 text-xs text-gray-600">{{ ticket.created_by?.email }}</p>
            <NuxtLink to="/admin/accounts" class="ui-link mt-2 inline-block text-xs">
              Open accounts →
            </NuxtLink>
          </UiCard>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

type Msg = {
  id: string
  body: string
  is_admin_reply: boolean
  created_at: string
  sender_email: string | null
}

type Ticket = {
  id: string
  subject: string
  status: string
  updated_at: string
  messages: Msg[]
  company: { id: string; name: string } | null
  created_by: { email: string | null } | null
  subscription: {
    status: string
    ends_at: string
    plan: { name: string } | null
  } | null
}

const route = useRoute()
const api = createApiClient()
const ticket = ref<Ticket | null>(null)
const loading = ref(true)
const error = ref('')
const msgErr = ref('')
const busy = ref(false)
const body = ref('')

const statuses = ['open', 'pending', 'resolved', 'closed']
const ticketId = computed(() => String(route.params.id || ''))

function statusClass(s: string) {
  if (s === 'open') return 'bg-violet-50 text-violet-700'
  if (s === 'pending') return 'bg-amber-50 text-amber-800'
  if (s === 'resolved') return 'bg-emerald-50 text-emerald-700'
  return 'bg-gray-100 text-gray-600'
}

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString()
  } catch {
    return iso
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get<Ticket>(`/admin/support/tickets/${ticketId.value}/`)
    ticket.value = data
  } catch {
    error.value = 'Ticket not found.'
    ticket.value = null
  } finally {
    loading.value = false
  }
}

async function reply() {
  busy.value = true
  msgErr.value = ''
  try {
    const { data } = await api.post<Ticket>(
      `/admin/support/tickets/${ticketId.value}/messages/`,
      { body: body.value },
    )
    ticket.value = data
    body.value = ''
  } catch {
    msgErr.value = 'Could not send reply.'
  } finally {
    busy.value = false
  }
}

async function setStatus(s: string) {
  busy.value = true
  try {
    const { data } = await api.patch<Ticket>(`/admin/support/tickets/${ticketId.value}/`, {
      status: s,
    })
    ticket.value = data
  } catch {
    error.value = 'Could not update status.'
  } finally {
    busy.value = false
  }
}

watch(ticketId, load, { immediate: true })
</script>

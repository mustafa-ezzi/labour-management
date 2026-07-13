<template>
  <div>
    <NuxtLink to="/support" class="ui-link mb-4 inline-block">← Support</NuxtLink>

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <template v-else-if="ticket">
      <div class="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 class="text-lg font-bold text-gray-900">{{ ticket.subject }}</h2>
          <p class="mt-1 text-xs text-gray-500">Updated {{ formatWhen(ticket.updated_at) }}</p>
        </div>
        <span
          class="rounded px-2 py-0.5 text-[10px] font-bold uppercase"
          :class="statusClass(ticket.status)"
        >
          {{ ticket.status }}
        </span>
      </div>

      <ul class="mb-4 space-y-3">
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
            {{ msg.is_admin_reply ? 'LabourPro Admin' : 'You' }}
            · {{ formatWhen(msg.created_at) }}
          </p>
          <p class="mt-1 whitespace-pre-wrap text-sm text-gray-800">{{ msg.body }}</p>
        </li>
      </ul>

      <UiCard v-if="ticket.status !== 'closed'">
        <p v-if="replyErr" class="mb-2 text-sm text-red-600">{{ replyErr }}</p>
        <form class="space-y-3" @submit.prevent="reply">
          <textarea v-model="body" required rows="3" class="ui-input" placeholder="Write a reply…" />
          <button type="submit" class="ui-btn-primary" :disabled="busy">
            {{ busy ? 'Sending…' : 'Send reply' }}
          </button>
        </form>
      </UiCard>
      <p v-else class="text-sm text-gray-500">This ticket is closed.</p>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

type Msg = {
  id: string
  body: string
  is_admin_reply: boolean
  created_at: string
}

type Ticket = {
  id: string
  subject: string
  status: string
  updated_at: string
  messages: Msg[]
}

const route = useRoute()
const api = createApiClient()
const ticket = ref<Ticket | null>(null)
const loading = ref(true)
const error = ref('')
const replyErr = ref('')
const busy = ref(false)
const body = ref('')

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

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get<Ticket>(`/support/tickets/${ticketId.value}/`)
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
  replyErr.value = ''
  try {
    const { data } = await api.post<Ticket>(`/support/tickets/${ticketId.value}/messages/`, {
      body: body.value,
    })
    ticket.value = data
    body.value = ''
  } catch {
    replyErr.value = 'Could not send reply.'
  } finally {
    busy.value = false
  }
}

watch(ticketId, load, { immediate: true })
</script>

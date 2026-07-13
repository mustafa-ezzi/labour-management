<template>
  <div>
    <UiPageHeader title="Subscription" subtitle="Your plan and renewal date" />

    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <template v-else-if="sub">
      <div
        v-if="sub.is_expired"
        class="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
      >
        <p class="font-semibold">Your plan has ended</p>
        <p class="mt-1 text-amber-800">
          You can keep using LabourPro. Contact us to renew. An Admin only disables login from the
          admin panel if needed.
        </p>
      </div>
      <div
        v-else-if="sub.ending_soon"
        class="mb-4 rounded-xl border border-violet-200 bg-violet-50 px-4 py-3 text-sm text-violet-900"
      >
        <p class="font-semibold">Plan ending soon</p>
        <p class="mt-1">{{ sub.days_remaining }} day(s) left — contact LabourPro to renew.</p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <UiCard>
          <p class="ui-label">Plan</p>
          <p class="mt-1 text-lg font-bold text-gray-900">{{ sub.plan?.name }}</p>
          <p class="mt-1 text-xs capitalize text-gray-500">{{ sub.status }}</p>
        </UiCard>
        <UiCard>
          <p class="ui-label">Ends on</p>
          <p class="mt-1 text-lg font-bold tabular-nums text-gray-900">{{ formatDate(sub.ends_at) }}</p>
          <p v-if="!sub.is_expired" class="mt-1 text-xs text-gray-500">
            {{ sub.days_remaining }} day(s) remaining
          </p>
        </UiCard>
      </div>

      <UiCard class="mt-4">
        <p class="text-sm font-semibold text-gray-900">How to renew</p>
        <p class="mt-2 text-sm text-gray-600">
          Pay outside the app (bank / JazzCash / etc.), then ask LabourPro Admin to renew your plan.
          Support tickets arrive in a later update — for now contact your LabourPro contact directly.
        </p>
        <p class="mt-3 text-xs text-gray-400">
          Workspace: {{ sub.company_name }}
        </p>
      </UiCard>

      <div v-if="plans.length" class="mt-6">
        <h2 class="ui-label mb-3">Available plans</h2>
        <ul class="divide-y divide-gray-100 overflow-hidden rounded-xl border border-gray-200 bg-white">
          <li v-for="p in plans" :key="p.id" class="flex items-center justify-between px-4 py-3">
            <div>
              <p class="text-sm font-semibold text-gray-900">{{ p.name }}</p>
              <p class="text-xs text-gray-500">{{ p.duration_days }} days</p>
            </div>
            <p class="text-sm font-medium tabular-nums text-gray-700">
              {{ p.currency }} {{ p.price }}
            </p>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

type Plan = {
  id: string
  name: string
  price: string
  currency: string
  duration_days: number
}

type Sub = {
  company_name: string
  status: string
  ends_at: string
  days_remaining: number
  ending_soon: boolean
  is_expired: boolean
  plan: Plan | null
  message: string | null
}

const api = createApiClient()
const sub = ref<Sub | null>(null)
const plans = ref<Plan[]>([])
const loading = ref(true)
const error = ref('')

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return iso
  }
}

onMounted(async () => {
  try {
    const [meRes, plansRes] = await Promise.all([
      api.get<Sub>('/subscription/me/'),
      api.get<{ results: Plan[] }>('/subscription/plans/'),
    ])
    sub.value = meRes.data
    plans.value = plansRes.data.results.filter((p) => p.name)
  } catch {
    error.value = 'Could not load subscription.'
  } finally {
    loading.value = false
  }
})
</script>

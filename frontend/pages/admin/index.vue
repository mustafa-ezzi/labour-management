<template>
  <div>
    <p v-if="loading" class="ui-muted">Loading…</p>
    <p v-else-if="error" class="text-red-600">{{ error }}</p>
    <template v-else-if="stats">
      <p class="mb-5 text-sm text-gray-500">
        Whole-app overview. Plan expiry is alerts-only — disable login from Accounts when needed.
      </p>
      <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div class="rounded-xl border border-violet-200 bg-violet-50 px-4 py-4">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-violet-600">Users</p>
          <p class="mt-1 text-2xl font-bold tabular-nums text-violet-900">{{ stats.total_users }}</p>
          <p class="mt-0.5 text-xs text-gray-500">{{ stats.active_users }} active</p>
        </div>
        <div class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-4">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-amber-700">Disabled</p>
          <p class="mt-1 text-2xl font-bold tabular-nums text-amber-900">{{ stats.disabled_users }}</p>
        </div>
        <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-4">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-emerald-700">Active plans</p>
          <p class="mt-1 text-2xl font-bold tabular-nums text-emerald-900">
            {{ stats.active_subscriptions }}
          </p>
          <p class="mt-0.5 text-xs text-gray-500">{{ stats.expiring_this_week }} ending ≤7d</p>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white px-4 py-4">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Expired plans</p>
          <p class="mt-1 text-2xl font-bold tabular-nums text-gray-900">
            {{ stats.expired_subscriptions }}
          </p>
          <p class="mt-0.5 text-xs text-gray-400">{{ stats.open_support_tickets }} open tickets</p>
        </div>
      </div>

      <UiCard class="mt-6">
        <p class="text-sm font-semibold text-gray-900">Phase 3 live</p>
        <p class="mt-1 text-sm text-gray-600">
          Manage plans and renewals under Subscriptions. Ending a plan never auto-locks a user.
        </p>
        <div class="mt-3 flex flex-wrap gap-2">
          <NuxtLink to="/admin/subscriptions" class="ui-btn-primary py-2 text-xs">Subscriptions</NuxtLink>
          <NuxtLink to="/admin/plans" class="ui-btn-secondary py-2 text-xs">Plans</NuxtLink>
          <NuxtLink to="/admin/accounts" class="ui-btn-secondary py-2 text-xs">Accounts</NuxtLink>
        </div>
      </UiCard>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })

type Dashboard = {
  total_users: number
  active_users: number
  disabled_users: number
  total_companies: number
  open_support_tickets: number
  active_subscriptions: number
  expired_subscriptions: number
  expiring_this_week: number
}

const api = createApiClient()
const stats = ref<Dashboard | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get<Dashboard>('/admin/dashboard/')
    stats.value = data
  } catch {
    error.value = 'Could not load admin dashboard. Confirm you signed in as App Admin.'
  } finally {
    loading.value = false
  }
})
</script>

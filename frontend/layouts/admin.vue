<template>
  <div class="min-h-dvh bg-[#f7f5fc] text-gray-900 lg:flex">
    <aside class="hidden w-56 shrink-0 flex-col border-r border-[#e9e4f5] bg-white lg:flex">
      <div class="border-b border-[#e9e4f5] px-5 py-5">
        <p class="text-[10px] font-semibold uppercase tracking-widest text-violet-600">LabourPro</p>
        <p class="mt-0.5 text-sm font-bold text-gray-900">Admin</p>
      </div>
      <nav class="flex flex-1 flex-col gap-0.5 px-3 py-3">
        <NuxtLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="rounded-lg px-3 py-2.5 text-sm font-medium transition-colors"
          :class="
            isActive(item.to)
              ? 'bg-violet-700 text-white'
              : 'text-gray-600 hover:bg-violet-50 hover:text-violet-800'
          "
        >
          {{ item.label }}
        </NuxtLink>
      </nav>
      <div class="border-t border-[#e9e4f5] px-3 py-3">
        <p class="truncate px-3 text-xs text-gray-400">{{ adminEmail }}</p>
        <button
          type="button"
          class="mt-2 w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-gray-500 hover:bg-gray-100"
          @click="logout"
        >
          Sign out
        </button>
      </div>
    </aside>

    <div class="flex min-h-dvh min-w-0 flex-1 flex-col">
      <header class="border-b border-[#e9e4f5] bg-white px-4 py-3 lg:px-7">
        <div class="flex items-center justify-between gap-3">
          <div>
            <p class="text-[10px] font-semibold uppercase tracking-widest text-violet-600 lg:hidden">
              Admin
            </p>
            <h1 class="text-base font-bold text-gray-900">{{ pageTitle }}</h1>
          </div>
          <button
            type="button"
            class="rounded-lg px-3 py-1.5 text-xs font-semibold text-gray-500 hover:bg-gray-100 lg:hidden"
            @click="logout"
          >
            Sign out
          </button>
        </div>
        <nav class="mt-3 flex gap-1 overflow-x-auto lg:hidden">
          <NuxtLink
            v-for="item in nav"
            :key="item.to"
            :to="item.to"
            class="shrink-0 rounded-lg px-3 py-1.5 text-xs font-semibold"
            :class="
              isActive(item.to)
                ? 'bg-violet-100 text-violet-800'
                : 'bg-gray-50 text-gray-500'
            "
          >
            {{ item.label }}
          </NuxtLink>
        </nav>
      </header>

      <main class="mx-auto w-full max-w-6xl flex-1 px-4 py-5 lg:px-7 lg:py-7">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const auth = useAuthStore()
const router = useRouter()
const api = createApiClient()

const adminEmail = ref('')

const nav = [
  { to: '/admin', label: 'Dashboard' },
  { to: '/admin/accounts', label: 'Accounts' },
  { to: '/admin/subscriptions', label: 'Subscriptions' },
  { to: '/admin/plans', label: 'Plans' },
  { to: '/admin/support', label: 'Support' },
  { to: '/admin/audit', label: 'Audit' },
]

const pageTitle = computed(() => {
  const hit = nav.find((n) => isActive(n.to))
  return hit?.label || 'Admin'
})

function isActive(to: string) {
  if (to === '/admin') return route.path === '/admin' || route.path === '/admin/'
  return route.path === to || route.path.startsWith(`${to}/`)
}

async function logout() {
  auth.clear()
  await router.push('/login')
}

onMounted(async () => {
  try {
    const { data } = await api.get<{ user: { email: string } }>('/admin/me/')
    adminEmail.value = data.user.email
  } catch {
    adminEmail.value = ''
  }
})
</script>

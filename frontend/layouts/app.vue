<template>
  <div class="ui-app-bg lg:flex">
    <!-- Desktop sidebar -->
    <aside class="relative z-10 hidden w-56 shrink-0 flex-col border-r border-[#e9e4f5] bg-white lg:flex">
      <div class="flex items-center gap-3 border-b border-[#e9e4f5] px-5 py-5">
        <img src="/logo.png" alt="LabourPro" class="h-9 w-9 shrink-0 rounded-lg object-contain" />
        <span class="text-sm font-bold tracking-tight text-gray-900">LabourPro</span>
      </div>

      <nav class="flex flex-1 flex-col gap-0.5 px-3 py-3">
        <NuxtLink
          v-for="item in items"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150"
          :class="
            isActive(item)
              ? 'bg-violet-700 font-semibold text-white shadow-sm'
              : 'text-gray-600 hover:bg-violet-50 hover:text-violet-800'
          "
        >
          <AppNavIcon :name="item.icon" class="h-4 w-4 shrink-0" />
          {{ item.label }}
        </NuxtLink>
      </nav>

      <div class="mt-1 border-t border-[#e9e4f5] px-3 pb-5 pt-3">
        <button
          type="button"
          class="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-800"
          @click="logout"
        >
          <svg class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Sign out
        </button>
      </div>
    </aside>

    <div class="relative z-10 flex min-h-dvh min-w-0 flex-1 flex-col pb-[4.5rem] lg:pb-0">
      <header class="ui-header-bar">
        <div class="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-3 lg:px-7 lg:py-3.5">
          <div class="flex items-center gap-2.5 lg:hidden">
            <img src="/logo.png" alt="LabourPro" class="h-8 w-8 shrink-0 rounded-lg object-contain" />
            <span class="text-sm font-bold tracking-tight text-gray-900">LabourPro</span>
          </div>
          <div class="hidden lg:flex lg:items-center lg:gap-3">
            <p class="text-xs font-medium uppercase tracking-widest text-gray-400">
              Labour Management System
            </p>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="showInstallButton"
              type="button"
              class="rounded-lg bg-violet-700 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-violet-600"
              @click="triggerInstall"
            >
              Download
            </button>
            <button
              type="button"
              class="rounded-lg px-3 py-1.5 text-xs font-semibold text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-800"
              @click="logout"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main class="mx-auto w-full max-w-6xl flex-1 px-4 py-5 lg:px-7 lg:py-7">
        <slot />
      </main>

      <!-- Mobile bottom nav -->
      <nav
        class="fixed bottom-0 left-0 right-0 z-30 border-t border-[#e9e4f5] bg-white/95 backdrop-blur-md lg:hidden"
        style="padding-bottom: env(safe-area-inset-bottom, 0)"
      >
        <div class="mx-auto grid max-w-lg gap-px px-2 py-2" :class="bottomNavClass">
          <NuxtLink
            v-for="item in items"
            :key="item.to"
            :to="item.to"
            class="flex flex-col items-center gap-1 rounded-lg px-1 py-2.5 text-[10px] font-semibold uppercase tracking-wide transition-all"
            :class="
              isActive(item)
                ? 'bg-violet-50 text-violet-700'
                : 'text-gray-400 hover:text-gray-600'
            "
          >
            <span
              class="flex h-8 w-8 items-center justify-center rounded-lg transition-colors"
              :class="isActive(item) ? 'bg-violet-100 text-violet-700' : ''"
            >
              <AppNavIcon :name="item.icon" class="h-5 w-5" />
            </span>
            {{ item.shortLabel }}
          </NuxtLink>
        </div>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
const { items, bottomNavClass, isActive } = useAppNav()
const { showDownloadPopup, openModal } = usePwaInstall()
const auth = useAuthStore()
const router = useRouter()

const showInstallButton = computed(() => showDownloadPopup.value)

function triggerInstall() {
  openModal()
}

async function logout() {
  auth.clear()
  await router.push('/login')
}
</script>

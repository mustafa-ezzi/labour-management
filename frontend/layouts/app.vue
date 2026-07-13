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
          :data-tour="item.tourId"
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

    <div class="relative z-10 flex min-h-dvh min-w-0 flex-1 flex-col overflow-visible lg:pb-0" :class="mainPadClass">
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
              v-if="showDownloadPopup"
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

      <main class="mx-auto w-full max-w-6xl flex-1 overflow-visible px-4 py-5 lg:px-7 lg:py-7">
        <div
          v-if="showSubBanner && subInfo"
          class="mb-4 rounded-xl border px-4 py-3 text-sm"
          :class="
            subInfo.is_expired
              ? 'border-amber-200 bg-amber-50 text-amber-950'
              : 'border-violet-200 bg-violet-50 text-violet-950'
          "
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <p>
              <span class="font-semibold">
                {{ subInfo.is_expired ? 'Plan ended' : 'Plan ending soon' }}
              </span>
              — {{ subInfo.message || `${subInfo.days_remaining} day(s) left.` }}
              You can keep using the app.
            </p>
            <NuxtLink to="/subscription" class="shrink-0 text-xs font-bold underline">
              View plan
            </NuxtLink>
          </div>
        </div>
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
            :data-tour="item.tourId"
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

    <!-- Replay the guided tour anytime -->
    <button
      v-if="!tourActive && !modalOpen"
      type="button"
      class="fixed right-4 z-40 flex h-11 w-11 items-center justify-center rounded-full bg-violet-700 text-white shadow-lg shadow-violet-900/30 transition-transform hover:scale-105 active:scale-95 lg:bottom-6"
      :class="showPwaBanner ? 'bottom-[9.5rem]' : 'bottom-[5.5rem]'"
      aria-label="Replay app tour"
      @click="replayTour"
    >
      <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3s-1.79 3-4 3m0 3h.01M12 21a9 9 0 100-18 9 9 0 000 18z"
        />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { buildMainTourSteps } from '~/utils/tourSteps'

const { items, bottomNavClass, isActive } = useAppNav()
const { showDownloadPopup, canNativeInstall, install, openModal, bannerVisible, modalOpen } =
  usePwaInstall()
const { info: subInfo, showBanner: showSubBanner, refresh: refreshSub } = useSubscriptionBanner()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const { active: tourActive, start: startTour } = useOnboardingTour()
const { markMainTourDone } = useOnboardingFlags()

const showPwaBanner = computed(
  () => bannerVisible.value && showDownloadPopup.value && !modalOpen.value,
)

async function replayTour() {
  if (route.path !== '/dashboard') {
    await router.push('/dashboard')
    await nextTick()
  }
  await startTour(buildMainTourSteps(), { onFinish: markMainTourDone })
}

onMounted(() => {
  refreshSub()
})

watch(
  () => auth.accessToken,
  () => refreshSub(),
)

/** Extra bottom space so content clears nav + optional Download banner */
const mainPadClass = computed(() => {
  if (bannerVisible.value && showDownloadPopup.value && !modalOpen.value) {
    return 'pb-[9.5rem]'
  }
  return 'pb-[4.5rem]'
})

function triggerInstall() {
  if (canNativeInstall.value) {
    install()
    return
  }
  openModal()
}

async function logout() {
  clearLastSiteId()
  auth.clear()
  await router.push('/login')
}
</script>

<template>
  <!--
    Mobile  : deep-green gradient bg, glass cards, glass nav bars
    Desktop : forest-green bg (#174c2f), darker sidebar, solid-green active nav,
              white content cards — matches the LaborPro design reference
  -->
  <div
    class="min-h-dvh text-white lg:flex"
    style="background: linear-gradient(160deg, #0d2b1a 0%, #0f3520 50%, #0b2617 100%)"
  >
    <!-- ── Backdrop glow (mobile atmosphere) ────────────────── -->
    <div
      class="pointer-events-none fixed inset-0 z-0 lg:hidden"
      style="background: radial-gradient(ellipse 120% 60% at 50% 0%, rgba(22,163,74,0.15) 0%, transparent 70%)"
      aria-hidden="true"
    />

    <!-- ── Desktop sidebar ──────────────────────────────────── -->
    <aside
      class="relative z-10 hidden lg:flex lg:w-56 lg:shrink-0 lg:flex-col"
      style="background: #081f11; border-right: 1px solid rgba(255,255,255,0.07)"
    >
      <!-- Brand -->
      <div class="flex items-center gap-3 px-5 py-5" style="border-bottom: 1px solid rgba(255,255,255,0.07)">
        <span
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-green-600 text-xs font-black text-white"
          style="box-shadow: 0 2px 12px rgba(22,163,74,0.5)"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
          </svg>
        </span>
        <span class="text-sm font-bold tracking-tight text-white">LabourPro</span>
      </div>

      <!-- Nav -->
      <nav class="flex flex-1 flex-col gap-0.5 px-3 py-3">
        <NuxtLink
          v-for="item in items"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-white/55 transition-all duration-150 hover:bg-white/[0.07] hover:text-white"
          active-class="!bg-green-700 !text-white !font-semibold"
        >
          <AppNavIcon :name="item.icon" class="h-4 w-4 shrink-0" />
          {{ item.label }}
        </NuxtLink>
      </nav>

      <!-- Sign out -->
      <div class="px-3 pb-5" style="border-top: 1px solid rgba(255,255,255,0.07); padding-top: 12px; margin-top: 4px">
        <button
          type="button"
          class="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium text-white/40 transition-colors hover:bg-white/[0.06] hover:text-white/75"
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

    <!-- ── Main column ────────────────────────────────────── -->
    <div
      class="relative z-10 flex min-h-dvh min-w-0 flex-1 flex-col pb-[4.5rem] lg:pb-0"
      style="background: linear-gradient(160deg, #0d2b1a 0%, #0f3520 50%, #0b2617 100%); lg:background: #132d1b"
    >
      <!-- Top bar — glass always -->
      <header
        class="sticky top-0 z-20 backdrop-blur-2xl"
        style="
          background: rgba(8, 22, 12, 0.70);
          border-bottom: 1px solid rgba(255,255,255,0.07);
          -webkit-backdrop-filter: blur(24px);
        "
      >
        <div class="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-3 lg:px-7 lg:py-3.5">
          <!-- Mobile logo -->
          <div class="flex items-center gap-2.5 lg:hidden">
            <span
              class="flex h-8 w-8 items-center justify-center rounded-lg bg-green-600 text-[10px] font-black text-white"
              style="box-shadow: 0 2px 10px rgba(22,163,74,0.45)"
            >
              LP
            </span>
            <span class="text-sm font-bold tracking-tight text-white">LabourPro</span>
          </div>
          <!-- Desktop: page subtitle area -->
          <div class="hidden lg:flex lg:items-center lg:gap-3">
            <p class="text-xs font-medium uppercase tracking-widest text-white/30">
              Labour Management System
            </p>
          </div>
          <!-- Right: logout -->
          <button
            type="button"
            class="rounded-lg px-3 py-1.5 text-xs font-semibold text-white/40 transition-colors hover:bg-white/[0.07] hover:text-white/80"
            @click="logout"
          >
            Sign out
          </button>
        </div>
      </header>

      <!-- Page content -->
      <main class="mx-auto w-full max-w-6xl flex-1 px-4 py-5 lg:px-7 lg:py-7">
        <slot />
      </main>

      <!-- ── Mobile bottom nav — glassmorphism ───────────── -->
      <nav
        class="fixed bottom-0 left-0 right-0 z-30 lg:hidden"
        style="
          background: rgba(5, 16, 9, 0.82);
          border-top: 1px solid rgba(255,255,255,0.09);
          backdrop-filter: blur(28px);
          -webkit-backdrop-filter: blur(28px);
          padding-bottom: env(safe-area-inset-bottom, 0);
        "
      >
        <div class="mx-auto grid max-w-lg gap-px px-2 py-2" :class="bottomNavClass">
          <NuxtLink
            v-for="item in items"
            :key="item.to"
            :to="item.to"
            class="flex flex-col items-center gap-1 rounded-lg px-1 py-2.5 text-[10px] font-semibold uppercase tracking-wide text-white/35 transition-all"
            active-class="!text-green-400 !bg-green-500/10"
          >
            <AppNavIcon :name="item.icon" class="h-5 w-5" />
            {{ item.shortLabel }}
          </NuxtLink>
        </div>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
const { items, bottomNavClass } = useAppNav()
const auth = useAuthStore()
const router = useRouter()

async function logout() {
  auth.clear()
  await router.push('/login')
}
</script>

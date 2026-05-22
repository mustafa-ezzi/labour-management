<template>
  <div
    class="min-h-dvh text-white lg:grid lg:grid-cols-2"
    style="background: linear-gradient(160deg, #0d2b1a 0%, #0f3520 55%, #0b2617 100%)"
  >
    <!-- ── Left panel (desktop) ──────────────────────────── -->
    <aside
      class="relative hidden overflow-hidden lg:flex lg:flex-col lg:justify-between lg:p-12"
      style="background: #081f11; border-right: 1px solid rgba(255,255,255,0.07)"
    >
      <!-- Glow orb -->
      <div
        class="pointer-events-none absolute -left-16 top-1/3 h-96 w-96 rounded-full opacity-25"
        style="background: radial-gradient(circle, #22c55e 0%, transparent 70%); filter: blur(70px)"
        aria-hidden="true"
      />

      <!-- Brand + headline -->
      <div class="relative z-10">
        <div class="mb-10 flex items-center gap-3">
          <span
            class="flex h-10 w-10 items-center justify-center rounded-lg bg-green-600 text-sm font-black text-white"
            style="box-shadow: 0 4px 18px rgba(22,163,74,0.5)"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
            </svg>
          </span>
          <span class="text-base font-bold tracking-tight text-white">LabourPro</span>
        </div>
        <h1 class="max-w-xs text-3xl font-black leading-tight tracking-tight text-white">
          Labour management built for construction sites
        </h1>
        <p class="mt-4 max-w-sm text-sm leading-relaxed text-white/50">
          Track crew, daily attendance, wages, and payments — on mobile at the site or on desktop in the office.
        </p>
      </div>

      <!-- Features -->
      <ul class="relative z-10 space-y-3">
        <li v-for="feat in features" :key="feat" class="flex items-center gap-3 text-sm text-white/50">
          <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded bg-green-700/40 border border-green-600/40">
            <svg class="h-3 w-3 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
            </svg>
          </span>
          {{ feat }}
        </li>
      </ul>
    </aside>

    <!-- ── Right panel (form) ────────────────────────────── -->
    <main class="flex min-h-dvh flex-col justify-center px-5 py-10 sm:px-8 lg:px-14 lg:py-16">
      <!-- Mobile brand -->
      <div class="mb-8 flex items-center gap-2.5 lg:hidden">
        <span
          class="flex h-9 w-9 items-center justify-center rounded-lg bg-green-600 text-xs font-black text-white"
          style="box-shadow: 0 3px 12px rgba(22,163,74,0.45)"
        >LP</span>
        <span class="text-sm font-bold text-white">LabourPro</span>
      </div>

      <!-- Form wrapper — glass on mobile, bare on desktop -->
      <div
        class="w-full max-w-md rounded-xl border border-white/[0.10] p-6 shadow-2xl backdrop-blur-2xl sm:p-8 lg:border-0 lg:p-0 lg:shadow-none lg:backdrop-blur-none"
        style="background: rgba(255,255,255,0.05)"
        :style="{ background: 'rgba(255,255,255,0.05)' }"
      >
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const features = [
  'Multi-site & multi-worker support',
  'Wages carry forward until paid',
  'Bulk attendance & pay in seconds',
  'Company-scoped & fully secure',
]
</script>

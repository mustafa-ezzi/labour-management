<template>
  <div class="min-h-dvh bg-[#f7f5fc] text-gray-900 lg:grid lg:grid-cols-2">
    <!-- Desktop left panel -->
    <aside class="relative hidden overflow-hidden bg-violet-700 lg:flex lg:flex-col lg:justify-between lg:p-12">
      <div
        class="pointer-events-none absolute -left-16 top-1/3 h-96 w-96 rounded-full opacity-30"
        style="background: radial-gradient(circle, #a78bfa 0%, transparent 70%); filter: blur(70px)"
        aria-hidden="true"
      />

      <div class="relative z-10">
        <div class="mb-10 flex items-center gap-3">
          <span class="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-sm font-black text-violet-700 shadow-lg">
            LP
          </span>
          <span class="text-base font-bold tracking-tight text-white">LabourPro</span>
        </div>
        <h1 class="max-w-xs text-3xl font-black leading-tight tracking-tight text-white">
          Labour management built for construction sites
        </h1>
        <p class="mt-4 max-w-sm text-sm leading-relaxed text-violet-200">
          Track crew, daily attendance, wages, and payments — on mobile at the site or on desktop in the office.
        </p>
      </div>

      <ul class="relative z-10 space-y-3">
        <li v-for="feat in features" :key="feat" class="flex items-center gap-3 text-sm text-violet-100">
          <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded border border-violet-400/40 bg-violet-600/40">
            <svg class="h-3 w-3 text-violet-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
            </svg>
          </span>
          {{ feat }}
        </li>
      </ul>
    </aside>

    <!-- Auth form area -->
    <main class="flex min-h-dvh flex-col justify-center px-5 py-10 sm:px-8 lg:px-14 lg:py-16">
      <div class="mb-8 flex items-center gap-2.5 lg:hidden">
        <img src="/logo.png" alt="LabourPro" class="h-9 w-9 shrink-0 rounded-lg object-contain" />
        <span class="text-sm font-bold text-gray-900">LabourPro</span>
      </div>

      <div class="w-full max-w-md rounded-xl border border-[#e9e4f5] bg-white p-6 shadow-sm sm:p-8 lg:border-0 lg:bg-transparent lg:p-0 lg:shadow-none">
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

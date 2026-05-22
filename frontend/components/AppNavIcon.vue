<template>
  <svg
    v-if="name === 'home'"
    :class="iconClass"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    stroke-width="1.75"
    aria-hidden="true"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
    />
  </svg>
  <svg
    v-else-if="name === 'site'"
    :class="iconClass"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    stroke-width="1.75"
    aria-hidden="true"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
    />
  </svg>
  <svg
    v-else-if="name === 'crew'"
    :class="iconClass"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    stroke-width="1.75"
    aria-hidden="true"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
    />
  </svg>
  <svg
    v-else-if="name === 'pay'"
    :class="iconClass"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    stroke-width="1.75"
    aria-hidden="true"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
    />
  </svg>
  <svg
    v-else-if="name === 'materials'"
    :class="iconClass"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    stroke-width="1.75"
    aria-hidden="true"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
    />
  </svg>
  <svg
    v-else
    :class="iconClass"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    stroke-width="1.75"
    aria-hidden="true"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
    />
  </svg>
</template>

<script setup lang="ts">
import { computed, useAttrs } from 'vue'

const props = defineProps<{ name: string }>()
const attrs = useAttrs()

const iconClass = computed(() => {
  const extra = attrs.class
  const base = 'h-5 w-5 shrink-0'
  if (!extra) return base
  if (typeof extra === 'string') return `${base} ${extra}`
  return [base, extra]
})
</script>

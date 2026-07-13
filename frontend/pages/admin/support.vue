<template>
  <UiCard>
    <p class="text-sm font-semibold text-gray-900">Support</p>
    <p class="mt-1 text-sm text-gray-600">
      Support inbox lands in <strong>Phase 4</strong>.
    </p>
  </UiCard>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })
</script>

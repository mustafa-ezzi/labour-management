<template>
  <UiCard>
    <p class="text-sm font-semibold text-gray-900">Plans</p>
    <p class="mt-1 text-sm text-gray-600">
      Trial / monthly / yearly plan CRUD lands in <strong>Phase 3</strong>.
    </p>
  </UiCard>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })
</script>

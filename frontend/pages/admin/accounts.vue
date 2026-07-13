<template>
  <UiCard>
    <p class="text-sm font-semibold text-gray-900">Accounts</p>
    <p class="mt-1 text-sm text-gray-600">
      List, edit, disable, and delete users land in <strong>Phase 2</strong>.
    </p>
  </UiCard>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'admin'] })
</script>

<template>
  <div class="mb-5 flex flex-col gap-3 sm:mb-6 sm:flex-row sm:items-center sm:justify-between">
    <div>
      <h1 class="ui-page-title">{{ title }}</h1>
      <p v-if="subtitle" class="ui-muted mt-1">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.action" class="shrink-0">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>()
</script>

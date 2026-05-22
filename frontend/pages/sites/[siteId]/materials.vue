<template>
  <div>
    <div class="mb-2">
      <h2 class="ui-page-title text-lg lg:text-xl">Materials</h2>
      <p class="ui-muted mt-1">Consumption and costs for this site</p>
    </div>
    <MaterialsSubNav />
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })
</script>

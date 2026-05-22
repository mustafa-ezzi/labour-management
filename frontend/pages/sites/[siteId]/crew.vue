<template>
  <div>
    <div class="mb-2">
      <h2 class="ui-page-title text-lg lg:text-xl">Crew</h2>
      <p class="ui-muted mt-1">Workers and wages for this site</p>
    </div>
    <CrewSubNav />
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })
</script>

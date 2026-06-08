<template>
  <div>
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })
</script>

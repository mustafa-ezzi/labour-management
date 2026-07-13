<template>
  <!-- Remount layout when it changes (fixes Admin chrome sticking on /login). -->
  <NuxtLayout :key="layoutKey">
    <NuxtPage />
    <PwaInstallPrompt />
    <OnboardingTour />
  </NuxtLayout>
</template>

<script setup lang="ts">
const route = useRoute()

/** Force remount when leaving Admin → login/default (prevents sticky Admin chrome). */
const layoutKey = computed(() => String(route.meta.layout ?? 'default'))
</script>

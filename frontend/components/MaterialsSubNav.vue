<template>
  <nav
    class="-mt-1 mb-6 overflow-x-auto"
    :style="'border-bottom: 1px solid rgba(255,255,255,0.07)'"
    aria-label="Materials sections"
  >
    <div class="flex min-w-max gap-0.5 pb-px">
      <NuxtLink
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        class="relative rounded-t-lg px-4 py-2.5 text-sm font-semibold tracking-wide transition-colors"
        :class="
          isActive(tab)
            ? 'text-green-300 lg:text-green-700'
            : 'text-white/40 hover:bg-white/[0.05] hover:text-white/70 lg:text-gray-500 lg:hover:bg-gray-100/60 lg:hover:text-gray-700'
        "
      >
        {{ tab.label }}
        <span
          v-if="isActive(tab)"
          class="absolute bottom-0 left-0 right-0 h-[2px] rounded-full bg-green-400 lg:bg-green-600"
        />
      </NuxtLink>
    </div>
  </nav>
</template>

<script setup lang="ts">
import type { MaterialsTab } from '~/composables/useMaterialsNav'

const route = useRoute()
const { tabs } = useMaterialsNav()

function isActive(tab: MaterialsTab) {
  const path = route.path.replace(/\/$/, '') || route.path

  if (tab.section === 'usage') {
    return path.includes('/materials/usage')
  }
  return path.includes('/materials') && !path.includes('/materials/usage')
}
</script>

<template>
  <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
    <button
      type="button"
      class="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-violet-50/40"
      @click="open = !open"
    >
      <span v-if="icon" class="ui-icon-chip h-8 w-8">
        <AppNavIcon :name="icon" class="h-4 w-4" />
      </span>
      <span class="min-w-0 flex-1">
        <span class="block truncate text-sm font-semibold text-gray-900">{{ title }}</span>
        <span v-if="subtitle" class="block truncate text-xs text-gray-500">{{ subtitle }}</span>
      </span>
      <span v-if="$slots.summary" class="shrink-0 text-sm font-semibold text-gray-700">
        <slot name="summary" />
      </span>
      <AppNavIcon
        name="chevron-down"
        class="h-4 w-4 shrink-0 text-gray-400 transition-transform duration-200"
        :class="{ 'rotate-180': open }"
      />
    </button>
    <div v-show="open" class="border-t border-gray-100 bg-gray-50 px-4 py-3">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    title: string
    subtitle?: string
    icon?: string
    defaultOpen?: boolean
  }>(),
  { defaultOpen: false },
)

const open = ref(props.defaultOpen)
</script>

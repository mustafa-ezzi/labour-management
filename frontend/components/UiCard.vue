<template>
  <component :is="tag" :class="[hover ? 'ui-card-hover' : 'ui-card', $attrs.class]">
    <slot />
  </component>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    hover?: boolean
    tag?: string
  }>(),
  { hover: false, tag: 'div' },
)
</script>

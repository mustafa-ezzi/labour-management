<template>
  <Teleport to="body">
    <div
      v-if="showPrompt"
      class="fixed inset-x-0 z-50 px-4"
      :class="inAppLayout ? 'bottom-[4.75rem]' : 'bottom-4'"
      style="padding-bottom: env(safe-area-inset-bottom, 0)"
    >
      <div class="mx-auto max-w-lg overflow-hidden rounded-xl border border-violet-200 bg-white shadow-xl shadow-violet-900/10">
        <div class="flex items-start gap-3 p-4">
          <img src="/logo.png" alt="LabourPro" class="h-12 w-12 shrink-0 rounded-lg object-contain" />
          <div class="min-w-0 flex-1">
            <p class="text-sm font-bold text-gray-900">Install LabourPro</p>
            <p v-if="canNativeInstall" class="mt-0.5 text-xs text-gray-500">
              Add to your home screen for quick access on site.
            </p>
            <p v-else class="mt-0.5 text-xs text-gray-500">
              On iPhone: tap <span class="font-semibold text-violet-700">Share</span>, then
              <span class="font-semibold text-violet-700">Add to Home Screen</span>.
            </p>
          </div>
          <button
            type="button"
            class="shrink-0 rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="Dismiss install prompt"
            @click="dismiss"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex gap-2 border-t border-gray-100 bg-gray-50 px-4 py-3">
          <button
            v-if="canNativeInstall"
            type="button"
            class="ui-btn-primary flex-1 py-2.5"
            @click="installApp"
          >
            Install app
          </button>
          <button
            v-else
            type="button"
            class="ui-btn-primary flex-1 py-2.5"
            @click="showIosHelp = true"
          >
            How to install
          </button>
          <button type="button" class="ui-btn-secondary px-4 py-2.5" @click="dismiss">
            Not now
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="showIosHelp"
      class="fixed inset-0 z-[60] flex items-end justify-center bg-black/40 p-4 sm:items-center"
      @click.self="showIosHelp = false"
    >
      <div class="w-full max-w-sm rounded-xl bg-white p-5 shadow-2xl">
        <h2 class="text-base font-bold text-gray-900">Install on iPhone</h2>
        <ol class="mt-3 space-y-2 text-sm text-gray-600">
          <li>1. Tap the <strong>Share</strong> button in Safari (square with arrow).</li>
          <li>2. Scroll down and tap <strong>Add to Home Screen</strong>.</li>
          <li>3. Tap <strong>Add</strong> in the top right.</li>
        </ol>
        <button type="button" class="ui-btn-primary mt-4 w-full" @click="showIosHelp = false">
          Got it
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    inAppLayout?: boolean
  }>(),
  { inAppLayout: false },
)

const { showPrompt, canNativeInstall, install, dismiss } = usePwaInstall()
const showIosHelp = ref(false)

async function installApp() {
  const ok = await install()
  if (ok) showIosHelp.value = false
}
</script>

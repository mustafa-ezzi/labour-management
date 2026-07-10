<template>
  <Teleport to="body">
    <div
      v-if="modalOpen && showDownloadPopup"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="pwa-download-title"
      @click.self="closeModal"
    >
      <div class="relative w-full max-w-sm overflow-hidden rounded-2xl bg-white shadow-2xl">
        <button
          type="button"
          class="absolute right-3 top-3 z-10 rounded-full p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          aria-label="Close"
          @click="closeModal"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div class="bg-gradient-to-br from-violet-700 to-violet-900 px-6 pb-8 pt-10 text-center">
          <img
            src="/logo.png"
            alt="LabourPro"
            class="mx-auto h-20 w-20 rounded-2xl bg-white p-2 object-contain shadow-lg"
          />
          <h2 id="pwa-download-title" class="mt-4 text-xl font-bold text-white">Install LabourPro</h2>
          <p class="mt-1 text-sm text-violet-200">Add the app to your home screen</p>
        </div>

        <div class="space-y-3 px-6 py-5">
          <!-- iOS: inline steps (Apple does not allow one-tap install) -->
          <ol v-if="isIos" class="space-y-2 text-sm text-gray-700">
            <li class="flex gap-2">
              <span class="font-bold text-violet-700">1.</span>
              Tap <strong>Share</strong> in Safari (bottom bar)
            </li>
            <li class="flex gap-2">
              <span class="font-bold text-violet-700">2.</span>
              Tap <strong>Add to Home Screen</strong>
            </li>
            <li class="flex gap-2">
              <span class="font-bold text-violet-700">3.</span>
              Tap <strong>Add</strong>
            </li>
          </ol>

          <ul v-else class="space-y-2 text-sm text-gray-600">
            <li class="flex items-center gap-2">
              <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-700">✓</span>
              One tap install — no app store needed
            </li>
            <li class="flex items-center gap-2">
              <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-700">✓</span>
              Opens from your home screen
            </li>
          </ul>

          <p v-if="installError" class="text-center text-sm text-red-600">{{ installError }}</p>

          <!-- Android / Chrome: direct native install -->
          <button
            v-if="!isIos"
            type="button"
            class="ui-btn-primary w-full py-3.5 text-base"
            :disabled="installing || !canNativeInstall"
            @click="installNow"
          >
            <span v-if="installing" class="flex items-center justify-center gap-2">
              <svg class="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 100 16z" />
              </svg>
              Installing…
            </span>
            <span v-else-if="canNativeInstall">Install app</span>
            <span v-else>Preparing install…</span>
          </button>

          <button
            v-else
            type="button"
            class="ui-btn-primary w-full py-3.5 text-base"
            @click="dismiss"
          >
            Got it
          </button>

          <button
            type="button"
            class="w-full py-2 text-center text-sm font-medium text-gray-500 hover:text-gray-700"
            @click="dismiss"
          >
            Continue in browser
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const {
  showDownloadPopup,
  modalOpen,
  canNativeInstall,
  isIos,
  installing,
  install,
  dismiss,
  closeModal,
} = usePwaInstall()

const installError = ref('')

function installNow() {
  installError.value = ''
  if (!canNativeInstall.value) return
  install().then((ok) => {
    if (!ok) installError.value = 'Install was cancelled. Tap Install app to try again.'
  })
}
</script>

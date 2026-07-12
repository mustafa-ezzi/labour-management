<template>
  <Teleport to="body">
    <div
      v-if="bannerVisible && showDownloadPopup && !modalOpen"
      class="fixed inset-x-0 z-[90] px-3"
      style="bottom: calc(4.5rem + env(safe-area-inset-bottom, 0px))"
    >
      <div class="mx-auto flex max-w-lg items-center gap-3 rounded-2xl border border-violet-200 bg-white p-3 shadow-xl shadow-violet-900/15">
        <img src="/logo.png" alt="" class="h-11 w-11 shrink-0 rounded-xl object-contain" />
        <div class="min-w-0 flex-1">
          <p class="text-sm font-bold text-gray-900">Download LabourPro</p>
          <p class="text-[11px] text-gray-500">Add to your home screen</p>
        </div>
        <button
          type="button"
          class="shrink-0 rounded-xl bg-violet-700 px-3.5 py-2 text-xs font-bold text-white shadow-sm hover:bg-violet-600"
          @click="openModal"
        >
          Download
        </button>
        <button
          type="button"
          class="shrink-0 rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          aria-label="Hide"
          @click="hideBanner"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <div
      v-if="modalOpen && showDownloadPopup"
      class="fixed inset-0 z-[100] flex items-end justify-center bg-black/50 p-0 backdrop-blur-sm sm:items-center sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="pwa-download-title"
      @click.self="closeModal"
    >
      <div class="relative w-full max-w-sm overflow-hidden rounded-t-3xl bg-white shadow-2xl sm:rounded-2xl">
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
            src="/pwa-192.png"
            alt="LabourPro"
            class="mx-auto h-20 w-20 rounded-2xl bg-white p-2 object-contain shadow-lg"
          />
          <h2 id="pwa-download-title" class="mt-4 text-xl font-bold text-white">Download LabourPro</h2>
          <p class="mt-1 text-sm text-violet-200">Install on your phone home screen</p>
        </div>

        <div class="space-y-3 px-6 py-5">
          <!-- iPhone -->
          <template v-if="isIos">
            <ol class="space-y-2.5 text-sm text-gray-700">
              <li class="flex gap-2">
                <span class="font-bold text-violet-700">1.</span>
                Tap <strong>Share</strong> in Safari
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
            <button type="button" class="ui-btn-primary w-full py-3.5 text-base" @click="dismiss">
              Got it
            </button>
          </template>

          <!-- Android / other: one-tap when ready, else clear manual steps -->
          <template v-else>
            <template v-if="canNativeInstall">
              <ul class="space-y-2 text-sm text-gray-600">
                <li class="flex items-center gap-2">
                  <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-100 text-xs text-violet-700">✓</span>
                  One tap — no Play Store needed
                </li>
                <li class="flex items-center gap-2">
                  <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-100 text-xs text-violet-700">✓</span>
                  Opens from your home screen
                </li>
              </ul>
              <p v-if="installError" class="text-center text-sm text-red-600">{{ installError }}</p>
              <button
                type="button"
                class="ui-btn-primary w-full py-3.5 text-base"
                :disabled="installing"
                @click="installNow"
              >
                <span v-if="installing">Installing…</span>
                <span v-else>Download &amp; Install</span>
              </button>
            </template>

            <template v-else-if="!promptTimedOut">
              <p class="text-center text-sm text-gray-600">Checking if your browser can install apps…</p>
              <button type="button" class="ui-btn-primary w-full py-3.5 text-base" disabled>
                Preparing install…
              </button>
            </template>

            <template v-else>
              <p class="text-sm text-gray-700">
                Your browser needs a quick menu install (this is normal on some phones):
              </p>
              <ol class="space-y-2.5 text-sm text-gray-700">
                <li class="flex gap-2">
                  <span class="font-bold text-violet-700">1.</span>
                  Tap the <strong>⋮</strong> menu (top right in Chrome)
                </li>
                <li class="flex gap-2">
                  <span class="font-bold text-violet-700">2.</span>
                  Tap <strong>Install app</strong> or <strong>Add to Home screen</strong>
                </li>
                <li class="flex gap-2">
                  <span class="font-bold text-violet-700">3.</span>
                  Confirm <strong>Install</strong>
                </li>
              </ol>
              <button type="button" class="ui-btn-primary w-full py-3.5 text-base" @click="dismiss">
                Got it
              </button>
              <p class="text-center text-[11px] text-gray-400">
                Best on <strong>Chrome</strong> or <strong>Edge</strong>. In-app browsers (WhatsApp, Facebook) often block install.
              </p>
            </template>
          </template>

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
  promptTimedOut,
  isIos,
  installing,
  bannerVisible,
  install,
  dismiss,
  closeModal,
  openModal,
  hideBanner,
} = usePwaInstall()

const installError = ref('')

function installNow() {
  installError.value = ''
  if (!canNativeInstall.value) return
  install().then((ok) => {
    if (!ok) installError.value = 'Install was cancelled. Tap again to retry.'
  })
}
</script>

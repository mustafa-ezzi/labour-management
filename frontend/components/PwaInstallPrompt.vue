<template>
  <Teleport to="body">
    <!-- Sticky Download banner -->
    <div
      v-if="bannerVisible && showDownloadPopup && !modalOpen"
      class="fixed inset-x-0 z-[90] px-3"
      style="bottom: calc(4.5rem + env(safe-area-inset-bottom, 0px))"
    >
      <div class="mx-auto flex max-w-lg items-center gap-3 rounded-2xl border border-violet-200 bg-white p-3 shadow-xl shadow-violet-900/15">
        <img src="/logo.png" alt="" class="h-11 w-11 shrink-0 rounded-xl object-contain" />
        <div class="min-w-0 flex-1">
          <p class="text-sm font-bold text-gray-900">Download LabourPro</p>
          <p class="text-[11px] text-gray-500">Install for quick access from your home screen</p>
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

    <!-- Full install popup -->
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
            src="/logo.png"
            alt="LabourPro"
            class="mx-auto h-20 w-20 rounded-2xl bg-white p-2 object-contain shadow-lg"
          />
          <h2 id="pwa-download-title" class="mt-4 text-xl font-bold text-white">Download LabourPro</h2>
          <p class="mt-1 text-sm text-violet-200">Install the app on your phone</p>
        </div>

        <div class="space-y-3 px-6 py-5">
          <template v-if="isIos">
            <ol class="space-y-2.5 text-sm text-gray-700">
              <li class="flex gap-2">
                <span class="font-bold text-violet-700">1.</span>
                Tap the <strong>Share</strong> button in Safari
              </li>
              <li class="flex gap-2">
                <span class="font-bold text-violet-700">2.</span>
                Scroll and tap <strong>Add to Home Screen</strong>
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

          <template v-else>
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
            <p v-else-if="!canNativeInstall" class="text-center text-xs text-gray-500">
              Preparing install… If the button stays disabled, open this site in <strong>Chrome</strong>, then tap again.
            </p>

            <button
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
              <span v-else-if="canNativeInstall">Download &amp; Install</span>
              <span v-else>Preparing install…</span>
            </button>

            <p v-if="!canNativeInstall" class="text-center text-[11px] leading-relaxed text-gray-400">
              Or Chrome menu (⋮) → <strong>Install app</strong> / Add to Home screen
            </p>
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
    if (!ok) {
      installError.value = 'Install was cancelled. Tap Download & Install to try again.'
    }
  })
}
</script>

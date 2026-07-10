<template>
  <Teleport to="body">
    <!-- Main download popup -->
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
          <h2 id="pwa-download-title" class="mt-4 text-xl font-bold text-white">Download LabourPro</h2>
          <p class="mt-1 text-sm text-violet-200">Install the app on your phone for quick site access</p>
        </div>

        <div class="space-y-3 px-6 py-5">
          <ul class="space-y-2 text-sm text-gray-600">
            <li class="flex items-center gap-2">
              <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-700">✓</span>
              Works offline on site
            </li>
            <li class="flex items-center gap-2">
              <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-700">✓</span>
              One-tap from home screen
            </li>
            <li class="flex items-center gap-2">
              <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-700">✓</span>
              Daily wages &amp; crew in seconds
            </li>
          </ul>

          <button
            type="button"
            class="ui-btn-primary w-full py-3.5 text-base"
            :disabled="installing"
            @click="downloadApp"
          >
            <span v-if="installing" class="flex items-center justify-center gap-2">
              <svg class="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 100 16z" />
              </svg>
              Downloading…
            </span>
            <span v-else>Download app</span>
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

    <!-- iOS install steps -->
    <div
      v-if="showIosHelp"
      class="fixed inset-0 z-[110] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
      @click.self="showIosHelp = false"
    >
      <div class="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
        <h2 class="text-lg font-bold text-gray-900">Download on iPhone</h2>
        <p class="mt-1 text-sm text-gray-500">Follow these steps to install LabourPro:</p>
        <ol class="mt-4 space-y-3 text-sm text-gray-700">
          <li class="flex gap-3">
            <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-violet-700 text-xs font-bold text-white">1</span>
            <span>Tap the <strong>Share</strong> button at the bottom of Safari</span>
          </li>
          <li class="flex gap-3">
            <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-violet-700 text-xs font-bold text-white">2</span>
            <span>Scroll and tap <strong>Add to Home Screen</strong></span>
          </li>
          <li class="flex gap-3">
            <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-violet-700 text-xs font-bold text-white">3</span>
            <span>Tap <strong>Add</strong> — LabourPro will appear on your home screen</span>
          </li>
        </ol>
        <button type="button" class="ui-btn-primary mt-5 w-full" @click="showIosHelp = false">
          Got it
        </button>
      </div>
    </div>

    <!-- Android: waiting for install prompt -->
    <div
      v-if="showAndroidHelp"
      class="fixed inset-0 z-[110] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
      @click.self="showAndroidHelp = false"
    >
      <div class="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
        <h2 class="text-lg font-bold text-gray-900">Install LabourPro</h2>
        <p class="mt-2 text-sm text-gray-600">
          Open this site in <strong>Chrome</strong>, then tap the menu (⋮) and choose
          <strong>Install app</strong> or <strong>Add to Home screen</strong>.
        </p>
        <button type="button" class="ui-btn-primary mt-5 w-full" @click="showAndroidHelp = false">
          OK
        </button>
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
  openModal,
} = usePwaInstall()

const showIosHelp = ref(false)
const showAndroidHelp = ref(false)
const autoOpened = useState('pwa-auto-opened', () => false)

onMounted(() => {
  if (!showDownloadPopup.value || autoOpened.value) return
  autoOpened.value = true
  window.setTimeout(() => {
    openModal()
  }, 800)
})

async function downloadApp() {
  if (isIos.value) {
    showIosHelp.value = true
    return
  }
  if (canNativeInstall.value) {
    const ok = await install()
    if (!ok) closeModal()
    return
  }
  showAndroidHelp.value = true
}
</script>

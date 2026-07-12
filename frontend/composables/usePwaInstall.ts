type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

type PwaWindow = Window & {
  __pwaInit?: boolean
  __bip?: BeforeInstallPromptEvent | null
  __bipListener?: boolean
}

const DISMISS_UNTIL_KEY = 'labourpro-pwa-dismiss-until'
const OLD_DISMISS_KEY = 'labourpro-pwa-install-dismissed'
const DISMISS_DAYS = 3

function detectStandalone(): boolean {
  if (!import.meta.client) return false
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as Navigator & { standalone?: boolean }).standalone === true
  )
}

function detectIos(): boolean {
  if (!import.meta.client) return false
  return /iphone|ipad|ipod/i.test(window.navigator.userAgent)
}

function detectAndroid(): boolean {
  if (!import.meta.client) return false
  return /android/i.test(window.navigator.userAgent)
}

function detectMobile(): boolean {
  if (!import.meta.client) return false
  return (
    /android|iphone|ipad|ipod|mobile/i.test(window.navigator.userAgent) ||
    window.matchMedia('(max-width: 1023px)').matches
  )
}

function readDismissed(): boolean {
  if (!import.meta.client) return false
  if (localStorage.getItem(OLD_DISMISS_KEY) === '1') {
    localStorage.removeItem(OLD_DISMISS_KEY)
  }
  const until = localStorage.getItem(DISMISS_UNTIL_KEY)
  if (until && Date.now() < Number(until)) return true
  return false
}

/** Capture beforeinstallprompt as early as possible (before Vue hydrates). */
export function captureInstallPromptEarly() {
  if (!import.meta.client) return
  const w = window as PwaWindow
  if (w.__bipListener) return
  w.__bipListener = true
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault()
    w.__bip = event as BeforeInstallPromptEvent
    window.dispatchEvent(new CustomEvent('labourpro:bip'))
  })
}

export function usePwaInstall() {
  const deferredPrompt = useState<BeforeInstallPromptEvent | null>('pwa-deferred-prompt', () => null)
  const dismissed = useState('pwa-install-dismissed', () => false)
  const isInstalled = useState('pwa-is-installed', () => false)
  const isIos = useState('pwa-is-ios', () => false)
  const isAndroid = useState('pwa-is-android', () => false)
  const isMobile = useState('pwa-is-mobile', () => false)
  const modalOpen = useState('pwa-modal-open', () => false)
  const installing = useState('pwa-installing', () => false)
  const installReady = useState('pwa-install-ready', () => false)
  const bannerVisible = useState('pwa-banner-visible', () => false)
  /** True after we stop waiting for Chrome's install event. */
  const promptTimedOut = useState('pwa-prompt-timed-out', () => false)

  const canNativeInstall = computed(() => !!deferredPrompt.value)

  const showDownloadPopup = computed(() => {
    if (!import.meta.client) return false
    if (isInstalled.value) return false
    return isMobile.value
  })

  const showAutoPopup = computed(() => showDownloadPopup.value && !dismissed.value)
  const showPrompt = showDownloadPopup

  function adoptPrompt(event: BeforeInstallPromptEvent | null | undefined) {
    if (!event) return
    deferredPrompt.value = event
    installReady.value = true
    promptTimedOut.value = false
  }

  function onInstallPrompt(event: Event) {
    event.preventDefault()
    adoptPrompt(event as BeforeInstallPromptEvent)
  }

  function syncFromWindow() {
    const w = window as PwaWindow
    if (w.__bip) adoptPrompt(w.__bip)
  }

  function init() {
    if (!import.meta.client || (window as PwaWindow).__pwaInit) return
    ;(window as PwaWindow).__pwaInit = true

    captureInstallPromptEarly()

    isInstalled.value = detectStandalone()
    isIos.value = detectIos() && !isInstalled.value
    isAndroid.value = detectAndroid() && !isInstalled.value
    isMobile.value = detectMobile() && !isInstalled.value
    dismissed.value = readDismissed()

    window.addEventListener('beforeinstallprompt', onInstallPrompt)
    window.addEventListener('labourpro:bip', () => syncFromWindow())
    syncFromWindow()

    window.addEventListener('appinstalled', () => {
      isInstalled.value = true
      deferredPrompt.value = null
      ;(window as PwaWindow).__bip = null
      installReady.value = false
      modalOpen.value = false
      installing.value = false
      bannerVisible.value = false
      localStorage.removeItem(DISMISS_UNTIL_KEY)
      localStorage.removeItem(OLD_DISMISS_KEY)
    })

    // Don't leave "Preparing…" forever — after 2.5s show manual install.
    window.setTimeout(() => {
      if (!deferredPrompt.value) promptTimedOut.value = true
    }, 2500)

    if (isMobile.value && !isInstalled.value) {
      bannerVisible.value = true
      if (!dismissed.value) {
        window.setTimeout(() => openModal(), 900)
      }
    }
  }

  function openModal() {
    if (!isInstalled.value) {
      syncFromWindow()
      modalOpen.value = true
    }
  }

  function closeModal() {
    modalOpen.value = false
  }

  function install(): Promise<boolean> {
    syncFromWindow()
    const event = deferredPrompt.value || (window as PwaWindow).__bip || null
    if (!event) return Promise.resolve(false)

    installing.value = true
    event.prompt()

    return event.userChoice
      .then(({ outcome }) => {
        deferredPrompt.value = null
        ;(window as PwaWindow).__bip = null
        installReady.value = false
        if (outcome === 'accepted') {
          isInstalled.value = true
          modalOpen.value = false
          bannerVisible.value = false
          return true
        }
        return false
      })
      .catch(() => false)
      .finally(() => {
        installing.value = false
      })
  }

  function dismiss() {
    dismissed.value = true
    modalOpen.value = false
    if (import.meta.client) {
      const untilTs = Date.now() + DISMISS_DAYS * 24 * 60 * 60 * 1000
      localStorage.setItem(DISMISS_UNTIL_KEY, String(untilTs))
    }
  }

  function hideBanner() {
    bannerVisible.value = false
  }

  return {
    canNativeInstall,
    showDownloadPopup,
    showAutoPopup,
    showPrompt,
    isInstalled,
    isIos,
    isAndroid,
    isMobile,
    modalOpen,
    installing,
    installReady,
    bannerVisible,
    promptTimedOut,
    init,
    openModal,
    closeModal,
    install,
    dismiss,
    hideBanner,
  }
}

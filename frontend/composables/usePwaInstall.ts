type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
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
  // Clear old permanent dismiss so the new Download popup can appear again.
  if (localStorage.getItem(OLD_DISMISS_KEY) === '1') {
    localStorage.removeItem(OLD_DISMISS_KEY)
  }
  const until = localStorage.getItem(DISMISS_UNTIL_KEY)
  if (until && Date.now() < Number(until)) return true
  return false
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

  const canNativeInstall = computed(() => !!deferredPrompt.value)

  /** Show popup / Download controls on mobile when not already installed. */
  const showDownloadPopup = computed(() => {
    if (!import.meta.client) return false
    if (isInstalled.value) return false
    return isMobile.value
  })

  /** Soft-dismissed for a few days — still allow header Download button. */
  const showAutoPopup = computed(() => showDownloadPopup.value && !dismissed.value)

  /** @deprecated use showDownloadPopup */
  const showPrompt = showDownloadPopup

  function onInstallPrompt(event: Event) {
    event.preventDefault()
    deferredPrompt.value = event as BeforeInstallPromptEvent
    installReady.value = true
    // If the download popup is already open, user can tap Install immediately.
  }

  function init() {
    if (!import.meta.client || (window as Window & { __pwaInit?: boolean }).__pwaInit) return
    ;(window as Window & { __pwaInit?: boolean }).__pwaInit = true

    isInstalled.value = detectStandalone()
    isIos.value = detectIos() && !isInstalled.value
    isAndroid.value = detectAndroid() && !isInstalled.value
    isMobile.value = detectMobile() && !isInstalled.value
    dismissed.value = readDismissed()

    window.addEventListener('beforeinstallprompt', onInstallPrompt)

    window.addEventListener('appinstalled', () => {
      isInstalled.value = true
      deferredPrompt.value = null
      installReady.value = false
      modalOpen.value = false
      installing.value = false
      bannerVisible.value = false
      localStorage.removeItem(DISMISS_UNTIL_KEY)
      localStorage.removeItem(OLD_DISMISS_KEY)
    })

    // Always offer Download on mobile (popup + sticky banner).
    if (isMobile.value && !isInstalled.value) {
      bannerVisible.value = true
      if (!dismissed.value) {
        window.setTimeout(() => openModal(), 900)
      }
    }
  }

  function openModal() {
    if (!isInstalled.value) modalOpen.value = true
  }

  function closeModal() {
    modalOpen.value = false
  }

  /**
   * One-tap native install (Android Chrome / Edge / Samsung Internet).
   * prompt() must run from the user click — do not await before calling it.
   */
  function install(): Promise<boolean> {
    const event = deferredPrompt.value
    if (!event) return Promise.resolve(false)

    installing.value = true
    event.prompt()

    return event.userChoice
      .then(({ outcome }) => {
        deferredPrompt.value = null
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
    init,
    openModal,
    closeModal,
    install,
    dismiss,
    hideBanner,
  }
}

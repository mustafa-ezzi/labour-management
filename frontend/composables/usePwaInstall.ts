type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

const DISMISS_KEY = 'labourpro-pwa-install-dismissed'

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

function detectMobile(): boolean {
  if (!import.meta.client) return false
  return (
    /android|iphone|ipad|ipod|mobile/i.test(window.navigator.userAgent) ||
    window.matchMedia('(max-width: 1023px)').matches
  )
}

export function usePwaInstall() {
  const deferredPrompt = useState<BeforeInstallPromptEvent | null>('pwa-deferred-prompt', () => null)
  const dismissed = useState('pwa-install-dismissed', () => false)
  const isInstalled = useState('pwa-is-installed', () => false)
  const isIos = useState('pwa-is-ios', () => false)
  const isMobile = useState('pwa-is-mobile', () => false)
  const modalOpen = useState('pwa-modal-open', () => false)
  const installing = useState('pwa-installing', () => false)

  const canNativeInstall = computed(() => !!deferredPrompt.value)
  const showDownloadPopup = computed(() => {
    if (!import.meta.client) return false
    if (isInstalled.value) return false
    if (dismissed.value) return false
    return isMobile.value
  })

  /** @deprecated use showDownloadPopup */
  const showPrompt = showDownloadPopup

  function init() {
    if (!import.meta.client || (window as Window & { __pwaInit?: boolean }).__pwaInit) return
    ;(window as Window & { __pwaInit?: boolean }).__pwaInit = true

    isInstalled.value = detectStandalone()
    isIos.value = detectIos() && !isInstalled.value
    isMobile.value = detectMobile() && !isInstalled.value
    dismissed.value = localStorage.getItem(DISMISS_KEY) === '1'

    window.addEventListener('beforeinstallprompt', (event) => {
      event.preventDefault()
      deferredPrompt.value = event as BeforeInstallPromptEvent
    })

    window.addEventListener('appinstalled', () => {
      isInstalled.value = true
      deferredPrompt.value = null
      modalOpen.value = false
      installing.value = false
    })
  }

  function openModal() {
    if (!isInstalled.value) modalOpen.value = true
  }

  function closeModal() {
    modalOpen.value = false
  }

  async function install(): Promise<boolean> {
    if (isIos.value) {
      return false
    }
    if (!deferredPrompt.value) {
      return false
    }
    installing.value = true
    try {
      await deferredPrompt.value.prompt()
      const { outcome } = await deferredPrompt.value.userChoice
      deferredPrompt.value = null
      if (outcome === 'accepted') {
        isInstalled.value = true
        modalOpen.value = false
        return true
      }
      return false
    } finally {
      installing.value = false
    }
  }

  function dismiss() {
    dismissed.value = true
    modalOpen.value = false
    if (import.meta.client) {
      localStorage.setItem(DISMISS_KEY, '1')
    }
  }

  return {
    canNativeInstall,
    showDownloadPopup,
    showPrompt,
    isInstalled,
    isIos,
    isMobile,
    modalOpen,
    installing,
    init,
    openModal,
    closeModal,
    install,
    dismiss,
  }
}

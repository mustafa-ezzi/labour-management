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

export function usePwaInstall() {
  const deferredPrompt = useState<BeforeInstallPromptEvent | null>('pwa-deferred-prompt', () => null)
  const dismissed = useState('pwa-install-dismissed', () => false)
  const isInstalled = useState('pwa-is-installed', () => false)
  const isIos = useState('pwa-is-ios', () => false)

  const canNativeInstall = computed(() => !!deferredPrompt.value)
  const showPrompt = computed(() => {
    if (!import.meta.client) return false
    if (isInstalled.value) return false
    if (dismissed.value) return false
    return canNativeInstall.value || isIos.value
  })

  function init() {
    if (!import.meta.client || (window as Window & { __pwaInit?: boolean }).__pwaInit) return
    ;(window as Window & { __pwaInit?: boolean }).__pwaInit = true

    isInstalled.value = detectStandalone()
    isIos.value = detectIos() && !isInstalled.value
    dismissed.value = localStorage.getItem(DISMISS_KEY) === '1'

    window.addEventListener('beforeinstallprompt', (event) => {
      event.preventDefault()
      deferredPrompt.value = event as BeforeInstallPromptEvent
    })

    window.addEventListener('appinstalled', () => {
      isInstalled.value = true
      deferredPrompt.value = null
    })
  }

  async function install(): Promise<boolean> {
    if (!deferredPrompt.value) return false
    await deferredPrompt.value.prompt()
    const { outcome } = await deferredPrompt.value.userChoice
    deferredPrompt.value = null
    if (outcome === 'accepted') {
      isInstalled.value = true
      return true
    }
    return false
  }

  function dismiss() {
    dismissed.value = true
    if (import.meta.client) {
      localStorage.setItem(DISMISS_KEY, '1')
    }
  }

  return {
    canNativeInstall,
    showPrompt,
    isInstalled,
    isIos,
    init,
    install,
    dismiss,
  }
}

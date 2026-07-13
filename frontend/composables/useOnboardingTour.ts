/**
 * Lightweight guided-tour engine (shared singleton state via useState).
 * Drives navigation + element targeting; visuals live in components/OnboardingTour.vue.
 */

export type TourStep = {
  id: string
  /** Route to navigate to before this step is shown (optional if same page). */
  to?: string
  /** CSS selector for the element to spotlight. Omit for a centered welcome/closing card. */
  selector?: string
  title: string
  description: string
  /** AppNavIcon name shown in the card header chip. */
  icon?: string
}

type TourStartOptions = {
  onFinish?: () => void
}

function isVisible(el: HTMLElement): boolean {
  const r = el.getBoundingClientRect()
  return r.width > 0 && r.height > 0
}

/** Multiple elements can share a selector (desktop + mobile nav) — pick the visible one. */
function findVisibleTarget(selector: string): HTMLElement | null {
  if (!import.meta.client) return null
  const els = Array.from(document.querySelectorAll<HTMLElement>(selector))
  return els.find(isVisible) || null
}

export function useOnboardingTour() {
  const router = useRouter()
  const route = useRoute()

  const active = useState<boolean>('tour-active', () => false)
  const steps = useState<TourStep[]>('tour-steps', () => [])
  const stepIndex = useState<number>('tour-step-index', () => 0)
  const targetRect = useState<DOMRect | null>('tour-target-rect', () => null)
  const ready = useState<boolean>('tour-ready', () => false)
  const finishCb = useState<(() => void) | null>('tour-finish-cb', () => null)

  const currentStep = computed<TourStep | null>(() => steps.value[stepIndex.value] ?? null)
  const isFirst = computed(() => stepIndex.value === 0)
  const isLast = computed(() => stepIndex.value === Math.max(steps.value.length - 1, 0))

  async function locateCurrent() {
    ready.value = false
    targetRect.value = null
    const step = currentStep.value
    if (!step) return

    if (step.to && route.path !== step.to) {
      try {
        await router.push(step.to)
      } catch {
        // ignore duplicate-navigation errors
      }
      await nextTick()
    }

    if (!step.selector) {
      ready.value = true
      return
    }

    for (let attempt = 0; attempt < 30; attempt++) {
      const el = findVisibleTarget(step.selector)
      if (el) {
        if (attempt === 0) {
          el.scrollIntoView({ block: 'center', behavior: 'smooth' })
          await new Promise((r) => setTimeout(r, 260))
        }
        targetRect.value = el.getBoundingClientRect()
        ready.value = true
        return
      }
      await new Promise((r) => setTimeout(r, 90))
    }
    // Target never appeared — fall back to a centered card instead of getting stuck.
    ready.value = true
  }

  function refreshRect() {
    const step = currentStep.value
    if (!step?.selector) return
    const el = findVisibleTarget(step.selector)
    if (el) targetRect.value = el.getBoundingClientRect()
  }

  async function start(newSteps: TourStep[], options: TourStartOptions = {}) {
    if (!newSteps.length) return
    finishCb.value = options.onFinish ?? null
    steps.value = newSteps
    stepIndex.value = 0
    active.value = true
    await locateCurrent()
  }

  async function next() {
    if (isLast.value) {
      finish()
      return
    }
    stepIndex.value += 1
    await locateCurrent()
  }

  async function prev() {
    if (isFirst.value) return
    stepIndex.value -= 1
    await locateCurrent()
  }

  function finish() {
    const cb = finishCb.value
    active.value = false
    steps.value = []
    stepIndex.value = 0
    targetRect.value = null
    ready.value = false
    finishCb.value = null
    cb?.()
  }

  /**
   * Silently discard tour state without firing onFinish — used when the tour is
   * orphaned (e.g. the user signed out, or navigated away outside the tour flow)
   * rather than genuinely completed or skipped by the user.
   */
  function abort() {
    active.value = false
    steps.value = []
    stepIndex.value = 0
    targetRect.value = null
    ready.value = false
    finishCb.value = null
    if (import.meta.client) {
      document.body.classList.remove('tour-open')
    }
  }

  return {
    active,
    steps,
    stepIndex,
    currentStep,
    isFirst,
    isLast,
    ready,
    targetRect,
    start,
    next,
    prev,
    finish,
    skip: finish,
    abort,
    refreshRect,
  }
}

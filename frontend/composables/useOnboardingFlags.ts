/** Per-browser flags controlling when guided tours auto-start. */

const NEEDS_MAIN_TOUR_KEY = 'lms:tour:needsMain'
const MAIN_TOUR_DONE_KEY = 'lms:tour:mainDone'
const SITE_TOUR_DONE_KEY = 'lms:tour:siteDone'

export function useOnboardingFlags() {
  function markNeedsMainTour() {
    if (import.meta.client) localStorage.setItem(NEEDS_MAIN_TOUR_KEY, '1')
  }

  /** Returns true once, then clears the flag so the tour never re-triggers automatically. */
  function consumeNeedsMainTour(): boolean {
    if (!import.meta.client) return false
    const flagged = localStorage.getItem(NEEDS_MAIN_TOUR_KEY) === '1'
    if (flagged) localStorage.removeItem(NEEDS_MAIN_TOUR_KEY)
    return flagged
  }

  function markMainTourDone() {
    if (import.meta.client) localStorage.setItem(MAIN_TOUR_DONE_KEY, '1')
  }

  function isMainTourDone(): boolean {
    return import.meta.client && localStorage.getItem(MAIN_TOUR_DONE_KEY) === '1'
  }

  function markSiteTourDone() {
    if (import.meta.client) localStorage.setItem(SITE_TOUR_DONE_KEY, '1')
  }

  function isSiteTourDone(): boolean {
    return import.meta.client && localStorage.getItem(SITE_TOUR_DONE_KEY) === '1'
  }

  function resetTours() {
    if (!import.meta.client) return
    localStorage.removeItem(NEEDS_MAIN_TOUR_KEY)
    localStorage.removeItem(MAIN_TOUR_DONE_KEY)
    localStorage.removeItem(SITE_TOUR_DONE_KEY)
  }

  return {
    markNeedsMainTour,
    consumeNeedsMainTour,
    markMainTourDone,
    isMainTourDone,
    markSiteTourDone,
    isSiteTourDone,
    resetTours,
  }
}

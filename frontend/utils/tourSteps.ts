import type { TourStep } from '~/composables/useOnboardingTour'

/** First-run tour: whole-app orientation shown right after registration. */
export function buildMainTourSteps(): TourStep[] {
  return [
    {
      id: 'welcome',
      title: 'Welcome to LabourPro 👋',
      description:
        "Let's take a quick look around — about 60 seconds — so you know exactly where everything lives.",
      icon: 'home',
    },
    {
      id: 'company',
      selector: '[data-tour="dash-company-card"]',
      title: 'Your workspace',
      description:
        'This is your company profile. Every site, worker, wage, and material you track belongs here.',
      icon: 'site',
    },
    {
      id: 'sites-card',
      selector: '[data-tour="dash-sites-card"]',
      title: 'Sites live here',
      description: 'Tap Sites anytime to see every construction project you manage.',
      icon: 'site',
    },
    {
      id: 'add-site',
      to: '/sites',
      selector: '[data-tour="sites-add-btn"]',
      title: 'Create your first site',
      description:
        'Every worker, wage, and material is scoped to a site. Tap here whenever you start a new project.',
      icon: 'site',
    },
    {
      id: 'nav-subscription',
      selector: '[data-tour="nav-subscription"]',
      title: 'Track your plan',
      description:
        "See your plan and renewal date here. Nothing gets disabled automatically — we'll just remind you.",
      icon: 'pay',
    },
    {
      id: 'nav-support',
      selector: '[data-tour="nav-support"]',
      title: 'Need help?',
      description: 'Message LabourPro support anytime — we reply right inside the app.',
      icon: 'attendance',
    },
    {
      id: 'done',
      title: "You're all set 🎉",
      description:
        "Create your first site to unlock crew, wages, attendance, and materials — we'll guide you through those too.",
      icon: 'wages',
    },
  ]
}

/**
 * Contextual tour shown the first time any site overview page is opened.
 * Walks the actual worker, attendance/wage, material, log-usage, and pay-material
 * screens (not just shortcut tiles) so every core workflow gets a real, live demo.
 */
export function buildSiteTourSteps(siteId: string): TourStep[] {
  const base = `/sites/${siteId}`
  return [
    {
      id: 'site-stats',
      selector: '[data-tour="site-stats"]',
      title: 'Live site snapshot',
      description: "Workers, wages due, materials, and today's attendance — updated as you go.",
      icon: 'attendance',
    },
    {
      id: 'crew',
      to: `${base}/crew`,
      selector: '[data-tour="crew-add-btn"]',
      title: 'Add your crew',
      description:
        'Add every worker on this site with a name and daily wage rate. Edit or deactivate anyone anytime.',
      icon: 'crew',
    },
    {
      id: 'wages',
      to: `${base}/crew/wages`,
      selector: '[data-tour="wages-date-card"]',
      title: 'Attendance & daily wages',
      description:
        "Pick a date, mark who worked, and set what's paid — pending balances are calculated for you automatically.",
      icon: 'wages',
    },
    {
      id: 'materials',
      to: `${base}/materials`,
      selector: '[data-tour="materials-header-actions"]',
      title: 'Materials',
      description:
        'Add every material you buy for the site with its unit and rate — costs build up automatically as you log usage.',
      icon: 'materials',
    },
    {
      id: 'log-usage',
      to: `${base}/materials/usage`,
      selector: '[data-tour="usage-date-card"]',
      title: 'Log usage',
      description: 'Record how much of a material was used on any date — the cost is calculated for you.',
      icon: 'log',
    },
    {
      id: 'pay-materials',
      to: `${base}/materials/pay`,
      selector: '[data-tour="pay-date-card"]',
      title: 'Pay materials',
      description: "Settle what you owe suppliers — partially or in full, whenever you're ready.",
      icon: 'pay',
    },
    {
      id: 'site-done',
      title: "That's the whole workflow! 🎉",
      description: 'You now know your way around a site. Explore at your own pace from here.',
      icon: 'home',
    },
  ]
}

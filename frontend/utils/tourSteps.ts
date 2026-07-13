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

/** Contextual tour shown the first time any site overview page is opened. */
export function buildSiteTourSteps(): TourStep[] {
  return [
    {
      id: 'site-stats',
      selector: '[data-tour="site-stats"]',
      title: 'Live site snapshot',
      description: "Workers, wages due, materials, and today's attendance — updated as you go.",
      icon: 'attendance',
    },
    {
      id: 'site-wages',
      selector: '[data-tour="site-wages-tile"]',
      title: 'Daily wages',
      description: 'Mark attendance and pay wages for your whole crew from one screen.',
      icon: 'wages',
    },
    {
      id: 'site-workers',
      selector: '[data-tour="site-workers-tile"]',
      title: 'Manage your crew',
      description: 'Add workers, edit rates, and check individual balances.',
      icon: 'crew',
    },
    {
      id: 'site-materials',
      selector: '[data-tour="site-materials-tile"]',
      title: 'Materials',
      description: 'Track material stock and what you owe suppliers.',
      icon: 'materials',
    },
    {
      id: 'site-logusage',
      selector: '[data-tour="site-logusage-tile"]',
      title: 'Log usage',
      description: 'Record materials used today in a couple of taps.',
      icon: 'log',
    },
    {
      id: 'site-history',
      selector: '[data-tour="site-history-link"]',
      title: 'Attendance history',
      description: 'A calendar view of who showed up, for any worker, any day.',
      icon: 'attendance',
    },
    {
      id: 'site-pay',
      selector: '[data-tour="site-pay-link"]',
      title: 'Pay materials',
      description: "Settle what you owe suppliers, whenever you're ready.",
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

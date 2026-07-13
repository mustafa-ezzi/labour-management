<template>
  <div>
    <UiPageHeader title="Dashboard" subtitle="Overview of your company" />

    <p v-if="pending" class="ui-muted">Loading…</p>
    <p v-else-if="err" class="text-red-600">{{ err }}</p>
    <template v-else>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <UiCard data-tour="dash-company-card">
          <p class="ui-label">Company</p>
          <p class="ui-stat-value mt-1 !text-base text-gray-900">{{ me?.company?.name }}</p>
          <p class="ui-muted mt-1 capitalize">Role: {{ me?.company?.role }}</p>
        </UiCard>
        <UiCard>
          <p class="ui-label">Signed in as</p>
          <p class="mt-1 break-all text-sm font-medium text-gray-800 lg:text-base">{{ me?.user?.email }}</p>
        </UiCard>
      </div>

      <div v-if="showInstallCard" class="mt-6">
        <div class="flex items-center gap-4 rounded-xl border border-violet-200 bg-violet-50 p-4">
          <img src="/logo.png" alt="LabourPro" class="h-12 w-12 shrink-0 rounded-lg object-contain" />
          <div class="min-w-0 flex-1">
            <p class="text-sm font-bold text-gray-900">Install LabourPro on your phone</p>
            <p class="mt-0.5 text-xs text-gray-600">One tap — adds the app to your home screen.</p>
          </div>
          <button type="button" class="ui-btn-primary shrink-0 py-2 text-xs" @click="triggerInstall">
            Download
          </button>
        </div>
      </div>

      <div v-if="lastSiteLink" class="mt-8">
        <NuxtLink
          :to="lastSiteLink"
          class="ui-card-hover block px-5 py-4"
        >
          <p class="text-xs font-semibold uppercase tracking-widest text-violet-700">Continue</p>
          <p class="mt-1 font-semibold text-gray-900">Resume last opened site →</p>
        </NuxtLink>
      </div>

      <h2 class="ui-label mb-3 mt-8">Where to next</h2>
      <p class="mb-4 ui-muted">Open a construction site once — crew, materials, and attendance stay scoped to that site until you tap “All sites” in the bottom bar.</p>

      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink to="/sites" data-tour="dash-sites-card" class="ui-card-hover block p-4 lg:p-5">
          <AppNavIcon name="site" class="mb-3 text-violet-700" />
          <p class="font-semibold text-gray-900">Sites</p>
          <p class="ui-muted mt-1">Pick a site to manage crew &amp; materials there</p>
        </NuxtLink>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { buildMainTourSteps } from '~/utils/tourSteps'

definePageMeta({ layout: 'app', middleware: 'auth' })

type MeResponse = {
  user: { id: string; email: string; first_name: string; last_name: string }
  company: { id: string; name: string; role: string }
}

const api = createApiClient()
const me = ref<MeResponse | null>(null)
const pending = ref(true)
const err = ref('')

const lastSiteLink = useResumeSitePath()
const { showDownloadPopup, canNativeInstall, install, openModal, modalOpen } = usePwaInstall()
const tour = useOnboardingTour()
const { consumeNeedsMainTour, markMainTourDone } = useOnboardingFlags()

const showInstallCard = computed(() => showDownloadPopup.value)

function triggerInstall() {
  if (canNativeInstall.value) {
    install()
    return
  }
  openModal()
}

function beginMainTour() {
  window.setTimeout(() => {
    tour.start(buildMainTourSteps(), { onFinish: markMainTourDone })
  }, 500)
}

onMounted(async () => {
  try {
    const { data } = await api.get<MeResponse>('/me/')
    me.value = data
  } catch {
    err.value = 'Could not load profile.'
  } finally {
    pending.value = false
  }

  if (consumeNeedsMainTour()) {
    if (modalOpen.value) {
      const stop = watch(modalOpen, (open) => {
        if (!open) {
          stop()
          beginMainTour()
        }
      })
    } else {
      beginMainTour()
    }
  }
})
</script>

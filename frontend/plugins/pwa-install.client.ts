import { captureInstallPromptEarly, usePwaInstall } from '~/composables/usePwaInstall'

export default defineNuxtPlugin({
  name: 'pwa-install',
  enforce: 'pre',
  setup() {
    captureInstallPromptEarly()
    usePwaInstall().init()
  },
})

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-05-01',
  devtools: { enabled: true },
  modules: ['@pinia/nuxt', '@nuxtjs/tailwindcss', '@vite-pwa/nuxt'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      // Local default — set NUXT_PUBLIC_API_BASE on Railway for production deploy
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8002/api',
    },
  },
  app: {
    head: {
      title: 'LabourPro',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'theme-color', content: '#7c3aed' },
        { name: 'description', content: 'Labour management for construction sites — crew, wages, attendance, materials.' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'default' },
        { name: 'apple-mobile-web-app-title', content: 'LabourPro' },
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: '/logo.png' },
        { rel: 'apple-touch-icon', href: '/pwa-192.png' },
      ],
      script: [{ key: 'pwa-bip-capture', src: '/pwa-capture.js', tagPosition: 'head' }],
    },
  },
  pwa: {
    registerType: 'autoUpdate',
    includeAssets: ['logo.png', 'pwa-192.png', 'pwa-512.png'],
    manifest: {
      name: 'LabourPro — Labour Management',
      short_name: 'LabourPro',
      description: 'Manage crew, daily wages, attendance, and materials on construction sites.',
      theme_color: '#7c3aed',
      background_color: '#f7f5fc',
      display: 'standalone',
      orientation: 'portrait-primary',
      scope: '/',
      start_url: '/',
      id: '/',
      icons: [
        {
          src: '/pwa-192.png',
          sizes: '192x192',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: '/pwa-512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: '/pwa-512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'maskable',
        },
      ],
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico,woff2}'],
      cleanupOutdatedCaches: true,
    },
    client: {
      installPrompt: false,
    },
    devOptions: {
      enabled: true,
      type: 'module',
    },
  },
})

export default defineNuxtPlugin(() => {
  const { init } = usePwaInstall()
  init()
})

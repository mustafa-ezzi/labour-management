/* Captures Chrome's beforeinstallprompt before the app JS loads. */
window.__bip = null
window.addEventListener('beforeinstallprompt', function (e) {
  e.preventDefault()
  window.__bip = e
  window.dispatchEvent(new Event('labourpro:bip'))
})

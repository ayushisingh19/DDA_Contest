// Guarded bootstrap for the Admin page
;(() => {
  const el = document.querySelector('[data-page="admin"]')
  if (!el) return // Not on this page
  console.debug('[admin.ts] Loaded')
})()

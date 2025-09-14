// Guarded bootstrap for the Start page (problem workspace)
;(() => {
  const runBtn = document.getElementById('runBtn')
  const submitBtn = document.getElementById('submitBtn')
  const editor = document.getElementById('editor') as HTMLTextAreaElement | null
  if (!runBtn && !submitBtn && !editor) return // Not on this page
  // Placeholder: page-specific logic can be ported here incrementally.
  console.debug('[start.ts] Loaded')
})()

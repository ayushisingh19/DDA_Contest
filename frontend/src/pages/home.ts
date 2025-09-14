const bootHome = () => {
  try {
    ;(globalThis as any).lucide?.createIcons?.()
  } catch {}
  const btn = document.getElementById('mobile-menu-button')
  const menu = document.getElementById('mobile-menu')
  if (btn && menu) btn.addEventListener('click', () => menu.classList.toggle('hidden'))
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootHome)
} else {
  bootHome()
}

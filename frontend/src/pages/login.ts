const bootLogin = () => {
  try {
    ;(globalThis as any).lucide?.createIcons?.()
  } catch {}
  // Auto-dismiss message toasts if present
  setTimeout(() => {
    document.querySelectorAll('.fixed .max-w-sm').forEach((msg) => {
      ;(msg as HTMLElement).style.opacity = '0'
      setTimeout(() => msg.remove(), 300)
    })
  }, 5000)
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootLogin)
} else {
  bootLogin()
}

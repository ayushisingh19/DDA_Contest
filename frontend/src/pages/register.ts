const bootRegister = () => {
  try {
    ;(globalThis as any).lucide?.createIcons?.()
  } catch {}
  setTimeout(() => {
    document.querySelectorAll('.fixed .max-w-sm').forEach((msg) => {
      ;(msg as HTMLElement).style.opacity = '0'
      setTimeout(() => msg.remove(), 300)
    })
  }, 5000)
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootRegister)
} else {
  bootRegister()
}

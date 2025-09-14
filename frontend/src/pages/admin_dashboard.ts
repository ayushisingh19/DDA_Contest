export function getCSRF(): string | null {
  const meta = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement | null
  return meta?.content ?? null
}

// Expose globally for inline onclicks if needed
;(window as any).getCSRF = getCSRF

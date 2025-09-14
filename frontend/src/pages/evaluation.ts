import { getCSRFCookie } from './utils/csrf'

async function startEval() {
  const sel = document.getElementById('eval_contest') as HTMLSelectElement | null
  const cid = sel?.value
  if (!cid) return
  const res = await fetch(`/api/contests/${cid}/evaluate/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCSRFCookie() ?? '' },
  })
  alert(res.ok ? 'Evaluation completed' : 'Evaluation failed')
}

async function loadScoreboard() {
  const sel = document.getElementById('eval_contest') as HTMLSelectElement | null
  const cid = sel?.value
  if (!cid) return
  const res = await fetch(`/api/contests/${cid}/scoreboard/`)
  const data = (await res.json().catch(() => ({ columns: [], rows: [] }))) as any
  const container = document.getElementById('scoreboard')
  if (!container) return
  const cols: string[] = data.columns ?? []
  const rows: any[] = data.rows ?? []

  let html = '<table><thead><tr>'
  cols.forEach((c) => {
    html += `<th>${c}</th>`
  })
  html += '</tr></thead><tbody>'
  rows.forEach((r) => {
    html += '<tr>'
    cols.forEach((c) => {
      html += `<td>${r[c] ?? ''}</td>`
    })
    html += '</tr>'
  })
  html += '</tbody></table>'
  container.innerHTML = html
}

;(window as any).startEval = startEval
;(window as any).loadScoreboard = loadScoreboard

import { getCSRFCookie } from './utils/csrf'

function getVal(id: string): string {
  return (document.getElementById(id) as HTMLInputElement | HTMLTextAreaElement)?.value ?? ''
}

async function createProblem() {
  const title = getVal('p_title').trim()
  const description = getVal('p_desc').trim()
  const exp = (document.getElementById('p_exp') as HTMLSelectElement)?.value
  const mem = parseInt((document.getElementById('p_mem') as HTMLInputElement)?.value || '256', 10)
  const lines = getVal('p_tcs').trim().split('\n').filter(Boolean)
  const testcases = lines.map((l) => {
    const [i, o, h] = l.split('|||')
    return { input_data: i ?? '', expected_output: o ?? '', is_hidden: (h || '0').trim() === '1' }
  })

  const res = await fetch('/api/problems/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFCookie() ?? '' },
    body: JSON.stringify({ title, description, exp_complexity: exp, mem_limit_mb: mem, testcases }),
  })
  const data = await res.json().catch(() => ({}))
  const result = document.getElementById('p_result')
  if (result)
    result.textContent = res.ok ? `Created Problem ID ${(data as any).id}` : JSON.stringify(data)
  if (res.ok) {
    const ex = document.getElementById('existing_ids') as HTMLInputElement
    if (ex) ex.value = ex.value ? ex.value + ',' + (data as any).id : String((data as any).id)
  }
}

async function createContest() {
  const name = getVal('c_name')
  const start = getVal('c_start').replace(' ', 'T') + ':00'
  const dur = parseInt(getVal('c_dur') || '120', 10)
  const is_active = (document.getElementById('c_active') as HTMLSelectElement)?.value === 'true'
  const ids = getVal('existing_ids')
    .split(',')
    .map((s) => parseInt(s.trim(), 10))
    .filter((n) => !isNaN(n))
  const res = await fetch('/api/contests/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFCookie() ?? '' },
    body: JSON.stringify({
      name,
      start_at: start,
      duration_minutes: dur,
      is_active,
      problems: ids,
    }),
  })
  const data = await res.json().catch(() => ({}))
  const result = document.getElementById('c_result')
  if (result)
    result.textContent = res.ok ? `Created Contest ID ${(data as any).id}` : JSON.stringify(data)
}

;(window as any).createProblem = createProblem
;(window as any).createContest = createContest

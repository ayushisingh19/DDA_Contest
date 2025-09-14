const BASE = (import.meta as any).env?.VITE_API_BASE_URL || ''

export async function createSubmission(payload: {
  problem_id: number
  code: string
  language: string
}) {
  const res = await fetch(`${BASE}/api/submissions/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(`Failed: ${res.status}`)
  return res.json()
}

export async function getSubmission(id: string) {
  const res = await fetch(`${BASE}/api/submissions/${id}/`)
  if (!res.ok) throw new Error(`Failed: ${res.status}`)
  return res.json()
}

export async function getProblemDetail(problemId: number, language: string = 'python') {
  const res = await fetch(`${BASE}/api/problems/${problemId}/?language=${language}`)
  if (!res.ok) throw new Error(`Failed: ${res.status}`)
  return res.json()
}

export async function getStarterCode(problemId: number, language: string) {
  const res = await fetch(`${BASE}/api/problems/${problemId}/starter-code/?language=${language}`)
  if (!res.ok) throw new Error(`Failed: ${res.status}`)
  return res.json()
}

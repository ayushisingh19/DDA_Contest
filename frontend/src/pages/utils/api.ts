export type ProblemSummary = {
  id: number
  code: string
  title: string
  difficulty: string
  is_solved: boolean
}

export type VisibleTestCase = {
  test_case_no: number
  stdin: string
  expected_output: string
}

export type ProblemDetail = ProblemSummary & {
  description: string
  constraints: string
}

async function get<T>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: 'include' })
  if (!res.ok) throw new Error(`GET ${url} failed: ${res.status}`)
  return (await res.json()) as T
}

export async function fetchProblems(): Promise<ProblemSummary[]> {
  const data = await get<{ problems: ProblemSummary[] }>('/api/problems/')
  return data.problems
}

export async function fetchVisibleTestCases(problemId: number): Promise<VisibleTestCase[]> {
  const data = await get<{ visible_testcases: VisibleTestCase[] }>(
    `/get_visible_testcases/${problemId}/`
  )
  return data.visible_testcases
}

export async function fetchProblemDetail(problemId: number): Promise<ProblemDetail> {
  const d = await get<{
    id: number
    code: string
    title: string
    description: string
    difficulty: string
    constraints: string
  }>(`/api/problems/${problemId}/`)
  return {
    id: d.id,
    code: d.code,
    title: d.title,
    description: d.description || '',
    difficulty: d.difficulty,
    constraints: d.constraints || '',
    is_solved: false,
  }
}

export type LeaderboardRow = {
  rank: number
  student_id: number
  name: string
  email: string
  solved: number
  first_solve_at?: string | null
  total_time_s?: number
  total_best_time_ms?: number
  points?: number
}

export async function fetchLeaderboard(contestId?: number): Promise<LeaderboardRow[]> {
  const url = contestId ? `/api/leaderboard/?contest_id=${contestId}` : '/api/leaderboard/'
  const data = await get<{ leaderboard: LeaderboardRow[] }>(url)
  return data.leaderboard
}

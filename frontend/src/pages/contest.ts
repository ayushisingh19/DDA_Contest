const lucideGlobal: any = (globalThis as any).lucide

function initMobileMenu() {
  const btn = document.getElementById('mobile-menu-button')
  const menu = document.getElementById('mobile-menu')
  if (!btn || !menu) return
  btn.addEventListener('click', () => menu.classList.toggle('hidden'))
}

function initIcons() {
  try {
    lucideGlobal?.createIcons?.()
  } catch {}
}

function boot() {
  initIcons()
  initMobileMenu()
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot)
} else {
  boot()
}
// Guarded bootstrap for the Contest page
;(() => {
  const el = document.querySelector('[data-page="contest"]') || document.querySelector('main')
  if (!el) return // Not on this page
  console.debug('[contest.ts] Loaded')

  // Progressive enhancement: render problems & sample visible cases if placeholders exist
  import('./utils/api').then(async ({ fetchProblems, fetchVisibleTestCases, fetchProblemDetail, fetchLeaderboard }) => {
    const list = document.getElementById('problem-list')
    const detail = document.getElementById('problem-detail')
    const cases = document.getElementById('problem-visible-cases')
    const leaderboardEl = document.getElementById('leaderboard')

    // Conditionally render problems UI only if containers exist
    if (list) {
      try {
        const problems = await fetchProblems()
        list.innerHTML = ''
        const renderDetail = async (pid: number) => {
          if (!detail) return
          detail.innerHTML = '<div class="text-gray-400 text-sm">Loading problem...</div>'
          try {
            const d = await fetchProblemDetail(pid)
            detail.innerHTML = `
              <div class="space-y-2">
                <div class="text-lg font-semibold text-white">${d.code}: ${d.title}</div>
                <div class="text-gray-300 whitespace-pre-wrap">${d.description || ''}</div>
                ${d.constraints ? `<div class=\"text-sm text-gray-400\"><span class=\"font-semibold text-gray-300\">Constraints:</span> ${d.constraints}</div>` : ''}
              </div>
            `
          } catch (e) {
            detail.innerHTML = '<div class="text-red-400 text-sm">Failed to load problem detail</div>'
          }
        }

        const renderCases = async (pid: number) => {
          if (!cases) return
          cases.innerHTML = '<div class="text-gray-400 text-sm">Loading examples...</div>'
          try {
            const vc = await fetchVisibleTestCases(pid)
            if (!vc.length) {
              cases.innerHTML = '<div class="text-gray-400 text-sm">No sample cases</div>'
              return
            }
            const frag = document.createDocumentFragment()
            vc.forEach((c) => {
              const pre = document.createElement('pre')
              pre.className = 'bg-black/30 text-gray-200 p-3 rounded-lg overflow-auto'
              pre.textContent = `# Case ${c.test_case_no}\nInput: ${c.stdin}\nExpected: ${c.expected_output}`
              frag.appendChild(pre)
            })
            cases.innerHTML = ''
            cases.appendChild(frag)
          } catch (err) {
            cases.innerHTML = '<div class="text-red-400 text-sm">Failed to load examples</div>'
          }
        }

        for (const p of problems) {
          const row = document.createElement('div')
          row.className = 'flex items-center justify-between p-3 rounded-lg border border-gray-700 hover:bg-white/5'
          row.innerHTML = `
            <div>
              <div class="font-semibold text-white">${p.code}: ${p.title}</div>
              <div class="text-xs text-gray-400">Difficulty: ${p.difficulty}</div>
            </div>
            <div class="flex items-center gap-3">
              ${p.is_solved ? '<span class="text-green-400 text-sm">Solved</span>' : ''}
              <a href="/problems/${p.id}/" class="text-yellow-400 hover:text-yellow-300 text-sm">Open</a>
            </div>
          `
          row.addEventListener('click', async () => {
            await renderDetail(p.id)
            await renderCases(p.id)
          })
          list.appendChild(row)
        }

        if (problems.length) {
          await renderDetail(problems[0].id)
          await renderCases(problems[0].id)
        }
      } catch (err) {
        list.innerHTML = '<div class="text-red-400">Failed to load problems.</div>'
      }
    }

    // Live Leaderboard (simple polling); always try to render if present
    const renderLeaderboard = async () => {
      if (!leaderboardEl) return
      try {
        const rows = await fetchLeaderboard()
        if (!rows.length) {
          leaderboardEl.innerHTML = '<div class="text-gray-400 text-sm">No results yet</div>'
          return
        }
        const table = document.createElement('table')
        table.className = 'min-w-full text-sm'
        table.innerHTML = `
          <thead>
            <tr class="text-gray-300 border-b border-gray-700">
              <th class="text-left py-2 pr-4">#</th>
              <th class="text-left py-2 pr-4">Name</th>
              <th class="text-left py-2 pr-4">Solved</th>
              <th class="text-left py-2 pr-4">Pts</th>
              <th class="text-left py-2 pr-4">Best Time</th>
            </tr>
          </thead>
          <tbody></tbody>
        `
        const tbody = table.querySelector('tbody')!
        rows.forEach((r) => {
          const tr = document.createElement('tr')
          tr.className = 'border-b border-gray-800'
          const bestMs = r.total_best_time_ms ?? 0
          const bestDisp = bestMs ? `${(bestMs / 1000).toFixed(3)}s` : '-'
          const pts = r.points ?? r.solved ?? 0
          tr.innerHTML = `
            <td class="py-2 pr-4 text-gray-200">${r.rank}</td>
            <td class="py-2 pr-4 text-white">${r.name}</td>
            <td class="py-2 pr-4 text-gray-200">${r.solved}</td>
            <td class="py-2 pr-4 text-gray-200">${pts}</td>
            <td class="py-2 pr-4 text-gray-400">${bestDisp}</td>
          `
          tbody.appendChild(tr)
        })
        leaderboardEl.innerHTML = ''
        leaderboardEl.appendChild(table)
      } catch (e) {
        leaderboardEl.innerHTML = '<div class="text-red-400 text-sm">Failed to load leaderboard</div>'
      }
    }

    await renderLeaderboard()
    setInterval(renderLeaderboard, 10000)
  })
})()

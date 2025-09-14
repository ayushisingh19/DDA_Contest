;(function () {
  function qs(id) {
    return document.getElementById(id)
  }

  async function fetchLeaderboard() {
    const res = await fetch('/api/leaderboard/', { credentials: 'same-origin' })
    if (!res.ok) throw new Error('Failed to fetch leaderboard')
    const data = await res.json()
    // Support both { leaderboard: [...] } and bare array (future-proof)
    if (Array.isArray(data)) return data
    if (data && Array.isArray(data.leaderboard)) return data.leaderboard
    return []
  }

  function renderTable(rows) {
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
    const tbody = table.querySelector('tbody')
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
    return table
  }

  async function renderLeaderboardOnce(target) {
    try {
      const rows = await fetchLeaderboard()
      if (!rows || !rows.length) {
        target.innerHTML = '<div class="text-gray-400 text-sm">No results yet</div>'
        return
      }
      target.innerHTML = ''
      target.appendChild(renderTable(rows))
    } catch (e) {
      target.innerHTML = '<div class="text-red-400 text-sm">Failed to load leaderboard</div>'
    }
  }

  function boot() {
    const el = qs('leaderboard')
    if (!el) return
    renderLeaderboardOnce(el)
    setInterval(() => renderLeaderboardOnce(el), 10000)
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot)
  } else {
    boot()
  }
})()

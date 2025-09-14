import { getCSRFCookie } from './utils/csrf'

async function delContest(id: number) {
  if (!confirm('Delete contest ' + id + ' ?')) return
  const res = await fetch('/api/contests/' + id + '/', {
    method: 'DELETE',
    headers: { 'X-CSRFToken': getCSRFCookie() ?? '' },
  })
  if (res.status === 204) {
    document.getElementById('row-' + id)?.remove()
  } else {
    alert('Failed')
  }
}

;(window as any).delContest = delContest

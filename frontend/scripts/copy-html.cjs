// Recursively copies HTML templates from frontend/templates to Django templates dir
const fs = require('fs')
const path = require('path')

const srcRoot = path.join(__dirname, '../templates')
const destRoot = path.join(__dirname, '../../src/student_auth')
const destTpl = path.join(destRoot, 'accounts/templates')

function copyDir(src, dest) {
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true })
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name)
    const d = path.join(dest, entry.name)
    if (entry.isDirectory()) {
      copyDir(s, d)
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      fs.copyFileSync(s, d)
      console.log(`[copy-html] Copied ${path.relative(srcRoot, s)}`)
    }
  }
}

copyDir(srcRoot, destTpl)

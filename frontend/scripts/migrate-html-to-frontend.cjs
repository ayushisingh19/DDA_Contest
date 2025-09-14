// Copies original Django templates into the frontend/templates tree
const fs = require('fs')
const path = require('path')

const srcRoot = path.join(__dirname, '../../src/student_auth/accounts/templates')
const destRoot = path.join(__dirname, '../templates')

function copyDir(src, dest) {
  if (!fs.existsSync(src)) {
    console.log(`[migrate-html] Source not found: ${src}`)
    return
  }
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true })
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name)
    const d = path.join(dest, entry.name)
    if (entry.isDirectory()) {
      copyDir(s, d)
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      fs.copyFileSync(s, d)
      console.log(`[migrate-html] Copied ${path.relative(srcRoot, s)}`)
    }
  }
}

copyDir(srcRoot, destRoot)
console.log('[migrate-html] Done.')

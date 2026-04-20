import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(dirname, '..')
const source = path.resolve(root, '..', 'site-data', 'signal_desk.json')
const outDir = path.join(root, 'public', 'site-data')
const target = path.join(outDir, 'signal_desk.json')

if (!fs.existsSync(source)) {
  throw new Error(`Missing generated Signal Desk data: ${source}`)
}

fs.mkdirSync(outDir, { recursive: true })
fs.copyFileSync(source, target)
console.log(`Synced ${path.relative(root, source)} -> ${path.relative(root, target)}`)

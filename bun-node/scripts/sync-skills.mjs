import {
  cpSync,
  existsSync,
  mkdirSync,
  readdirSync,
  rmSync,
  statSync,
} from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = resolve(fileURLToPath(new URL('.', import.meta.url)))
const projectRoot = resolve(__dirname, '..')

const sourceRoot = resolve(projectRoot, '.claude', 'skills')
const targetRoot = resolve(projectRoot, '.codex', 'skills')

const ignoredNames = new Set(['.DS_Store', '.git', '.venv', '__pycache__'])

function listRawEntries(root) {
  if (!existsSync(root)) {
    return []
  }

  return readdirSync(root, { withFileTypes: true })
}

function listEntries(root) {
  return listRawEntries(root).filter(
    (entry) => !ignoredNames.has(entry.name),
  )
}

function syncDirectory(sourceDir, targetDir) {
  mkdirSync(targetDir, { recursive: true })

  const sourceEntries = listEntries(sourceDir)
  const sourceNames = new Set(sourceEntries.map((entry) => entry.name))

  for (const targetEntry of listRawEntries(targetDir)) {
    if (ignoredNames.has(targetEntry.name) || !sourceNames.has(targetEntry.name)) {
      rmSync(join(targetDir, targetEntry.name), {
        force: true,
        recursive: true,
      })
    }
  }

  for (const entry of sourceEntries) {
    const sourcePath = join(sourceDir, entry.name)
    const targetPath = join(targetDir, entry.name)

    if (entry.isDirectory()) {
      syncDirectory(sourcePath, targetPath)
      continue
    }

    if (entry.isFile()) {
      cpSync(sourcePath, targetPath, { force: true })
    }
  }
}

if (!existsSync(sourceRoot) || !statSync(sourceRoot).isDirectory()) {
  console.error(`Missing skills source: ${sourceRoot}`)
  process.exit(1)
}

syncDirectory(sourceRoot, targetRoot)

const syncedSkills = listEntries(targetRoot)
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort()

console.log(`Synced ${syncedSkills.length} skill(s) to ${targetRoot}`)
for (const skillId of syncedSkills) {
  console.log(`- ${skillId}`)
}

import { existsSync, statSync } from 'node:fs'
import { extname } from 'node:path'
import { json, notFound, withCors } from '../lib/sse.ts'
import { listImages, safeSessionFilePath, MIME_MAP } from '../lib/sessions.ts'

export async function handleMedia(req: Request, url: URL): Promise<Response | null> {

  // GET /api/images?sessionId=
  if (req.method === 'GET' && url.pathname === '/api/images') {
    const sessionId = url.searchParams.get('sessionId') ?? 'default'
    return json({ images: listImages(sessionId) })
  }

  // GET /sessions/**  — serve images from session output dirs
  if (req.method === 'GET' && url.pathname.startsWith('/sessions/')) {
    const rel = decodeURIComponent(url.pathname.replace(/^\/sessions\//, ''))
    const fullPath = safeSessionFilePath(rel)
    if (!fullPath) return notFound()

    const ext = extname(fullPath).toLowerCase()
    const mime = MIME_MAP[ext]
    if (!mime || !existsSync(fullPath) || !statSync(fullPath).isFile()) return notFound()

    const file = Bun.file(fullPath)
    return new Response(file, {
      headers: withCors({
        'Content-Type': mime,
        'Cache-Control': 'no-cache',
      }),
    })
  }

  return null
}

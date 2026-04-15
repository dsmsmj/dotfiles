import { existsSync, statSync } from 'node:fs'
import { extname } from 'node:path'
import { json, notFound, withCors } from '../lib/sse.ts'
import {
  buildImageGenerationResult,
  listImageArtifacts,
  listImages,
  listTextArtifacts,
  MIME_MAP,
  safeSessionFilePath,
} from '../lib/sessions.ts'

function wantsInlineData(url: URL): boolean {
  const value = url.searchParams.get('inline')
  return value === 'base64' || value === 'true' || value === '1'
}

export async function handleMedia(req: Request, url: URL): Promise<Response | null> {
  if (req.method === 'GET' && url.pathname === '/api/images') {
    const sessionId = url.searchParams.get('sessionId') ?? 'default'
    return json({ images: listImages(sessionId) })
  }

  if (req.method === 'GET' && url.pathname === '/api/artifacts') {
    const sessionId = url.searchParams.get('sessionId') ?? 'default'
    return json({
      artifacts: [
        ...listImageArtifacts(sessionId, wantsInlineData(url)),
        ...listTextArtifacts(sessionId),
      ],
    })
  }

  if (req.method === 'GET' && url.pathname === '/api/image-result') {
    const sessionId = url.searchParams.get('sessionId') ?? 'default'
    return json(buildImageGenerationResult(sessionId, wantsInlineData(url)))
  }

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

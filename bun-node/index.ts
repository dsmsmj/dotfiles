import { PORT, PROJECT_ROOT, DATA_ROOT } from './lib/runtime.ts'
import { withCors } from './lib/sse.ts'
import { handleSessions } from './routes/sessions.ts'
import { handleRun, handleExec } from './routes/run.ts'
import { handleControl } from './routes/control.ts'
import { handleMedia } from './routes/media.ts'

const server = Bun.serve({
  port: PORT,
  async fetch(req, srv) {
    const url = new URL(req.url)

    // CORS preflight
    if (req.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: withCors() })
    }

    // Route to handlers in priority order
    return (
      (await handleSessions(req, url)) ??
      (await handleRun(req, url, srv)) ??
      (await handleExec(req, url, srv)) ??
      (await handleControl(req, url)) ??
      (await handleMedia(req, url)) ??
      new Response('Not Found', { status: 404, headers: withCors() })
    )
  },
})

console.log(`acpx server listening on http://${server.hostname}:${server.port}`)
console.log(`ACPX_PROJECT_ROOT=${PROJECT_ROOT}`)
console.log(`ACPX_DATA_ROOT=${DATA_ROOT}`)

export function withCors(headers?: Record<string, string>): Record<string, string> {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    ...(headers ?? {}),
  }
}

export function json(data: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(data), {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...withCors(),
      ...(init?.headers ?? {}),
    },
  })
}

export function notFound(): Response {
  return new Response('Not Found', { status: 404, headers: withCors() })
}

export function badRequest(message: string): Response {
  return json({ error: message }, { status: 400 })
}

export function serverError(message: string): Response {
  return json({ error: message }, { status: 500 })
}

export function sseEvent(type: string, data: string, extra?: Record<string, unknown>): string {
  return `data: ${JSON.stringify({ type, data, ...(extra ?? {}) })}\n\n`
}

export function sseHeaders(): Record<string, string> {
  return withCors({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  })
}

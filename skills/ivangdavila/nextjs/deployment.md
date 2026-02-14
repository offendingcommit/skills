# Deployment Traps

## Build Issues

- `output: 'standalone'` no incluye `public/` ni `static/` — copiar manualmente
- Build en CI puede tener variables de entorno diferentes — builds no reproducibles
- `generateStaticParams` que falla = build falla — no hay fallback
- ISR requiere filesystem writable — serverless read-only = ISR no funciona

## Environment Variables

- `NEXT_PUBLIC_*` se bake en build time — cambiar después no tiene efecto
- `.env.local` no existe en CI — secrets deben venir de otra fuente
- Runtime env con `publicRuntimeConfig` requiere `getInitialProps` — rompe static optimization
- `process.env.X` en client es undefined — solo `NEXT_PUBLIC_X` funciona

## Docker

- `.next/cache` debe persistir entre builds — o rebuilds son 10x más lentos
- `standalone` output necesita node_modules específicos — no el node_modules completo
- Health check a `/` puede ser redirect 308 — usar `/api/health` explícito
- Signal handling: Next.js necesita SIGTERM graceful — no SIGKILL

## Serverless

- Cold start con muchas rutas = lento — cada ruta es una función
- `getStaticPaths` con `fallback: true` + serverless = primera request muy lenta
- Connection pooling a DB no funciona — cada invocation es nueva conexión
- 50MB limit en Vercel — easy to hit con dependencies pesadas

## CDN/Edge

- Edge runtime no soporta todos los Node APIs — muchos packages fallan
- Middleware en edge + API route en Node = dos cold starts
- `Cache-Control` headers pueden ser ignorados por CDN — depende de config
- Purge de CDN no purga el cache de Next.js — son independientes

## Monitoring

- Errores en Server Components no llegan a error tracking client-side
- `console.log` en server components va a server logs, no browser
- Source maps en producción requieren config explícita — errores ilegibles sin ellos

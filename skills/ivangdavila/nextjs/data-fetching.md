# Data Fetching Traps

## Server Components

- `async` component que tarda mucho bloquea TODO — envolver en Suspense
- Fetch sin error handling crashea la página entera — usar error.tsx o try/catch
- `fetch` en loop es secuencial — usar Promise.all para paralelizar

## Caching Surprises

- POST/PUT/DELETE requests NO se cachean pero el GET después SÍ usa caché viejo
- `revalidate: 0` no es lo mismo que `cache: 'no-store'` — comportamiento sutil diferente
- Fetch en desarrollo SIEMPRE no-cacheado — bugs de caché solo aparecen en producción
- `fetch` con body diferente = cache key diferente — pero headers no afectan cache key

## Revalidation

- `revalidatePath('/')` NO revalida recursivamente — solo esa ruta exacta
- `revalidateTag` en Server Action no afecta al response actual — solo requests siguientes
- Tags son strings globales — colisión de nombres entre features causa bugs

## Server Actions

- Llamar server action en loop = N requests HTTP — no hay batching automático
- `redirect()` en server action NO funciona en try/catch — se lanza como error
- Return value de server action tiene límite de tamaño — no devolver datasets grandes

## Streaming

- Suspense boundary muy profundo = muchos chunks HTTP — overhead de red
- Error en Suspense fallback crashea todo — el fallback también puede fallar
- `loading.tsx` no funciona con `generateStaticParams` — es dinámico o estático, no ambos

## Client Fetching

- `useEffect` fetch en client component = waterfall después de SSR
- SWR/React Query en server component no funciona — son client-only
- Fetch en useEffect sin cleanup = race conditions en fast navigation

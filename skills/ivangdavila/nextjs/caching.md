# Caching Traps

## Request Memoization

- Solo funciona dentro de un ÚNICO request — no entre requests
- Solo para GET requests con misma URL y options — POST no memoiza
- `cache: 'no-store'` desactiva memoization también — no solo data cache
- Solo en React tree — fetch fuera de componente no memoiza

## Data Cache

- Persiste entre DEPLOYS — datos viejos sobreviven redeploy
- No hay forma de invalidar TODO el cache — solo por path/tag específico
- `fetch` third party sin tag = imposible invalidar selectivamente
- Edge runtime no tiene acceso al mismo cache que Node runtime

## Full Route Cache

- Rutas con `cookies()` o `headers()` NUNCA se cachean — son siempre dinámicas
- `searchParams` en page props = ruta dinámica automáticamente
- `export const dynamic = 'force-static'` con función dinámica = build error, no warning

## Router Cache (Client)

- Persiste 30s para páginas dinámicas, 5min para estáticas — no configurable
- Back/forward SIEMPRE usa cache — incluso si datos cambiaron
- `router.refresh()` no limpia router cache — solo re-fetcha server components
- Única forma de limpiar: navegación a ruta diferente y volver

## Common Mistakes

- Asumir que revalidate en producción = comportamiento en dev — son MUY diferentes
- `revalidate: 60` en fetch + `revalidate: 30` en page = usa el MENOR (30)
- Múltiples fetches con diferentes `revalidate` = comportamiento impredecible
- Cache de imágenes `next/image` es separado — tiene sus propias reglas

## Debugging

- No hay forma nativa de ver qué está cacheado — solo trial and error
- Headers `x-nextjs-cache` solo en producción con CDN configurado
- Logs de revalidación no indican si realmente cambió algo

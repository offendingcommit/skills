# Routing Traps

## File System

- Archivo `page.tsx` en carpeta sin `page.tsx` padre = 404 para rutas intermedias
- `loading.tsx` NO aplica al primer render de la página — solo navegaciones subsecuentes
- `error.tsx` no captura errores en `layout.tsx` del mismo nivel — necesita estar un nivel arriba
- Renombrar carpeta no actualiza caché — borrar `.next` manualmente

## Parallel Routes

- `@modal` sin `default.tsx` = crash en navegación directa — siempre añadir default
- Slots no matcheados devuelven `null` silenciosamente — no error, simplemente no renderiza
- `useSelectedLayoutSegment` devuelve null en default slots — comportamiento confuso

## Intercepting Routes

- `(.)photo` solo intercepta desde el MISMO nivel — no funciona desde subdirectorios
- Intercepted route y original deben tener MISMO layout — o UX rota
- Hard refresh siempre muestra la ruta original, no la interceptada

## Link Component

- `<Link>` prefetch en viewport por defecto — puede causar cientos de requests
- `prefetch={false}` no desactiva completamente — hover todavía prefetcha
- `replace` no funciona con intercepted routes — siempre hace push

## Navigation

- `router.push` no espera a que la navegación complete — es fire-and-forget
- `router.refresh()` no recarga la página — solo revalida server components
- `redirect()` en try/catch se captura como error — lanza NEXT_REDIRECT que no debes catchear

## Dynamic Routes

- `[...slug]` catch-all NO matchea la ruta vacía — usar `[[...slug]]` para opcional
- `generateStaticParams` con paths que no existen = build warning, no error
- Params son siempre strings — `[id]` recibe `"123"` no `123`

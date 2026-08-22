# SportShield Frontend - Agent Instructions

## Project Overview

Next.js 16.2.4 + React 19 + TypeScript + Tailwind CSS v4 + Supabase SSR auth.
Dark-themed sports piracy protection dashboard with AI fingerprinting capabilities.

**Critical:** This uses Next.js 16 — APIs, conventions, and file structure may differ from training data. Read `node_modules/next/dist/docs/` before writing code.

---

## Build & Development Commands

```bash
npm run dev          # Start dev server (localhost:3000)
npm run build        # Production build
npm start        # Start production server
npm run lint         # Run ESLint
```

**No test framework configured yet.** Project uses manual testing via dashboard UI.

---

## Code Style & Conventions

### Imports
- Use absolute imports via `@/*` path alias (e.g., `@/utils/supabase/server`)
- Group imports: React → Next.js → Components → Utils
- Use named exports for components, default exports for pages

### TypeScript
- Strict mode enabled. No `any` types.
- Use interfaces for component props
- Type event handlers explicitly when needed

### Naming Conventions
- Components: PascalCase (`StatCard`, `AuthForm`)
- Utils/functions: camelCase (`fetchApi`, `createClient`)
- Files: match component name (e.g., `StatCard.tsx`)
- Directories: lowercase with hyphens (`dashboard/`, `auth/`)

### Formatting
- Single quotes for strings
- Semicolons required
- Trailing commas in multi-line objects
- 2-space indentation

### Error Handling
- Always wrap Supabase calls in try/catch
- Use `instanceof Error` for type-safe error handling
- Log errors with descriptive messages
- Provide fallback data on API failures

### Component Patterns
```tsx
// Server Component (default for pages)
export default async function DashboardPage() {
  const data = await fetchData()
  return <div>{data}</div>
}

// Client Component (when interactivity needed)
"use client"
export default function AuthForm() {
  const [state, setState] = useState()
  return <form>...</form>
}
```

---

## Architecture Notes

### App Router
- All pages in `src/app/`
- Route groups: `dashboard/`, `auth/`, `login/`
- Layouts use `layout.tsx`, error handling via `error.tsx`

### Supabase Auth (SSR)
- Server: `createClient(cookies())` from `@/utils/supabase/server`
- Client: `createClient()` from `@/utils/supabase/client`
- Session tokens injected into API requests automatically

### API Layer
- `@/utils/api.ts` - Server-side fetcher with auth injection
- Base URL: `NEXT_PUBLIC_API_URL` (fallback: localhost:8000)
- Always returns JSON, throws on non-OK responses

### Styling
- Tailwind CSS v4 (uses `bg-[#0B0E14]`, `text-slate-400`, etc.)
- Design tokens: Coral accent `#FF6B6B`, dark backgrounds `#111415`
- Material SymbolsOutlined icons (loaded in layout.tsx)
- Inline `<style>` tags for complex animations

---

## Environment Variables

Required in `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

---

## Adding New Features

1. **New Page:** Create folder in `src/app/` with `page.tsx`
2. **New Component:** Add to `src/components/<feature>/`
3. **New API Endpoint:** Update `src/utils/api.ts` with typed fetcher
4. **Auth Required:** Call `supabase.auth.getUser()` in server component

---

## Common Pitfalls

- ❌ Don't use `useEffect` in server components
- ❌ Don't access `window` in server components
- ✅ Use `async/await` for data fetching in pages
- ✅ Mark interactive components with `"use client"`
- ✅ Handle loading states with `loading.tsx`
- ✅ Handle errors with `error.tsx`

---

## Testing (Manual)

1. Run `npm run dev`
2. Navigate to affected page
3. Verify UI matches Figma design tokens
4. Check console for errors
5. Test auth flow if applicable

---

## Git Hygiene

- Atomic commits (~100 lines max)
- Imperative commit messages ("Add dashboard stats", not "Added")
- No secrets or `.env` files committed
- Short-lived feature branches off main
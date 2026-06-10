# Core ERP Admin Panel

Professional ERP admin panel — Next.js 15 + React 19 + TypeScript.

## Stack

- Next.js 15 (App Router)
- React 19, TypeScript
- Tailwind CSS 4, Shadcn-style UI
- TanStack Query, Zustand
- React Hook Form + Zod
- Axios

## Quick start

```bash
cd admin-panel
cp .env.example .env.local
npm install
npm run dev
```

Backend ishlayotgan bo'lishi kerak (`uvicorn app.main:app --reload`).

`.env.local`:

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
API_URL=http://127.0.0.1:8000
```

Login: seed qilingan `ADMIN_EMAIL` / `ADMIN_PASSWORD`.

## Arxitektura

Batafsil: [ARCHITECTURE.md](./ARCHITECTURE.md)

## Modullar

| Modul | List | Create | Edit | View |
|-------|------|--------|------|------|
| Dashboard | ✓ | — | — | — |
| Products | ✓ | ✓ | ✓ | ✓ |
| Clients | ✓ | ✓ | ✓ | ✓ |
| Sales Orders | ✓ | ✓ | * | ✓ |
| Warehouses | ✓ | ✓ | — | ✓ |
| Payments | ✓ | ✓ | — | ✓ |
| Invoices | ✓ | ✓ | * | ✓ |
| Receivables | ✓ | — | — | — |
| Users | ✓ | ✓ | — | ✓ |
| Roles | ✓ | ✓ | — | ✓ |
| Settings | — | — | — | ✓ |

`*` — keyingi iteratsiyada to'ldiriladi.

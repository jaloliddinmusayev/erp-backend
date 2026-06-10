# Core ERP Admin Panel — Arxitektura

## 1. Umumiy ko'rinish

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js 15 App Router                    │
├──────────────┬──────────────────────────────────────────────┤
│  (auth)      │  (dashboard) — Protected Shell               │
│  /login      │  Sidebar + Navbar + Module Pages             │
└──────────────┴──────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐          ┌──────────────────────────┐
│  Zustand Auth   │          │  TanStack Query Cache    │
│  Store (persist)│          │  + Axios API Client      │
└─────────────────┘          └──────────────────────────┘
                                        │
                                        ▼
                             ┌──────────────────────────┐
                             │  FastAPI ERP Backend     │
                             │  JWT tenant (company_id) │
                             └──────────────────────────┘
```

## 2. Folder Structure

```
admin-panel/src/
├── app/
│   ├── (auth)/login/           # Public login
│   ├── (dashboard)/            # Protected app shell
│   │   ├── layout.tsx          # Sidebar + Navbar
│   │   ├── page.tsx            # Dashboard KPIs
│   │   └── [module]/           # CRUD pages per resource
│   ├── api/auth/               # Optional cookie bridge
│   ├── layout.tsx              # Root + Providers
│   └── providers.tsx           # Query, Theme, Toast
├── components/
│   ├── ui/                     # Shadcn primitives
│   ├── layout/                 # AppShell, Sidebar, Navbar
│   ├── data-table/             # Reusable DataTable
│   ├── forms/                  # FormField, ResourceForm
│   └── crud/                   # CrudList, CrudDetail, guards
├── features/                   # Module-specific UI + hooks
│   ├── auth/
│   ├── dashboard/
│   ├── products/
│   └── ...
├── lib/
│   ├── api/                    # Axios client + module APIs
│   ├── permissions/            # RBAC helpers
│   └── utils.ts
├── hooks/                      # useAuth, usePermissions, useCrud
├── stores/                     # auth-store, ui-store
├── types/                      # API DTOs
└── config/
    ├── navigation.ts           # Sidebar menu + permissions
    ├── permissions.ts          # Permission matrix
    └── resources/              # CRUD generator configs
```

## 3. API Integration Strategy

| Qatlam | Vazifa |
|--------|--------|
| `lib/api/client.ts` | Axios instance, Bearer interceptor, 401 → logout |
| `lib/api/errors.ts` | `ApiError` parse, toast-friendly messages |
| `lib/api/modules/*.ts` | Typed CRUD per backend resource |
| TanStack Query | `useQuery` lists/detail, `useMutation` CUD + invalidate |
| `next.config.ts` | Dev proxy: `/api/backend/*` → FastAPI |

**Pagination:** Backend `skip` + `limit` (no total count). Frontend: page index → `skip = (page-1)*limit`, `hasMore = data.length === limit`.

**Money fields:** Parse `Decimal` strings with `parseMoney()`.

**Multi-tenant:** Never send `company_id` in bodies — JWT handles scope.

## 4. State Management Strategy

| Store | Texnologiya | Ma'lumot |
|-------|-------------|----------|
| Auth | Zustand + persist | `token`, `user` (from `/auth/me`) |
| UI | Zustand | sidebar collapsed, mobile drawer |
| Server | TanStack Query | All API data, staleTime 30s |
| Forms | React Hook Form + Zod | Local form state per page |

**Auth flow:**
1. `POST /auth/login` → token
2. `GET /auth/me` → user + role
3. Axios interceptor attaches `Authorization: Bearer`
4. 401 → clear store → redirect `/login`

## 5. Permission Model

```ts
type Permission =
  | "dashboard:view"
  | "products:read" | "products:write"
  | "clients:read" | "clients:write"
  | "sales_orders:read" | "sales_orders:write"
  | "warehouses:read" | "warehouses:write"
  | "payments:read" | "payments:write"
  | "invoices:read" | "invoices:write"
  | "receivables:read"
  | "users:read" | "users:write"      // admin only
  | "roles:read" | "roles:write"      // admin only
  | "settings:view";

// role.code === "admin" → all permissions
// future roles → explicit permission map
```

**Menu filtering:** `navigation.ts` items have `permissions[]` — sidebar filters by `hasPermission()`.

**Route guards:** `PermissionGuard` component wraps admin-only actions.

## 6. UI Component Strategy

| Komponent | Maqsad |
|-----------|--------|
| `DataTable` | TanStack Table + sorting + pagination + search |
| `ResourceForm` | RHF + Zod + field config driven |
| `CrudListPage` | Generic list from `ResourceConfig` |
| `CrudFormPage` | Create/Edit from same config |
| `CrudDetailPage` | View + action buttons (lifecycle) |
| `PageHeader` | Title, breadcrumbs, primary action |
| `KpiCard` | Dashboard metrics |
| `StatusBadge` | Enum status colors |

**Theme:** `next-themes` + CSS variables (shadcn-compatible). Light/dark toggle in Navbar.

**Responsive:** Sidebar collapses to sheet on mobile (`md:` breakpoint).

## 7. CRUD Generator Architecture

```ts
interface ResourceConfig<TList, TDetail, TCreate, TUpdate> {
  key: string;                    // query key prefix
  label: string;                  // "Products"
  basePath: string;               // "/products"
  api: ResourceApi<T...>;         // typed API module
  columns: ColumnDef<TList>[];
  formFields: FormFieldConfig[];
  schemas: { create: ZodSchema; update: ZodSchema };
  permissions: { read: Permission; write: Permission };
  listFilters?: FilterConfig[];
  detailActions?: ActionConfig[];  // lifecycle (confirm, issue, etc.)
}
```

Pages import config → render generic CRUD shell → module-specific overrides in `features/`.

## 8. Module Page Matrix

| Module | List | Create | Edit | View | Notes |
|--------|------|--------|------|------|-------|
| Products | ✓ | ✓ | ✓ | ✓ | Full CRUD |
| Clients | ✓ | ✓ | ✓ | ✓ | Full CRUD |
| Sales Orders | ✓ | ✓ | ✓ | ✓ | + lifecycle actions |
| Warehouses | ✓ | ✓ | — | ✓ | Backend: list+create only |
| Payments | ✓ | ✓ | — | ✓ | No update |
| Invoices | ✓ | ✓ | ✓ | ✓ | + issue/cancel |
| Receivables | ✓ | — | — | — | Aging + statements |
| Users | ✓ | ✓ | — | ✓ | Admin, list+create |
| Roles | ✓ | ✓ | — | ✓ | Admin, list+create |
| Settings | — | — | — | ✓ | Profile + theme |

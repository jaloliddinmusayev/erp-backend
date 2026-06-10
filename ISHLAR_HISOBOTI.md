# Core ERP — bajarilgan ishlar hisoboti

**Sana:** 2026-06-10  
**Loyiha:** Core ERP (`erp-backend` + `admin-panel`)  
**Bosqich:** Phase 1 — Backend tayyor, Admin Panel yaratildi

---

## 1. Umumiy ko'rinish

Loyiha ikki mustaqil qismdan iborat:

| Qism | Texnologiya | Holat |
|------|-------------|-------|
| **Backend API** | FastAPI + PostgreSQL + SQLAlchemy 2.x | Phase 1 tayyor |
| **Admin Panel** | Next.js 15 + React 19 + TypeScript | Yangi yaratildi, production build OK |

```
┌─────────────────────┐         ┌─────────────────────┐
│   admin-panel/      │  JWT    │   ERP Backend       │
│   Next.js 15        │ ──────► │   FastAPI           │
│   localhost:3000    │  Axios  │   localhost:8000    │
└─────────────────────┘         └─────────────────────┘
                                         │
                                         ▼
                                ┌─────────────────────┐
                                │   PostgreSQL        │
                                │   (multi-tenant)    │
                                └─────────────────────┘
```

---

## 2. Backend (avvaldan mavjud — Phase 1)

### 2.1. Modullar

| Modul | API prefix | Holat |
|-------|-----------|-------|
| Autentifikatsiya | `/auth` | JWT login, `/auth/me` |
| Kompaniyalar | `/companies` | List + create (admin) |
| Rollar | `/roles` | List + create (admin) |
| Foydalanuvchilar | `/users` | List + create (admin) |
| Filiallar | `/branches` | List + create |
| Omborlar | `/warehouses` | List + create |
| Kategoriyalar | `/categories` | To'liq CRUD + deactivate |
| Birliklar | `/units` | To'liq CRUD + deactivate |
| Mahsulotlar | `/products` | To'liq CRUD + deactivate |
| Mijozlar | `/clients` | To'liq CRUD + deactivate |
| Sotuv buyurtmalari | `/sales-orders` | CRUD + lifecycle + WMS |
| Integratsiya | `/integration-jobs` | Outbox navbat |
| WMS callback | `/wms` | Inbound fulfillment |
| To'lovlar | `/payments` | Create + list + summary |
| Fakturalar | `/invoices` | CRUD + issue/cancel |
| Allocatsiya | `/payment-allocations` | To'lov ↔ faktura |
| Qarzdorlik | `/receivables` | Aging + statement |

### 2.2. Ma'lumotlar bazasi

Alembic migratsiyalar zanjiri:

| Revision | Mazmuni |
|----------|---------|
| `0001` | companies, roles, users, branches, warehouses |
| `0002` | categories, units, products |
| `0003` | clients |
| `0004` | sales_orders, sales_order_items |
| `0005` | WMS fulfillment maydonlari |
| `0006` | integration_jobs, WMS metadata |
| `0007` | payments |
| `0008` | invoices, invoice_items, payment_allocations |

### 2.3. Xavfsizlik va tenant

- JWT claims: `user_id`, `company_id`, `exp`
- Barcha biznes jadvallarida `company_id`
- `Company.tenant_mode`: `shared` / `dedicated` (kelajak uchun)
- Admin: `role.code === "admin"`

### 2.4. Deploy

- Render Blueprint: `render.yaml`
- Startup: DB ping + `alembic upgrade head`
- Health check: `GET /health`

---

## 3. Bugun bajarilgan ishlar (2026-06-10)

### 3.1. Batafsil loyiha hujjati

**Fayl:** [`LOYIHA_BATAFSIL_HISOBOT.md`](./LOYIHA_BATAFSIL_HISOBOT.md)

15 bo'lim: arxitektura, modellar, API endpointlari, WMS integratsiyasi, moliyaviy modullar, deploy, konfiguratsiya, roadmap.

### 3.2. ERP Admin Panel

**Papka:** [`admin-panel/`](./admin-panel/)  
**Arxitektura:** [`admin-panel/ARCHITECTURE.md`](./admin-panel/ARCHITECTURE.md)

#### Texnologiyalar

| Texnologiya | Versiya / izoh |
|-------------|----------------|
| Next.js | 15.5 (App Router) |
| React | 19 |
| TypeScript | 5.x |
| Tailwind CSS | 4 |
| UI | Shadcn-style komponentlar |
| Server state | TanStack Query 5 |
| Client state | Zustand (persist) |
| Formlar | React Hook Form + Zod 3 |
| HTTP | Axios |
| Toast | Sonner |
| Theme | next-themes (light/dark/system) |

#### Infratuzilma

| Komponent | Joylashuv | Vazifa |
|-----------|-----------|--------|
| API client | `src/lib/api/client.ts` | Bearer JWT, 401 → logout |
| API modullar | `src/lib/api/modules/*.ts` | Typed CRUD har resurs uchun |
| Xato boshqaruvi | `src/lib/api/errors.ts` | ApiError, toast xabarlari |
| Auth store | `src/stores/auth-store.ts` | Token + user (persist) |
| UI store | `src/stores/ui-store.ts` | Sidebar holati |
| Permissions | `src/config/permissions.ts` | admin / manager / viewer |
| Navigation | `src/config/navigation.ts` | Sidebar menu + filter |
| CRUD config | `src/config/resources/*.ts` | ResourceConfig generator |

#### Layout va autentifikatsiya

- **Login** — `/(auth)/login` — email + parol → JWT
- **Protected routes** — `AuthGuard` dashboard layout ichida
- **Sidebar** — permission-based menu (11 ta band)
- **Navbar** — theme toggle, foydalanuvchi menyusi, chiqish
- **Responsive** — mobile: Sheet sidebar; desktop: collapsible sidebar

#### Qayta ishlatiladigan komponentlar

| Komponent | Fayl | Vazifa |
|-----------|------|--------|
| DataTable | `components/data-table/data-table.tsx` | Sort, pagination, qidiruv |
| ResourceForm | `components/forms/resource-form.tsx` | RHF + Zod, config-driven |
| ResourceListPage | `components/crud/resource-list-page.tsx` | Generic ro'yxat |
| ResourceFormPage | `components/crud/resource-form-page.tsx` | Generic create/edit |
| ResourceDetailPage | `components/crud/resource-detail-page.tsx` | Generic view |
| PermissionGuard | `components/crud/permission-guard.tsx` | RBAC action filter |
| KpiCard | `components/shared/kpi-card.tsx` | Dashboard kartalar |
| PageHeader | `components/shared/page-header.tsx` | Sarlavha + breadcrumb |
| StatusBadge | `components/shared/status-badge.tsx` | Enum holat ranglari |

#### Dashboard KPI kartalari

| KPI | Manba |
|-----|-------|
| Total Products | `GET /products/` |
| Total Clients | `GET /clients/` |
| Total Sales Orders | `GET /sales-orders/` |
| Open Orders | Status filter (completed/cancelled dan tashqari) |
| Invoices Outstanding | `outstanding_amount` yig'indisi |
| Payments Received | Faol to'lovlar `amount` yig'indisi |

#### Modul sahifalari

| Modul | List | Create | Edit | View | Eslatma |
|-------|------|--------|------|------|---------|
| Dashboard | ✅ | — | — | — | 6 KPI |
| Products | ✅ | ✅ | ✅ | ✅ | To'liq CRUD |
| Clients | ✅ | ✅ | ✅ | ✅ | To'liq CRUD |
| Sales Orders | ✅ | ✅ | * | ✅ | Lifecycle actionlar |
| Warehouses | ✅ | ✅ | — | ✅ | Backend: list+create |
| Payments | ✅ | ✅ | — | ✅ | Backend: create only |
| Invoices | ✅ | ✅ | * | ✅ | Issue/cancel actionlar |
| Receivables | ✅ | — | — | — | Aging bucketlar |
| Users | ✅ | ✅ | — | ✅ | Admin only |
| Roles | ✅ | ✅ | — | ✅ | Admin only |
| Settings | — | — | — | ✅ | Profil + theme |

`*` — edit formlari keyingi iteratsiyada to'ldiriladi

#### Build natijasi

```
npm run build — MUVAFFAQIYATLI
24 ta route (login + dashboard + modullar)
```

#### Backend o'zgarishi (admin panel uchun)

`app/main.py` ga CORS middleware qo'shildi:

```python
allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
```

---

## 4. Hujjatlar ro'yxati

| Fayl | Maqsad |
|------|--------|
| [`README.md`](./README.md) | Backend quick start |
| [`LOYIHA_BATAFSIL_HISOBOT.md`](./LOYIHA_BATAFSIL_HISOBOT.md) | To'liq texnik hujjat (backend) |
| [`ISHLAR_HISOBOTI.md`](./ISHLAR_HISOBOTI.md) | Ushbu fayl — bajarilgan ishlar hisoboti |
| [`Hisobot.md`](./Hisobot.md) | Ishlar jurnali (changelog) |
| [`admin-panel/README.md`](./admin-panel/README.md) | Frontend quick start |
| [`admin-panel/ARCHITECTURE.md`](./admin-panel/ARCHITECTURE.md) | Frontend arxitektura |
| [`admin-panel/.env.example`](./admin-panel/.env.example) | Frontend muhit o'zgaruvchilari |
| [`.env.example`](./.env.example) | Backend muhit o'zgaruvchilari |

---

## 5. Ishga tushirish tartibi

### 5.1. Backend

```bash
cd c:\Users\hp\Desktop\ERP

# 1. Muhit
cp .env.example .env
# ADMIN_EMAIL, ADMIN_PASSWORD, DATABASE_URL ni tahrirlang

# 2. PostgreSQL ishga tushirilgan bo'lishi kerak
alembic upgrade head
python scripts/seed.py

# 3. API
uvicorn app.main:app --reload
```

Tekshiruv: `http://127.0.0.1:8000/health` → `{"status":"ok"}`

### 5.2. Admin Panel

```bash
cd c:\Users\hp\Desktop\ERP\admin-panel

cp .env.example .env.local
npm install
npm run dev
```

Brauzer: `http://localhost:3000/login`

### 5.3. Login ma'lumotlari

| Maydon | Qayerdan |
|--------|----------|
| Email | `.env` dagi `ADMIN_EMAIL` |
| Parol | `.env` dagi `ADMIN_PASSWORD` |

**Muhim:** Admin panel o'zi foydalanuvchi yaratmaydi. Birinchi admin faqat `python scripts/seed.py` orqali yaratiladi.

Default (`.env.example`):

```
ADMIN_EMAIL=admin@erp.uz
ADMIN_PASSWORD=change-me-strong-password
```

---

## 6. Hozirgi holat va muammolar

### 6.1. Nima ishlayapti

| Komponent | Holat |
|-----------|-------|
| Admin panel (`npm run dev`) | ✅ Ishga tushgan (`localhost:3000`) |
| Admin panel (`npm run build`) | ✅ Muvaffaqiyatli |
| Backend kod | ✅ Tayyor |
| Hujjatlar | ✅ Yozilgan |

### 6.2. Nima ishlamayapti (mahalliy muhit)

| Muammo | Sabab | Yechim |
|--------|-------|--------|
| Login xatosi | Backend ishlamayapti | PostgreSQL ishga tushiring |
| Backend startup xato | `Connection refused :5432` | PostgreSQL o'rnating/ishga tushiring |
| Foydalanuvchi topilmaydi | Seed qilinmagan | `python scripts/seed.py` |
| `.env` yo'q | Faqat `.env.example` bor | `cp .env.example .env` |

### 6.3. Aniqlangan xato (terminal)

```
psycopg2.OperationalError: connection to server at "localhost" port 5432 failed: Connection refused
Application startup failed. Exiting.
```

---

## 7. Keyingi qadamlar

| # | Vazifa | Ustuvorlik |
|---|--------|------------|
| 1 | PostgreSQL o'rnatish va ishga tushirish | Yuqori |
| 2 | `.env` yaratish + `seed.py` + backend ishga tushirish | Yuqori |
| 3 | Login test (admin panel ↔ backend) | Yuqori |
| 4 | Sales Order edit formasi (line items) | O'rta |
| 5 | Invoice edit formasi | O'rta |
| 6 | Payment Allocations UI | O'rta |
| 7 | Integration Jobs admin sahifasi | Past |
| 8 | OpenAPI codegen (TypeScript typelar) | Past |

---

## 8. O'zgartirishlar xulosasi

### Yaratilgan yangi fayllar/papkalar

```
admin-panel/                    # Butun frontend loyiha
├── ARCHITECTURE.md
├── README.md
├── .env.example
└── src/
    ├── app/(auth)/login/
    ├── app/(dashboard)/        # 32 ta sahifa
    ├── components/ui/          # Shadcn primitives
    ├── components/layout/      # Sidebar, Navbar, AppShell
    ├── components/crud/        # CRUD generator
    ├── components/data-table/
    ├── components/forms/
    ├── config/                 # navigation, permissions, resources
    ├── features/               # modul columns, schemas
    ├── lib/api/modules/        # typed API
    ├── stores/
    └── hooks/

LOYIHA_BATAFSIL_HISOBOT.md     # Backend batafsil hujjat
ISHLAR_HISOBOTI.md               # Ushbu hisobot
```

### O'zgartirilgan mavjud fayllar

| Fayl | O'zgarish |
|------|----------|
| `app/main.py` | CORS middleware (`localhost:3000`) |
| `Hisobot.md` | 2026-06-10 yozuvlari qo'shildi |

---

## 9. Xulosa

**Bugun amalga oshirildi:**

1. Loyiha haqida to'liq texnik hujjat (`LOYIHA_BATAFSIL_HISOBOT.md`)
2. Enterprise darajadagi ERP Admin Panel (`admin-panel/`)
3. 11 modul, 24 route, production-ready build
4. JWT auth, permission menu, CRUD generator arxitekturasi
5. Backend CORS sozlash

**Hali kutmoqda:**

- Mahalliy muhit to'liq sozlash (PostgreSQL + seed + login)
- Ba'zi edit formlar (sales orders, invoices)
- Payment allocations va integration jobs UI

---

*Hisobot sanasi: 2026-06-10. Yangilanishlar uchun [`Hisobot.md`](./Hisobot.md) (changelog) ga qarang.*

# ERP backend — ishlar hisoboti

Bu fayl loyihada bajarilgan asosiy ishlarni va qararlarni yozib borish uchun. **Har muhim o‘zgarishdan keyin** shu yerga qisqa yozuv qo‘shiladi (qoida: `.cursor/rules/hisobot-yangilash.mdc`).

---

## Loyiha haqida

| Parametr | Qiymat |
|----------|--------|
| Nom | Core ERP API (`erp-backend`) |
| Stack | FastAPI, PostgreSQL, SQLAlchemy 2.x, Alembic, Pydantic v2 |
| Tenant | `company_id` + `Company.tenant_mode` (`shared` / `dedicated`) |

---

## 2026-06-12 — Admin panel UI redesign (Triad SaaS)

- Triad indigo dizayn tizimi: `globals.css` tokenlar (primary 238°, semantic success/warning/info, sidebar, `--radius: 0.75rem`), `config/design.ts`.
- App shell: guruhlangan sidebar (main/sales/finance/admin), subtle active holat, collapsed tooltip, navbar glass + avatar ring, `max-w-7xl` content.
- Dashboard: welcome banner, rangli KPI kartalar, tezkor amallar, tenant info; `KpiCard` accent prop; receivables `KpiCard` ga o'tkazildi.
- Shared UI: `PageHeader`, `DataTable`, yangi `EmptyState`; CRUD detail/form vizual yaxshilash.
- Login split layout (indigo brand panel + forma); Settings section kartalar.
- i18n: nav guruhlari, dashboard quick actions, auth brand matnlari (uz/en/ru). `npm run build` muvaffaqiyatli.

## 2026-06-12 — Qarzdorlik sahifasi crash tuzatildi

- Sabab: frontend `buckets` kutgan, backend `summary` (GlobalAgingResponse) qaytaradi — `data.buckets.map` client-side exception.
- `receivables/page.tsx` API formatiga moslashtirildi; aging bucket kartalari va faktura soni `/receivables/aging/invoices` dan hisoblanadi.

## 2026-06-12 — Technology stack audit (TECH_STACK_AUDIT.md)

- Repozitoriya bo'yicha to'liq texnologiya audit: backend (FastAPI), frontend (Next.js), DB, worker, WMS, infra, deploy.
- Mobil ilova repoda yo'q; CI/CD, Docker, monitoring bo'shliqlari va 100/1k/10k user scale tavsiyalari hujjatlashtirildi.

## 2026-06-12 — Admin panel 3 tilli interfeys (UZ / EN / RU)

- `admin-panel/src/lib/i18n/` — yengil custom i18n: `messages/{uz,en,ru}.ts` lug'atlar, `locale-store.ts` (Zustand persist, default `uz`), `translate.ts` (`tGlobal`, `MessageKey` tip), `useT()` hook va `T` komponent.
- `LanguageSwitcher` navbar ga (globus tugma) va Settings ga (Til select) qo'shildi; `<html lang>` locale o'zgarganda yangilanadi.
- Barcha UI matnlar kalitlarga o'tkazildi: navigation, resource configlar (`labelKey`), 8 ta columns fayl (`<T k=...>`), DataTable, ResourceForm, CRUD sahifalar, StatusBadge (status enum tarjimasi), login, dashboard KPI, receivables, settings, toastlar va Zod validatsiya xabarlari.
- `formatMoney`/`formatDate`/`formatDateTime` endi joriy locale (`uz-UZ`/`en-US`/`ru-RU`) bo'yicha formatlaydi. `npm run build` muvaffaqiyatli (33 route).

## 2026-06-12 — Production server hujjati (vm57620)

- `SERVER.md`: `/var/www/erp-backend`, `erp-backend.service`, nginx → uvicorn:8000, deploy/tekshiruv buyruqlari.
- CORS fix (`a844e1e`) serverda deploy qilindi; OPTIONS preflight OK (`api.triad.uz` + Vercel origin).

## 2026-06-10 — Production CORS (Vercel + api.triad.uz)

- `app/main.py` + `app/core/config.py`: CORS endi `CORS_ORIGINS` va `CORS_ALLOW_ORIGIN_REGEX` orqali sozlanadi.
- Production: `https://erp-admin-five.vercel.app`; Vercel preview: `https://.*\.vercel\.app` regex.

## 2026-06-10 — ISHLAR_HISOBOTI.md

- `ISHLAR_HISOBOTI.md` — bugungi sessiya bo‘yicha to‘liq ishlar hisoboti (backend + admin panel + holat + keyingi qadamlar).

## 2026-06-10 — Sessiya yakuni va ishga tushirish holati

- Admin panel `npm run build` muvaffaqiyatli; 24 ta route (login + 11 modul).
- Foydalanuvchi login muammosi: `.env` (ADMIN_*) va `scripts/seed.py` hali ishga tushirilmagan; PostgreSQL `localhost:5432` ulanmagan (backend startup xato).
- Login: faqat seed qilingan `ADMIN_EMAIL` / `ADMIN_PASSWORD` — admin panel o‘zi foydalanuvchi yaratmaydi.

## 2026-06-10 — ERP Admin Panel (Next.js 15)

- `admin-panel/` — professional admin UI: Next.js 15, React 19, TypeScript, Tailwind 4, Shadcn-style UI.
- Auth (JWT + Zustand persist), protected routes, sidebar, navbar, dark/light mode.
- TanStack Query + Axios API client, global error handling, Sonner toast.
- Permission-based menu (`admin` / `manager` / `viewer`), CRUD generator (`ResourceConfig`).
- Modullar: Dashboard (6 KPI), Products, Clients, Sales Orders, Warehouses, Payments, Invoices, Receivables, Users, Roles, Settings.
- Backend: FastAPI ga CORS qo‘shildi (`localhost:3000`) — admin panel uchun.

## 2026-06-10 — Batafsil loyiha hisoboti

- `LOYIHA_BATAFSIL_HISOBOT.md` — arxitektura, modellar, API, WMS, AR modullari, deploy va roadmap bo‘yicha to‘liq hujjat.

## 2026-03-21 — Asosiy fondatsiya

- FastAPI ilova: kompaniyalar, rollar, foydalanuvchilar, filiallar, omborlar.
- `app/core`: `config`, `database`, `dependencies`, `security`, `exceptions`.
- Alembic: boshlang‘ich migratsiya `0001_initial_schema`.
- Ko‘p ijarachi tuzilma: barcha tenant jadvallarida `company_id`.

## 2026-03-21 — Repozitoriya tuzilmasi (Render uchun)

- Muammo: `requirements.txt` ichki `erp-backend/` papkasida, Render ildizdan qidirardi.
- Yechim: barcha loyiha fayllari **repozitoriya ildiziga** ko‘chirildi (`app/`, `alembic/`, `requirements.txt`, …).
- `render.yaml`: `rootDir` olib tashlandi; build/start ildizdan.
- `runtime.txt` (Python 3.12.8), `Procfile` (uvicorn).

## 2026-03-21 — GitHub

- Remote: `jaloliddinmusayev/erp-backend`, keyin `core-erp/erp-backend` ga to‘liq kod **force push** (avval faqat README bo‘lgan repoga).

## 2026-03-21 — JWT autentifikatsiya

- `POST /auth/login` — email + parol → `access_token` (JWT: `user_id`, `company_id`, `exp`).
- `get_current_user` — `Authorization: Bearer`; noto‘g‘ri token **401**.
- Himoya: `companies`, `users`, `branches`, shuningdek `roles` va `warehouses` (tenant konteksti uchun).
- Ro‘yxat endpointlarida `company_id` query olib tashlandi; tenant `current_user.company_id` dan.
- Create body dagi `company_id` joriy foydalanuvchi tenantiga majburan moslashtiriladi.

## 2026-03-21 — Bootstrap, `/auth/me`, admin tekshiruvi

- **Seed:** `app/services/bootstrap_service.py` + `scripts/seed.py` — idempotent: kompaniya `core`, rol `admin`, foydalanuvchi `.env` dagi `ADMIN_EMAIL` / `ADMIN_PASSWORD` bo‘yicha (faqat bo‘sh DB uchun). **Ilovani har ishga tushirishda emas**, alohida skript (multi-instance xavfsiz).
- **GET `/auth/me`** — JWT bilan joriy foydalanuvchi + rol.
- JWT da `user_id`, `company_id`, `exp`.
- `get_current_user` — `joinedload` orqali rol; `require_admin` — yangi kompaniya / foydalanuvchi / rol yaratish uchun (POST `/companies`, `/users`, `/roles`).

---

## 2026-03-21 — Production startup va JWT

- **Lifespan:** DB `SELECT 1`, logging, `alembic upgrade head` (`RUN_MIGRATIONS_ON_STARTUP`, Render uchun).
- **GET `/health`** — `{"status":"ok"}`.
- **JWT:** `user_id`, `company_id`, `exp`.
- **Seed:** `ADMIN_EMAIL`, `ADMIN_PASSWORD` (`.env`); hardcode parol olib tashlandi.

## 2026-03-21 — Mahsulot master ma’lumotlari

- Modellar: `Category`, `Unit`, `Product` (`company_id`, kodlar kompaniya bo‘yicha noyob, barcode qisman noyob indeks).
- Servislar va route’lar: `/categories`, `/units`, `/products` — faqat JWT; `deactivate` soft-delete.
- Alembic: `0002_product_master`.

## 2026-03-21 — Mijozlar (clients)

- Model `Client` (`company_id`, noyob `code` per tenant, `contact_person`, qidiruv: kod/nom/telefon).
- `/clients` — JWT; `GET /` da `search`, `is_active` query.
- Alembic: `0003_clients`.

## 2026-03-21 — Sotuv buyurtmalari (sales orders)

- Modellar: `SalesOrder`, `SalesOrderItem` (`company_id`, `order_number` per tenant noyob).
- `line_total`, `total_amount` — backend; `PUT` faqat `draft`; `confirm` / `cancel` / `deactivate` + lifecycle endpointlar (to‘liq ro‘yxat: WMS tayyorligi bo‘limi).
- `/sales-orders` — JWT; ro‘yxatda `status`, `fulfillment_status`, `client_id`, sanalar, `search`.
- Alembic: `0004_sales_orders` (asosiy jadval), keyin `0005` (qator `ordered_qty` / fulfillment).

## 2026-03-21 — Sales orders: WMS tayyorligi

- `status` kengaytirildi: `sent_to_wms`, `in_progress`, `completed` (+ avvalgilar).
- Sarlavha: `fulfillment_status` (pending / partial / fulfilled), `fulfilled_at`, `is_sent_to_wms`.
- Qator: `ordered_qty`, `fulfilled_qty`; qoldiq API da hisoblanadi.
- Endpointlar: `send-to-wms`, `mark-in-progress`, `update-fulfillment`, `complete`.
- Kelajak uchun: `app/integration/wms/` (hozircha faqat izoh).
- Alembic: `0005_sales_order_wms_fulfillment`.

## 2026-03-21 — ERP → WMS integratsiya fondatsiyasi

- `SalesOrder`: `wms_order_id`, `integration_status`, `sent_to_wms_at`, `last_sync_error`.
- `IntegrationJob` (outbox): `payload_json`, `status`, `attempt_count`, tenant `company_id`.
- `POST /sales-orders/{id}/enqueue-wms` — navbat; `PATCH send-to-wms` xuddi shu enqueue.
- Admin: `PATCH /integration-jobs/{id}/mark-sent|mark-failed` (worker simulyatsiyasi).
- `POST /wms/callback/sales-orders/{id}` — JWT tenant, fulfilled_qty yangilash.
- Haqiqiy tashqi WMS HTTP hali yo‘q; worker keyin `integration_jobs` dan o‘qiydi.
- Alembic: `0006_integration_jobs_wms_metadata`.

## 2026-03-21 — WMS integration worker

- `scripts/run_worker.py` — `pending` joblarni SKIP LOCKED bilan olish, `processing` → adapter → `sent` / qayta urinish / `failed`.
- `app/integration/wms/client.py` — `MockWmsClient`, `HttpWmsClient` (TODO: URL, javob formati).
- `app/integration/wms/service.py` — `send_sales_order_payload`.
- Sozlamalar: `WMS_MOCK_MODE`, `INTEGRATION_JOB_MAX_ATTEMPTS`, `INTEGRATION_WORKER_BATCH_SIZE`, stale lease qayta tiklash.
- Haqiqiy WMS shartnomasi tasdiqlanganda `HttpWmsClient` va mapping yangilanadi.

## 2026-03-21 — Qo‘lda to‘lovlar (payments)

- Model `Payment`: mijoz, ixtiyoriy `sales_order_id`, `amount`, `payment_date`, `payment_method` (cash / bank_transfer / card / other), `created_by_user_id`.
- `/payments` — JWT; client/order tenant tekshiruvi; bekor buyurtmaga yangi to‘lov taqiq.
- Qoldiq: `client-summary` (faol buyurtmalar `total_amount` yig‘indisi − faol to‘lovlar), `sales-order-summary` (shu buyurtmaga bog‘langan to‘lovlar).
- `is_active=false` yig‘indilarga kirmaydi.
- Bank integratsiyasi keyingi bosqich; hisob-faktura va allocatsiya — `0008` (quyida).
- Alembic: `0007_payments`.

## 2026-03-21 — Hisob-fakturalar va to‘lov taqsimoti (AR)

- Modellar: `Invoice` (draft / issued / partially_paid / paid / cancelled), `InvoiceItem` (snapshot), `PaymentAllocation` (to‘lov ↔ faktura, `is_active` bilan yumshoq bekor, hard delete yo‘q).
- `/invoices` — qo‘lda yoki `from-sales-order` (faqat confirmed+ buyurtma); `issue` dan keyin allocatsiya; `cancel` faqat allocatsiyasiz.
- `/payment-allocations` — bir to‘lov bir nechta fakturaga; miqdor to‘lovning unallocated va faktura outstanding dan oshmasin.
- `GET /payments/{id}/unallocated-amount` — qolgan mablag‘.
- To‘lov/faktura `deactivate` faqat allocatsiya bo‘lmasa (ma’lumot izchiligi).
- `app/core/money.py` — umumiy `quantize_money`.
- Alembic: `0008_invoices_payment_allocations`.

## 2026-03-21 — Qarzdorlik yoshi (aging) va mijoz statement

- `/receivables`: global va mijoz bo‘yicha **aging** (ochiq fakturalar, `due_date` yoki `invoice_date`), **`GET /aging/invoices`** tafsilot.
- **Statement**: faktura (debit) va to‘lov (kredit); allocatsiya — faqat izoh (0 summa), running balance ikki posting turiga asoslangan.
- Yordamchilar: `receivable_helpers` (`overdue_days`, `aging_bucket`).

## 2026-03-21 — Hisobot va izohlar

- JWT bo‘yicha faqat `user_id`, `company_id`, `exp` qoldirildi; `app/core/security.py` modul izohi moslashtirildi.
- Seed tavsifida aniq parol ko‘rsatilmaydi — faqat `ADMIN_EMAIL` / `ADMIN_PASSWORD` (.env).
- Terminologiya: omborlar (Hisobotda bir xil yozilish).

## Keyingi qadamlar (eslatma)

- Birinchi ishga tushirish: migratsiya (startup yoki `alembic upgrade head`), `.env` da `ADMIN_*`, `python scripts/seed.py`, login.
- Alembic: yangi modellar uchun `revision --autogenerate`.
- Render: `DATABASE_URL`, `SECRET_KEY`, migratsiya (`alembic upgrade head`).

---

## O‘zgartirishlar jadvali

| Sana | Qisqa mazmun |
|------|----------------|
| 2026-03-21 | Fondatsiya, flatten repo, Render, GitHub sync, JWT auth |
| 2026-03-21 | Bootstrap seed, GET /auth/me, require_admin, JWT user_id claim |
| 2026-03-21 | Startup migrations, /health, logging, ADMIN_* env, JWT faqat user_id+company_id |
| 2026-03-21 | Product master: categories, units, products + migratsiya 0002 |
| 2026-03-21 | Clients master + migratsiya 0003 |
| 2026-03-21 | Hisobot: JWT/seed matnlari, termin «omborlar» |
| 2026-03-21 | Sales orders + migratsiya 0004 |
| 2026-03-21 | Sales orders WMS tayyorligi + migratsiya 0005 |
| 2026-03-21 | Integration jobs + WMS metadata + callback API + 0006 |
| 2026-03-21 | WMS outbound worker + mock/HTTP adapter + scripts/run_worker.py |
| 2026-03-21 | Manual payments + receivable summaries + migratsiya 0007 |
| 2026-03-21 | Invoices + payment allocations (AR) + migratsiya 0008 |
| 2026-03-21 | Receivable aging + client statement (`/receivables`) |
| 2026-06-10 | `LOYIHA_BATAFSIL_HISOBOT.md` — batafsil loyiha hisoboti hujjati |
| 2026-06-10 | `admin-panel/` — Next.js ERP Admin Panel + backend CORS |
| 2026-06-10 | `ISHLAR_HISOBOTI.md` — bajarilgan ishlar hisoboti (MD) |
| 2026-06-12 | Production CORS deploy + `SERVER.md` (vm57620 deploy ma'lumotlari) |

*Yangi qatorlarni yuqoriga yoki shu jadvalga qo‘shing.*

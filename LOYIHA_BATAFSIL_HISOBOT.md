# Core ERP API — batafsil loyiha hisoboti

**Sana:** 2026-06-10  
**Loyiha nomi:** Core ERP API (`erp-backend`)  
**Bosqich:** Phase 1 — fondatsiya  
**Repozitoriya:** `core-erp/erp-backend` (GitHub)

---

## 1. Umumiy ma'lumot

**Core ERP API** — ko‘p ijarachi (multi-tenant) korxona resurslarini boshqarish uchun mo‘ljallangan **backend REST API** loyihasi. Hozirgi holatda faqat server qismi (FastAPI) mavjud; frontend alohida reja qilingan.

Loyiha quyidagi biznes jarayonlarini qamrab oladi:

- Korxona (tenant) va foydalanuvchi boshqaruvi
- Mahsulot katalogi (kategoriya, birlik, mahsulot)
- Mijozlar ro‘yxati
- Sotuv buyurtmalari va ularning hayotiy tsikli
- ERP → WMS (ombor tizimi) integratsiyasi
- Qo‘lda to‘lovlar, hisob-fakturalar va qarzdorlik hisobi (Accounts Receivable)

**Hozircha qamrab olinmagan:** bank feed avtomatizatsiyasi, GL (buxgalteriya jurnallari), Docker, frontend, haqiqiy WMS HTTP shartnomasi (mock rejim ishlaydi).

---

## 2. Texnologik stack

| Komponent | Texnologiya | Versiya / izoh |
|-----------|-------------|----------------|
| API framework | FastAPI | ≥ 0.115 |
| ASGI server | Uvicorn | ≥ 0.32 |
| Ma'lumotlar bazasi | PostgreSQL | SQLAlchemy 2.x orqali |
| ORM | SQLAlchemy | ≥ 2.0.36 |
| DB drayver | psycopg2-binary | ≥ 2.9 |
| Validatsiya | Pydantic v2 | ≥ 2.10 |
| Sozlamalar | pydantic-settings | `.env` faylidan |
| Migratsiyalar | Alembic | 8 ta revision |
| Parol xeshlash | passlib + bcrypt | |
| JWT | python-jose | HS256 algoritm |
| HTTP klient (WMS) | httpx | ≥ 0.28 |
| Python | 3.12.8 | `runtime.txt` |

---

## 3. Arxitektura

### 3.1. Ko‘p ijarachi (multi-tenant) modeli

Barcha biznes jadvallarida `company_id` ustuni mavjud. Tenant konteksti **JWT token** orqali aniqlanadi:

- Token da: `user_id`, `company_id`, `exp`
- Himoyalangan endpointlarda `company_id` query yoki body orqali yuborilmaydi
- Yaratish (create) operatsiyalarida body dagi `company_id` joriy foydalanuvchi tenantiga majburan moslashtiriladi

`Company` modelida `tenant_mode` maydoni:

| Qiymat | Ma'nosi |
|--------|---------|
| `shared` | Barcha tenantlar bir PostgreSQL bazasida (hozirgi holat) |
| `dedicated` | Kelajakda har bir kompaniya uchun alohida DB (hali amalga oshirilmagan) |

### 3.2. Qatlamlar (layered architecture)

```
HTTP so'rov
    ↓
app/api/routes/     — yupqa HTTP qatlam (routing, status kodlar)
    ↓
app/services/       — biznes logika (tenant-aware, company_id parametri)
    ↓
app/models/         — SQLAlchemy ORM modellar
    ↓
PostgreSQL
```

Qo'shimcha modullar:

- `app/core/` — konfiguratsiya, DB engine, xavfsizlik, dependency injection
- `app/schemas/` — Pydantic request/response DTO
- `app/integration/wms/` — WMS adapter (Mock + HTTP)
- `app/workers/` — fon jarayonlari (integration worker)

### 3.3. Dizayn tamoyillari

1. **Service funksiyalari** har doim `db: Session` va `company_id: int` qabul qiladi — kelajakda dedicated DB ga o‘tishda imzo o‘zgarmaydi.
2. **Soft-delete:** ko‘p modellarda `is_active=false` (hard delete emas).
3. **Outbox pattern:** WMS ga yuborish `IntegrationJob` jadvali orqali — API va worker ajratilgan.
4. **Pul hisobi:** `Numeric(18, 4)` + `app/core/money.py` dagi `quantize_money`.

---

## 4. Ma'lumotlar bazasi sxemasi

### 4.1. Migratsiyalar zanjiri

| Revision | Fayl | Mazmuni |
|----------|------|---------|
| `0001` | `initial_schema` | companies, roles, users, branches, warehouses |
| `0002` | `product_master` | categories, units, products |
| `0003` | `clients` | mijozlar jadvali |
| `0004` | `sales_orders` | sotuv buyurtmalari va qatorlari |
| `0005` | `sales_order_wms_fulfillment` | fulfillment_status, ordered_qty, fulfilled_qty |
| `0006` | `integration_jobs_wms_metadata` | IntegrationJob, WMS metadata maydonlari |
| `0007` | `payments` | qo‘lda to‘lovlar |
| `0008` | `invoices_payment_allocations` | fakturalar, qatorlar, to‘lov taqsimoti |

Migratsiyalarni qo‘llash:

```bash
alembic upgrade head
```

Ilova ishga tushganda avtomatik: `RUN_MIGRATIONS_ON_STARTUP=true` (default).

### 4.2. Modellar ro‘yxati

#### Asosiy infratuzilma

| Model | Jadval | Asosiy maydonlar |
|-------|--------|------------------|
| `Company` | `companies` | name, code (global noyob), tenant_mode, is_active |
| `Role` | `roles` | company_id, name, code (tenant bo‘yicha noyob) |
| `User` | `users` | company_id, role_id, email (global noyob), password_hash |
| `Branch` | `branches` | company_id, name, code, address |
| `Warehouse` | `warehouses` | company_id, branch_id, name, code |

#### Mahsulot katalogi

| Model | Jadval | Asosiy maydonlar |
|-------|--------|------------------|
| `Category` | `categories` | company_id, name, code |
| `Unit` | `units` | company_id, name, code, symbol |
| `Product` | `products` | company_id, category_id, base_unit_id, name, code, barcode |

`Product` indekslari: `(company_id, code)` noyob; `(company_id, barcode)` qisman noyob (barcode NULL bo‘lsa indeksga kirmaydi).

#### Mijozlar va sotuv

| Model | Jadval | Asosiy maydonlar |
|-------|--------|------------------|
| `Client` | `clients` | company_id, code, name, phone, contact_person |
| `SalesOrder` | `sales_orders` | client_id, order_number, status, fulfillment_status, integration_status, total_amount |
| `SalesOrderItem` | `sales_order_items` | product_id, ordered_qty, fulfilled_qty, unit_price, line_total |

**SalesOrderStatus:** `draft` → `confirmed` → `sent_to_wms` → `in_progress` → `completed` (+ `cancelled`)

**FulfillmentStatus:** `pending`, `partial`, `fulfilled`

**IntegrationStatus:** `not_sent`, `pending`, `sent`, `acknowledged`, `failed`

#### Integratsiya

| Model | Jadval | Asosiy maydonlar |
|-------|--------|------------------|
| `IntegrationJob` | `integration_jobs` | entity_type, entity_id, event_type, payload_json, status, attempt_count |

**IntegrationJobStatus:** `pending` → `processing` → `sent` / `failed`

#### Moliya (Accounts Receivable)

| Model | Jadval | Asosiy maydonlar |
|-------|--------|------------------|
| `Payment` | `payments` | client_id, sales_order_id (ixtiyoriy), amount, payment_date, payment_method |
| `Invoice` | `invoices` | client_id, invoice_number, status, total_amount, paid_amount, outstanding_amount |
| `InvoiceItem` | `invoice_items` | product snapshot (code, name), quantity, unit_price, line_total |
| `PaymentAllocation` | `payment_allocations` | payment_id, invoice_id, allocated_amount, is_active |

**InvoiceStatus:** `draft` → `issued` → `partially_paid` → `paid` (+ `cancelled`)

**PaymentMethod:** `cash`, `bank_transfer`, `card`, `other`

---

## 5. Autentifikatsiya va xavfsizlik

### 5.1. JWT oqimi

1. `POST /auth/login` — email + parol → `access_token`
2. `GET /auth/me` — `Authorization: Bearer <token>` → foydalanuvchi + rol
3. Barcha himoyalangan route lar uchun xuddi shu header

### 5.2. Token tarkibi

```json
{
  "user_id": 1,
  "company_id": 1,
  "exp": 1710000000
}
```

- Algoritm: HS256
- Default muddati: 30 daqiqa (`ACCESS_TOKEN_EXPIRE_MINUTES`)
- Kalit: `SECRET_KEY` (`.env` da, production da kuchli qiymat talab qilinadi)

### 5.3. Rol va ruxsatlar

| Rol kodi | Huquqlar |
|----------|----------|
| `admin` | `POST /companies`, `POST /users`, `POST /roles`; integration job simulyatsiyasi |
| Boshqa rollar | Tenant doirasidagi CRUD (kelajakda granular RBAC rejalashtirilgan) |

`require_admin` dependency — `app/core/dependencies.py` da.

### 5.4. Bootstrap (birinchi admin)

```bash
python scripts/seed.py
```

`.env` da talab qilinadi: `ADMIN_EMAIL`, `ADMIN_PASSWORD`, ixtiyoriy `ADMIN_FULL_NAME`.

Idempotent: mavjud bo‘lsa qayta yaratmaydi. Yaratadi:
- Kompaniya: `core`
- Rol: `admin`
- Admin foydalanuvchi

**Eslatma:** seed ilova har ishga tushganda emas, alohida skript — multi-instance xavfsizligi uchun.

---

## 6. API endpointlari (to‘liq ro‘yxat)

### 6.1. Autentifikatsiya

| Method | Path | Tavsif |
|--------|------|--------|
| POST | `/auth/login` | Login, JWT olish |
| GET | `/auth/me` | Joriy foydalanuvchi |

### 6.2. Tenant boshqaruvi

| Prefix | Operatsiyalar | JWT | Admin |
|--------|---------------|-----|-------|
| `/companies` | POST, GET | — / — | POST admin |
| `/roles` | POST, GET | ✓ | POST admin |
| `/users` | POST, GET | ✓ | POST admin |
| `/branches` | POST, GET | ✓ | |
| `/warehouses` | POST, GET | ✓ | |

### 6.3. Mahsulot katalogi

| Prefix | Operatsiyalar |
|--------|---------------|
| `/categories` | CRUD + `PATCH .../deactivate` |
| `/units` | CRUD + `PATCH .../deactivate` |
| `/products` | CRUD + `PATCH .../deactivate`; `GET ?category_id=` filter |

### 6.4. Mijozlar

| Prefix | Operatsiyalar |
|--------|---------------|
| `/clients` | CRUD + `PATCH .../deactivate`; `GET ?search=&is_active=` |

### 6.5. Sotuv buyurtmalari

| Method | Path | Tavsif |
|--------|------|--------|
| POST | `/sales-orders/` | Yangi buyurtma (draft) |
| GET | `/sales-orders/` | Ro‘yxat (status, fulfillment_status, client_id, sanalar, search) |
| GET | `/sales-orders/{id}` | Bitta buyurtma |
| PUT | `/sales-orders/{id}` | Tahrirlash (faqat draft) |
| PATCH | `/sales-orders/{id}/confirm` | Tasdiqlash |
| PATCH | `/sales-orders/{id}/cancel` | Bekor qilish |
| PATCH | `/sales-orders/{id}/deactivate` | Soft-delete |
| POST | `/sales-orders/{id}/enqueue-wms` | WMS navbatiga qo‘shish |
| PATCH | `/sales-orders/{id}/send-to-wms` | Xuddi enqueue-wms |
| PATCH | `/sales-orders/{id}/mark-in-progress` | Jarayonda deb belgilash |
| PATCH | `/sales-orders/{id}/update-fulfillment` | fulfilled_qty yangilash |
| PATCH | `/sales-orders/{id}/complete` | Yakunlash |

### 6.6. WMS integratsiyasi

| Method | Path | Tavsif |
|--------|------|--------|
| GET | `/integration-jobs/` | Navbat ro‘yxati |
| GET | `/integration-jobs/{id}` | Bitta job |
| PATCH | `/integration-jobs/{id}/mark-sent` | Admin — simulyatsiya |
| PATCH | `/integration-jobs/{id}/mark-failed` | Admin — simulyatsiya |
| POST | `/wms/callback/sales-orders/{id}` | WMS dan fulfillment callback |

### 6.7. To‘lovlar

| Method | Path | Tavsif |
|--------|------|--------|
| POST | `/payments/` | Yangi to‘lov |
| GET | `/payments/` | Ro‘yxat (filterlar) |
| GET | `/payments/{id}` | Bitta to‘lov |
| GET | `/payments/{id}/unallocated-amount` | Taqsimlanmagan qoldiq |
| PATCH | `/payments/{id}/deactivate` | Soft-delete |
| GET | `/payments/client-summary/{client_id}` | Mijoz bo‘yicha qoldiq |
| GET | `/payments/sales-order-summary/{sales_order_id}` | Buyurtma bo‘yicha to‘lovlar |

### 6.8. Hisob-fakturalar

| Method | Path | Tavsif |
|--------|------|--------|
| POST | `/invoices/` | Qo‘lda faktura yaratish |
| POST | `/invoices/from-sales-order/{id}` | Buyurtmadan snapshot |
| GET | `/invoices/` | Ro‘yxat |
| GET | `/invoices/{id}` | Bitta faktura |
| PUT | `/invoices/{id}` | Tahrirlash (faqat draft) |
| PATCH | `/invoices/{id}/issue` | Chiqarish (outstanding = total) |
| PATCH | `/invoices/{id}/cancel` | Bekor (allocatsiyasiz) |
| PATCH | `/invoices/{id}/deactivate` | Soft-delete |

### 6.9. To‘lov taqsimoti

| Method | Path | Tavsif |
|--------|------|--------|
| POST | `/payment-allocations/` | To‘lovni fakturaga bog‘lash |
| GET | `/payment-allocations/` | Ro‘yxat |
| GET | `/payment-allocations/{id}` | Bitta allocatsiya |
| PATCH | `/payment-allocations/{id}/deactivate` | Bekor (balanslarni qaytaradi) |

### 6.10. Qarzdorlik (Receivables)

| Method | Path | Tavsif |
|--------|------|--------|
| GET | `/receivables/aging` | Tenant bo‘yicha aging bucketlar |
| GET | `/receivables/aging/invoices` | Faktura tafsiloti |
| GET | `/receivables/aging/client/{client_id}` | Mijoz bo‘yicha aging |
| GET | `/receivables/statements/client/{client_id}` | Mijoz statement |

**Aging bucketlar:** `current`, `1-30`, `31-60`, `61-90`, `90+` kun (due_date yoki invoice_date asosida).

**Statement:** `invoice_issued` (debit), `payment_received` (credit); `payment_allocated` — faqat audit (0 summa).

### 6.11. Tizim

| Method | Path | Javob |
|--------|------|-------|
| GET | `/` | `{"message": "Core ERP API is running"}` |
| GET | `/health` | `{"status": "ok"}` |
| GET | `/docs` | OpenAPI (Swagger UI) |

---

## 7. WMS integratsiyasi (batafsil)

### 7.1. Outbound oqim (ERP → WMS)

```
confirmed buyurtma
    ↓
POST /sales-orders/{id}/enqueue-wms
    ↓
IntegrationJob yaratiladi (status=pending, payload_json)
    ↓
integration_worker (scripts/run_worker.py)
    ↓
FOR UPDATE SKIP LOCKED — job olish
    ↓
status=processing → WMS adapter chaqiruvi
    ↓
Muvaffaqiyat: order → sent_to_wms, wms_order_id, sent_to_wms_at
Muvaffaqiyatsizlik: qayta urinish yoki failed (max 5 marta)
```

### 7.2. Inbound oqim (WMS → ERP)

```
POST /wms/callback/sales-orders/{id}
    ↓
fulfilled_qty yangilanadi
    ↓
fulfillment_status hisoblanadi (pending/partial/fulfilled)
```

### 7.3. Worker sozlamalari

| O'zgaruvchi | Default | Ma'nosi |
|-------------|---------|---------|
| `WMS_MOCK_MODE` | `true` | Haqiqiy HTTP o‘rniga mock |
| `WMS_BASE_URL` | — | WMS server URL |
| `WMS_API_KEY` | — | API kalit |
| `INTEGRATION_JOB_MAX_ATTEMPTS` | 5 | Maksimal urinishlar |
| `INTEGRATION_WORKER_BATCH_SIZE` | 10 | Bir tsiklda joblar soni |
| `INTEGRATION_JOB_STALE_PROCESSING_SECONDS` | 900 | Crash recovery vaqti |
| `INTEGRATION_WORKER_LOOP_SECONDS` | 0 | 0 = bir marta chiqish (cron); >0 = daemon |

Worker ishga tushirish:

```bash
python scripts/run_worker.py
```

Render da: alohida **Background Worker** servisi.

### 7.4. Adapterlar

| Klass | Joylashuv | Holat |
|-------|-----------|-------|
| `MockWmsClient` | `app/integration/wms/client.py` | Ishlaydi |
| `HttpWmsClient` | `app/integration/wms/client.py` | TODO — vendor shartnomasi kutilmoqda |

---

## 8. Moliyaviy modullar (AR) — biznes qoidalari

### 8.1. Faktura hayotiy tsikli

1. **draft** — tahrirlash mumkin
2. **issue** — `outstanding_amount = total_amount`; allocatsiya boshlanadi
3. **partially_paid** — qisman to‘langan
4. **paid** — to‘liq to‘langan
5. **cancelled** — faqat allocatsiyasiz bekor qilish mumkin

Faktura yaratish usullari:
- Qo‘lda: `POST /invoices/` (qatorlar bilan)
- Buyurtmadan: `POST /invoices/from-sales-order/{id}` (faqat confirmed+ buyurtma, snapshot)

### 8.2. To‘lov taqsimoti qoidalari

- Bir to‘lov bir nechta fakturaga taqsimlanishi mumkin
- `allocated_amount` ≤ to‘lovning unallocated qismi
- `allocated_amount` ≤ faktura outstanding miqdori
- Allocatsiya qatorlari hard-delete qilinmaydi — faqat `deactivate`
- Deactivate qilganda `recalculate_invoice_balances` chaqiriladi

### 8.3. Qarzdorlik yoshi (Aging)

Hisobga olinadi:
- Faqat **active** fakturalar
- `outstanding_amount > 0`
- `draft` va `cancelled` **tashqarida**

`as_of_date` default — bugungi sana.

---

## 9. Loyiha fayl tuzilmasi

```
ERP/
├── app/
│   ├── main.py                 # FastAPI ilova, routerlar
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── database.py       # Engine, SessionLocal, Base
│   │   ├── dependencies.py   # get_db, get_current_user, require_admin
│   │   ├── security.py       # JWT, bcrypt
│   │   ├── exceptions.py     # Umumiy xatolar
│   │   ├── lifecycle.py      # Startup: DB ping, Alembic
│   │   └── money.py          # quantize_money
│   ├── models/                 # 15 ta SQLAlchemy model
│   ├── schemas/                # Pydantic DTO (har modul uchun)
│   ├── services/               # 19 ta biznes logika servisi
│   ├── api/routes/             # 17 ta route fayl
│   ├── integration/wms/        # WMS adapter
│   └── workers/                # integration_worker
├── alembic/
│   ├── env.py
│   └── versions/               # 0001 … 0008
├── scripts/
│   ├── seed.py                 # Bootstrap admin
│   └── run_worker.py           # Integration worker
├── .env.example
├── alembic.ini
├── requirements.txt
├── runtime.txt                 # Python 3.12.8
├── Procfile                    # uvicorn
├── render.yaml                 # Render Blueprint
├── start.sh                    # Unix start skripti
├── README.md
├── Hisobot.md                  # Ishlar jurnali (changelog)
└── LOYIHA_BATAFSIL_HISOBOT.md  # Ushbu hujjat
```

---

## 10. Konfiguratsiya (.env)

| O'zgaruvchi | Majburiy | Default | Tavsif |
|-------------|----------|---------|--------|
| `DATABASE_URL` | ✓ | localhost PostgreSQL | DB ulanish |
| `SECRET_KEY` | ✓ | change-me | JWT imzolash |
| `ADMIN_EMAIL` | seed uchun | — | Birinchi admin email |
| `ADMIN_PASSWORD` | seed uchun | — | Birinchi admin parol |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | 30 | Token muddati |
| `RUN_MIGRATIONS_ON_STARTUP` | | true | Startup da Alembic |
| `WMS_MOCK_MODE` | | true | Mock WMS |
| `DEBUG` | | false | Debug rejim |

To‘liq ro‘yxat: `.env.example`

---

## 11. Ishga tushirish (development)

```bash
# 1. Virtual muhit
python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # macOS/Linux

# 2. Bog'liqliklar
pip install -r requirements.txt

# 3. Muhit sozlamalari
cp .env.example .env
# DATABASE_URL, SECRET_KEY, ADMIN_* ni tahrirlang

# 4. Migratsiya
alembic upgrade head

# 5. Birinchi admin
python scripts/seed.py

# 6. API ishga tushirish
uvicorn app.main:app --reload

# 7. (Ixtiyoriy) Integration worker
python scripts/run_worker.py
```

**OpenAPI:** http://127.0.0.1:8000/docs

---

## 12. Production deploy (Render)

### Variant A — Blueprint (`render.yaml`)

1. Render → New → Blueprint
2. `DATABASE_URL` ni Environment da qo‘shing (Render PostgreSQL)
3. `SECRET_KEY` avtomatik generate qilinadi

### Variant B — Qo‘lda Web Service

| Parametr | Qiymat |
|----------|--------|
| Root Directory | bo‘sh (ildiz) |
| Build Command | `pip install --upgrade pip && pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Python | 3.12.8 |

**Background Worker** (WMS uchun):

- Start: `python scripts/run_worker.py`
- Cron: `*/2 * * * *` (har 2 daqiqada)

### Startup ketma-ketligi

1. Logging sozlash
2. `SELECT 1` — DB ulanish tekshiruvi
3. `alembic upgrade head` (agar `RUN_MIGRATIONS_ON_STARTUP=true`)
4. API tayyor

---

## 13. Servislar ro‘yxati

| Servis fayli | Vazifasi |
|--------------|----------|
| `auth_service.py` | Login, token yaratish |
| `bootstrap_service.py` | Seed logikasi |
| `company_service.py` | Kompaniyalar CRUD |
| `role_service.py` | Rollar CRUD |
| `user_service.py` | Foydalanuvchilar CRUD |
| `branch_service.py` | Filiallar CRUD |
| `warehouse_service.py` | Omborlar CRUD |
| `category_service.py` | Kategoriyalar CRUD |
| `unit_service.py` | O‘lchov birliklari CRUD |
| `product_service.py` | Mahsulotlar CRUD |
| `client_service.py` | Mijozlar CRUD |
| `sales_order_service.py` | Buyurtmalar + lifecycle + WMS |
| `integration_service.py` | IntegrationJob boshqaruvi |
| `payment_service.py` | To‘lovlar + summary |
| `invoice_service.py` | Fakturalar + lifecycle |
| `payment_allocation_service.py` | To‘lov taqsimoti |
| `receivable_service.py` | Aging hisoblash |
| `statement_service.py` | Mijoz statement |
| `receivable_helpers.py` | overdue_days, aging_bucket |

---

## 14. Kelajakdagi ishlar (roadmap)

| Yo‘nalish | Tavsif | Tayyorgarlik |
|-----------|--------|--------------|
| Dedicated DB | `Company.tenant_mode=dedicated` uchun alohida engine | Model va service imzolari tayyor |
| Granular RBAC | `Role.code` + route metadata | `require_admin` mavjud |
| Haqiqiy WMS HTTP | `HttpWmsClient` to‘ldirish | Adapter skeleti mavjud |
| Bank feeds | Avtomatik to‘lov import | Hali yo‘q |
| GL jurnallari | Buxgalteriya yozuvlari | Hali yo‘q |
| Docker | Konteynerizatsiya | Rejada, hali yo‘q |
| Frontend | Web/mobile UI | Backend API tayyor |
| Testlar | Unit/integration testlar | Hali minimal |

---

## 15. Xulosa

**Core ERP API** Phase 1 da quyidagilarni amalga oshirgan:

- Ko‘p ijarachi arxitektura (`company_id` + JWT)
- To‘liq mahsulot katalogi va mijozlar moduli
- Sotuv buyurtmalari hayotiy tsikli (draft dan completed gacha)
- WMS integratsiyasi fondatsiyasi (outbox + worker + mock adapter)
- Accounts Receivable: fakturalar, to‘lovlar, allocatsiya, aging, statement
- Production-ready deploy (Render, startup migrations, health check)

Loyiha kengaytirishga tayyor: service qatlami tenant-aware, migratsiyalar ketma-ket, integratsiya adapterlari alohida modulda.

---

*Ushbu hujjat 2026-06-10 da avtomatik tuzilgan. Yangilanishlar uchun `Hisobot.md` (ishlar jurnali) va `README.md` (texnik qo‘llanma) ga qarang.*

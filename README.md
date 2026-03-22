# erp-backend

Phase 1 foundation for a **multi-tenant ERP** API: shared PostgreSQL today, schema and services structured so **dedicated database per company** and **JWT-scoped tenant context** can be added without rewriting the domain layer.

- **Not in scope yet:** WMS integration (will be HTTP/API clients later), Docker.
- **In scope:** Companies (`tenant_mode`: `shared` | `dedicated`), roles, users, branches, warehouses, product master (`categories`, `units`, `products`), clients, **sales orders** (ERP lifecycle + fulfillment), **manual payments**, **invoices** (draft → issued → paid, line-item snapshot), **payment allocations**, **receivable aging** (bucketed by days past **due date**, or **invoice date** if `due_date` is null), **client statements** (chronological invoice vs payment lines + allocation audit notes) — tenant via JWT `company_id`. **Not yet:** bank feeds, GL journals.

## Stack

- FastAPI, Uvicorn  
- PostgreSQL, SQLAlchemy 2.x  
- Pydantic v2, pydantic-settings  
- Alembic migrations  
- passlib (bcrypt), python-jose (JWT helpers only for now)

## Quick start

```bash
# repozitoriya ildizidan
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env — set DATABASE_URL and a strong SECRET_KEY
```

### Database migrations

Create the database (e.g. `erp_db`), then:

```bash
# Optional: auto-generate future revisions after model changes (requires DB URL):
# alembic revision --autogenerate -m "describe change"

# Apply schema (through 0008: invoices + payment allocations):
alembic upgrade head
```

After pulling new modules: run `alembic upgrade head` (or rely on startup migrations on Render when enabled).

### Initial seed (first admin)

Set in `.env` (see `.env.example`):

- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- optional `ADMIN_FULL_NAME`

From repo root (DB reachable; migrations applied on app start or via `alembic upgrade head`):

```bash
python scripts/seed.py
```

Creates company **`core`**, role **`admin`**, and the admin user if missing. Idempotent.

### Auth flow (example)

1. `POST /auth/login` with the same email/password as in `ADMIN_*` → `access_token`  
2. `GET /auth/me` with header `Authorization: Bearer <token>` → user + role  
3. Use the same header for other protected routes.

**Admin-only:** `POST /companies`, `POST /users`, `POST /roles` require role code `admin`.

Shipped revisions: **`0001_initial_schema`** … **`0008_invoices_payment_allocations`**. Further changes: `alembic revision --autogenerate`.

**Accounts receivable (v1):** **`POST /invoices`** (manual lines + optional **`sales_order_id`**) or **`POST /invoices/from-sales-order/{id}`** (snapshot from confirmed-or-later order lines). Lifecycle: **`PATCH .../issue`** (sets **`outstanding_amount = total_amount`**), **`PATCH .../cancel`** (only if no allocations), **`PATCH .../deactivate`** (blocked if active allocations). **`POST /payment-allocations`** links an active **payment** to an **issued** invoice (same client); caps = payment **unallocated** amount and invoice **outstanding**. **`GET /payments/{id}/unallocated-amount`** for UI. Allocation rows are never hard-deleted; **`PATCH /payment-allocations/{id}/deactivate`** reverses balances via **`recalculate_invoice_balances`**. **Manual payments (order-level v1):** **`POST /payments`**, **`GET /payments/client-summary/{client_id}`**, **`GET /payments/sales-order-summary/{sales_order_id}`** — still order/payment based (not invoice AR aging).

**Bank automation / GL / aging reports** remain future layers.

**ERP → WMS outbound flow:** `confirmed` → **`POST /sales-orders/{id}/enqueue-wms`** (or **`PATCH .../send-to-wms`**) → `IntegrationJob` row (`pending`) + **`integration_status=pending`**. The **integration worker** (`python scripts/run_worker.py`) claims jobs with **`FOR UPDATE SKIP LOCKED`**, sets **`processing`**, calls the WMS adapter (`app/integration/wms/`), then **`finalize_worker_job_success`** (order → **`sent_to_wms`**, **`wms_order_id`**, **`sent_to_wms_at`**) or retries / **`failed`** after **`INTEGRATION_JOB_MAX_ATTEMPTS`**. Default **`WMS_MOCK_MODE=true`** (no HTTP). Set **`WMS_MOCK_MODE=false`**, **`WMS_BASE_URL`**, **`WMS_API_KEY`** when the vendor contract is ready (`HttpWmsClient` has **TODO** markers for path/response shape). Stale **`processing`** rows are reset to **`pending`** after **`INTEGRATION_JOB_STALE_PROCESSING_SECONDS`** (crash recovery). **Admin** **`PATCH /integration-jobs/{id}/mark-sent`** remains for manual testing. Inbound: **`POST /wms/callback/sales-orders/{id}`** (tenant JWT).

**Worker process:** same **`DATABASE_URL`** as the API. Cron: `*/2 * * * * cd /app && python scripts/run_worker.py`. Long-running: **`INTEGRATION_WORKER_LOOP_SECONDS=60`**. **Render:** add a **Background Worker** with start command **`python scripts/run_worker.py`**.

**Sales order lifecycle (summary):** unchanged after **`sent_to_wms`**. Header: **`integration_status`**, **`wms_order_id`**, **`last_sync_error`**. See **`app/workers/integration_worker.py`** and **`app/integration/wms/`**.

### Run the API

```bash
uvicorn app.main:app --reload
```

Or (Unix):

```bash
chmod +x start.sh
./start.sh
```

- **OpenAPI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- **Root:** `GET /` → `{"message": "Core ERP API is running"}`  
- **Health (load balancers):** `GET /health` → `{"status": "ok"}`  

On startup the app logs DB connectivity and runs `alembic upgrade head` when `RUN_MIGRATIONS_ON_STARTUP=true` (default).

## API overview (phase 1)

| Prefix        | Actions |
|---------------|---------|
| `/companies`  | `POST /`, `GET /` |
| `/roles`      | `POST /`, `GET /` (JWT tenant) |
| `/users`      | `POST /`, `GET /` (JWT tenant) |
| `/branches`   | `POST /`, `GET /` (JWT tenant) |
| `/warehouses` | `POST /`, `GET /` (JWT tenant) |
| `/categories` | CRUD + `PATCH .../deactivate` (JWT tenant) |
| `/units`       | CRUD + `PATCH .../deactivate` (JWT tenant) |
| `/products`    | CRUD + `PATCH .../deactivate`; optional `GET ?category_id=` filter |
| `/clients`     | CRUD + `PATCH .../deactivate`; optional `GET ?search=&is_active=` |
| `/sales-orders` | CRUD + filters (`integration_status`, …); **`POST .../enqueue-wms`**; lifecycle patches as before |
| `/integration-jobs` | `GET /`, `GET /{id}` (tenant); **`PATCH .../mark-sent`**, **`PATCH .../mark-failed`** (**admin** — worker simulation) |
| `/wms` | **`POST /callback/sales-orders/{id}`** — fulfillment payload (tenant JWT) |
| `/payments` | `POST /`, `GET /` (filters), `GET /{id}`, **`GET /{id}/unallocated-amount`**, `PATCH .../deactivate`; **`GET /client-summary/{client_id}`**, **`GET /sales-order-summary/{sales_order_id}`** |
| `/invoices` | `POST /`, **`POST /from-sales-order/{sales_order_id}`**, `GET /` (filters), `GET /{id}`, `PUT /{id}` (draft only), **`PATCH .../issue`**, **`PATCH .../cancel`**, **`PATCH .../deactivate`** |
| `/payment-allocations` | `POST /`, `GET /` (filters), `GET /{id}`, **`PATCH .../deactivate`** |
| `/receivables` | **`GET /aging`** (tenant-wide buckets), **`GET /aging/invoices`** (detail; optional `client_id`), **`GET /aging/client/{client_id}`** (optional `include_invoices`), **`GET /statements/client/{client_id}`** (`date_from` / `date_to` optional) |

**Aging:** Only **active** invoices with **`outstanding_amount > 0`**, excluding **draft** and **cancelled**. Buckets: **current** (not yet past due), **1–30**, **31–60**, **61–90**, **90+** days past due (calendar days from **`due_date`** or **`invoice_date`**). **`as_of_date`** defaults to today.

**Client statement:** Posting lines are **invoice_issued** (debit) and **payment_received** (credit on `payment_date`). **payment_allocated** rows are **non-posting** (0 debit/credit) audit lines describing applications. With **`date_from`**, **opening_balance** is activity before that date; without a start date, opening is **0** and all history through **`date_to`** (or open-ended) is listed.

Tenant scope comes from **`Authorization: Bearer`** (`company_id` in JWT). **Do not** send `company_id` in bodies for these resources.

## Layout

- `app/core` — settings, DB engine, `get_db`, security (hash + JWT scaffolding), shared exceptions  
- `app/models` — SQLAlchemy models (`company_id` on tenant tables; `Company.tenant_mode` for future routing)  
- `app/schemas` — Pydantic request/response DTOs  
- `app/services` — tenant-aware business logic (explicit `company_id` parameters)  
- `app/api/routes` — thin HTTP layer  
- `app/integration/wms` — WMS adapter (`MockWmsClient` / `HttpWmsClient`) + `send_sales_order_payload`  
- `app/workers` — background workers (`integration_worker` claims `IntegrationJob` rows)  

## Deploy on Render

Loyiha fayllari **repozitoriya ildizida** (`requirements.txt`, `app/`, `alembic/`). Render’da **Root Directory** ni **bo‘sh** qoldiring (yoki `.`).

### Variant A — `render.yaml` (Blueprint)

`render.yaml` ildizda. **New → Blueprint** yoki mavjud servisni yangilang. `DATABASE_URL` ni **Environment** da qo‘shing (Render PostgreSQL internal URL).

### Variant B — qo‘lda Web Service

1. **Root Directory:** bo‘sh  
2. **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`  
3. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (Render `$PORT` o‘zgaruvchisidan foydalanadi — qat’iy `10000` yozmang)  
4. **Environment:** `PYTHON_VERSION` = `3.12.8` yoki `runtime.txt`  
5. **DATABASE_URL**, **SECRET_KEY** — `.env.example` ga qarang.

**Migratsiya:** PostgreSQL ulangach, bir marta `alembic upgrade head` (shell yoki one-off).

## Future work (by design)

- **Dedicated DB:** resolve `Session`/engine from `Company.tenant_mode` + connection registry; keep service function signatures that accept `db` and `company_id`.  
- **JWT auth:** `decode_access_token` / login routes; replace `company_id` query params with dependencies.  
- **RBAC:** permission checks using `Role.code` and route metadata.  
- **WMS:** outbound integration clients only — no WMS schema here.  
- **More domains:** receivable aging / statements, bank reconciliation, GL postings, procurement — extend invoices / allocations without breaking `company_id` tenancy.

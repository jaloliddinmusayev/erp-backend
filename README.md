# erp-backend

Phase 1 foundation for a **multi-tenant ERP** API: shared PostgreSQL today, schema and services structured so **dedicated database per company** and **JWT-scoped tenant context** can be added without rewriting the domain layer.

- **Not in scope yet:** WMS integration (will be HTTP/API clients later), Docker.
- **In scope:** Companies (`tenant_mode`: `shared` | `dedicated`), roles, users, branches, warehouses, product master (`categories`, `units`, `products`), clients, **sales orders** (ERP lifecycle + fulfillment fields; **real WMS HTTP client** still out of scope) — tenant via JWT `company_id`.

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

# Apply schema (through 0005 sales order WMS prep: fulfillment columns, line qty rename):
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

Shipped revisions: **`0001_initial_schema`** … **`0005_sales_order_wms_fulfillment`**. Further changes: `alembic revision --autogenerate`.

**Sales order lifecycle (ERP):** `draft` → `PATCH .../confirm` → `confirmed` → `PATCH .../send-to-wms` → `sent_to_wms` (`is_sent_to_wms=true`) → `PATCH .../mark-in-progress` → `in_progress` → `PATCH .../update-fulfillment` (body: per-line `fulfilled_qty`) → when every line is fully picked, `PATCH .../complete` → `completed` (`fulfilled_at` set). **`PUT` only in `draft`.** After `sent_to_wms`, no structural edits. **`cancelled`** is terminal; **`completed`** cannot be cancelled. Header **`fulfillment_status`** is `pending` | `partial` | `fulfilled` (derived from lines). Line fields: **`ordered_qty`**, **`fulfilled_qty`**, response **`remaining_qty`** (computed). Real WMS calls: placeholder package **`app/integration/wms/`** (hook noted in service after `send_to_wms`).

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
| `/sales-orders` | CRUD-style: `POST /`, `GET /` (+ `status`, `fulfillment_status`, `client_id`, dates, `search`, `is_active`), `GET /{id}`, `PUT /{id}` (draft only); lifecycle: `PATCH .../confirm`, `send-to-wms`, `mark-in-progress`, `update-fulfillment`, `complete`, `cancel`, `deactivate` |

Tenant scope comes from **`Authorization: Bearer`** (`company_id` in JWT). **Do not** send `company_id` in bodies for these resources.

## Layout

- `app/core` — settings, DB engine, `get_db`, security (hash + JWT scaffolding), shared exceptions  
- `app/models` — SQLAlchemy models (`company_id` on tenant tables; `Company.tenant_mode` for future routing)  
- `app/schemas` — Pydantic request/response DTOs  
- `app/services` — tenant-aware business logic (explicit `company_id` parameters)  
- `app/api/routes` — thin HTTP layer  
- `app/integration` — future outbound adapters (e.g. WMS); no live integrations yet  

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
- **More domains:** invoicing, payments, procurement, finance — same pattern: model + schema + service + router, always `company_id` on tenant data.

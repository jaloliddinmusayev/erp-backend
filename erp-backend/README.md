# erp-backend

Phase 1 foundation for a **multi-tenant ERP** API: shared PostgreSQL today, schema and services structured so **dedicated database per company** and **JWT-scoped tenant context** can be added without rewriting the domain layer.

- **Not in scope yet:** WMS integration (will be HTTP/API clients later), Docker, full auth routes.
- **In scope:** Companies (`tenant_mode`: `shared` | `dedicated`), roles, users, branches, warehouses — all tenant-owned rows carry `company_id`.

## Stack

- FastAPI, Uvicorn  
- PostgreSQL, SQLAlchemy 2.x  
- Pydantic v2, pydantic-settings  
- Alembic migrations  
- passlib (bcrypt), python-jose (JWT helpers only for now)

## Quick start

```bash
cd erp-backend
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

# Apply schema (includes initial revision 0001):
alembic upgrade head
```

The repository ships with revision **`0001_initial_schema`**. Use `alembic revision --autogenerate` for **subsequent** changes once models evolve.

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
- **Root health:** `GET /` → `{"message": "Core ERP API is running"}`

## API overview (phase 1)

| Prefix        | Actions |
|---------------|---------|
| `/companies`  | `POST /`, `GET /` |
| `/roles`      | `POST /`, `GET /?company_id=` |
| `/users`      | `POST /`, `GET /?company_id=` |
| `/branches`   | `POST /`, `GET /?company_id=` |
| `/warehouses` | `POST /`, `GET /?company_id=` |

List endpoints take **`company_id` as a query parameter** until JWT + `current_user` supply tenant context.

## Layout

- `app/core` — settings, DB engine, `get_db`, security (hash + JWT scaffolding), shared exceptions  
- `app/models` — SQLAlchemy models (`company_id` on tenant tables; `Company.tenant_mode` for future routing)  
- `app/schemas` — Pydantic request/response DTOs  
- `app/services` — tenant-aware business logic (explicit `company_id` parameters)  
- `app/api/routes` — thin HTTP layer  

## Future work (by design)

- **Dedicated DB:** resolve `Session`/engine from `Company.tenant_mode` + connection registry; keep service function signatures that accept `db` and `company_id`.  
- **JWT auth:** `decode_access_token` / login routes; replace `company_id` query params with dependencies.  
- **RBAC:** permission checks using `Role.code` and route metadata.  
- **WMS:** outbound integration clients only — no WMS schema here.  
- **More domains:** clients, products, orders, procurement, finance — same pattern: model + schema + service + router, always `company_id` on tenant data.

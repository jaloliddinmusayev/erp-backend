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

*Yangi qatorlarni yuqoriga yoki shu jadvalga qo‘shing.*

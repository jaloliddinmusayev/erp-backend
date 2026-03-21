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

- FastAPI ilova: kompaniyalar, rollar, foydalanuvchilar, filiallar, ombxorlar.
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

- `POST /auth/login` — email + parol → `access_token` (JWT: `sub` = user id, `company_id`).
- `get_current_user` — `Authorization: Bearer`; noto‘g‘ri token **401**.
- Himoya: `companies`, `users`, `branches`, shuningdek `roles` va `warehouses` (tenant konteksti uchun).
- Ro‘yxat endpointlarida `company_id` query olib tashlandi; tenant `current_user.company_id` dan.
- Create body dagi `company_id` joriy foydalanuvchi tenantiga majburan moslashtiriladi.

---

## Keyingi qadamlar (eslatma)

- Birinchi kompaniya / admin foydalanuvchi: hozircha token talab qilinadi — seed yoki DB orqali boshlang‘ich yozuvlar.
- Alembic: yangi modellar uchun `revision --autogenerate`.
- Render: `DATABASE_URL`, `SECRET_KEY`, migratsiya (`alembic upgrade head`).

---

## O‘zgartirishlar jadvali

| Sana | Qisqa mazmun |
|------|----------------|
| 2026-03-21 | Fondatsiya, flatten repo, Render, GitHub sync, JWT auth |

*Yangi qatorlarni yuqoriga yoki shu jadvalga qo‘shing.*

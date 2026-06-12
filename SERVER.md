# Production server — deploy ma'lumotlari

**Oxirgi tekshiruv:** 2026-06-12  
**Server:** `vm57620` (root)

Bu fayl production serverda ERP backend ni yangilash va tekshirish uchun.

---

## URL lar

| Xizmat | URL |
|--------|-----|
| Backend API | https://api.triad.uz |
| Admin panel (Vercel) | https://erp-admin-five.vercel.app |
| Health | https://api.triad.uz/health |
| GitHub repo | https://github.com/jaloliddinmusayev/erp-backend |

---

## Server tuzilmasi

| Parametr | Qiymat |
|----------|--------|
| Loyiha papkasi | `/var/www/erp-backend` |
| Python venv | `/var/www/erp-backend/.venv` |
| systemd servis | `erp-backend.service` |
| Unit fayl | `/etc/systemd/system/erp-backend.service` |
| Ishga tushirish | `uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Reverse proxy | nginx 1.24 (Ubuntu) |
| Docker | yo'q |
| DB | PostgreSQL 16, `erp_db`, user `erp_user`, localhost |

---

## Tezkor deploy (kod yangilash)

SSH orqali serverga kiring, keyin:

```bash
cd /var/www/erp-backend
git pull origin main
sudo systemctl restart erp-backend
sudo systemctl status erp-backend --no-pager
```

Bitta qator:

```bash
cd /var/www/erp-backend && git pull origin main && sudo systemctl restart erp-backend && sudo systemctl status erp-backend --no-pager
```

**Eslatma:** `alembic` global emas — `.venv` ichida. Qo'lda migratsiya:

```bash
cd /var/www/erp-backend
git pull origin main
source .venv/bin/activate
alembic upgrade head
sudo systemctl restart erp-backend
```

Yoki venv aktivatsiyasiz:

```bash
cd /var/www/erp-backend && git pull origin main && .venv/bin/alembic upgrade head && sudo systemctl restart erp-backend
```

`RUN_MIGRATIONS_ON_STARTUP=true` (default) bo'lsa, `restart` o'zi `upgrade head` qiladi — lekin avval `git pull` shart (yangi `alembic/versions/*.py` serverda bo'lishi kerak).

---

## Tekshiruv buyruqlari

### Oxirgi commit

```bash
cd /var/www/erp-backend
git log -1 --oneline
```

### Health

```bash
curl -s https://api.triad.uz/health
# {"status":"ok"}
```

### CORS (login uchun)

```bash
curl -i -X OPTIONS "https://api.triad.uz/auth/login" \
  -H "Origin: https://www.triad.uz" \
  -H "Access-Control-Request-Method: POST"
```

Vercel uchun ham tekshiring:

```bash
curl -i -X OPTIONS "https://api.triad.uz/auth/login" \
  -H "Origin: https://erp-admin-five.vercel.app" \
  -H "Access-Control-Request-Method: POST"
```

Kutilgan headerlar:

```
access-control-allow-origin: https://erp-admin-five.vercel.app
access-control-allow-credentials: true
```

### Jarayon ishlayaptimi

```bash
ps aux | grep uvicorn
systemctl status erp-backend
```

---

## CORS sozlamalari (backend)

`.env` yoki default (`app/core/config.py`):

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://erp-admin-five.vercel.app,https://triad.uz,https://www.triad.uz
CORS_ALLOW_ORIGIN_REGEX=https://(www\.)?triad\.uz|https://.*\.vercel\.app
```

O'zgartirgandan keyin: `sudo systemctl restart erp-backend`

---

## Vercel (frontend)

Environment variable:

```
NEXT_PUBLIC_API_URL=https://api.triad.uz
```

O'zgartirgandan keyin Vercel da **Redeploy** qiling.

---

## systemd boshqaruvi

```bash
sudo systemctl start erp-backend
sudo systemctl stop erp-backend
sudo systemctl restart erp-backend
sudo systemctl status erp-backend
sudo journalctl -u erp-backend -f          # live log
sudo journalctl -u erp-backend -n 100      # oxirgi 100 qator
```

---

## Muammolarni bartaraf etish

### `sudo: unable to resolve host vm57620`

Ogohlantirish (ishga ta'sir qilmaydi). Tuzatish:

```bash
echo "127.0.0.1 vm57620" >> /etc/hosts
```

### `git pull` conflict

```bash
cd /var/www/erp-backend
git stash
git pull origin main
sudo systemctl restart erp-backend
```

### CORS hali ham ishlamasa

1. `git log -1` — CORS commit (`a844e1e` yoki undan yangi) bormi?
2. `systemctl restart erp-backend` qilinganmi?
3. nginx log: `sudo tail -f /var/log/nginx/error.log`

### Login ishlamasa (CORS emas)

1. `.env` dagi parol DB dagi parol bilan mos kelmasligi mumkin (seed boshqa parol bilan ishlagan).
2. Tekshirish: `grep ADMIN_ /var/www/erp-backend/.env`
3. Foydalanuvchi yo'q bo'lsa: `python scripts/seed.py`
4. Parolni `.env` ga mos qilish: `python scripts/reset_admin_password.py`

Default `.env.example` paroli (`change-me-strong-password`) production da **ishlamasligi** mumkin.

---

## Git

```bash
cd /var/www/erp-backend
git remote -v
# origin  https://github.com/jaloliddinmusayev/erp-backend.git
git branch
# main
```

---

## Tarix

| Sana | Hodisa |
|------|--------|
| 2026-06-12 | CORS fix deploy: `0f3bb2e` → `a844e1e`, OPTIONS tekshiruv OK |
| 2026-06-12 | Server ma'lumotlari aniqlash: `/var/www/erp-backend`, `erp-backend.service` |

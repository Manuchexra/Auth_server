# 🔐 Auth API — Autentifikatsiya Servisi

FastAPI asosida qurilgan to'liq autentifikatsiya mikro-servisi. JWT tokenlar, Redis kesh, PostgreSQL ma'lumotlar bazasi va Docker bilan ishlaydigan production-ready loyiha.

---

## ✨ Imkoniyatlar

| Funksiya | Tavsif |
|---|---|
| 📝 Ro'yxatdan o'tish | Email orqali hisob yaratish |
| 📧 Email tasdiqlash | Havolali tasdiqlash xati yuborish |
| 🔑 Tizimga kirish | Email + parol, JWT cookie |
| 🔄 Token yangilash | Refresh token orqali yangi access token |
| 👤 Profil ma'lumotlari | Tizimga kirgan foydalanuvchi ma'lumotlari |
| 🚪 Tizimdan chiqish | Tokenlarni o'chirish + cookie tozalash |

---

## 🛠️ Texnologiyalar

| Qatlam | Texnologiya |
|---|---|
| **Framework** | FastAPI (async) |
| **Ma'lumotlar bazasi** | PostgreSQL + SQLAlchemy 2.0 (async) |
| **Kesh / Token saqlash** | Redis |
| **Autentifikatsiya** | JWT (python-jose), Cookie-based |
| **Parol shifrlash** | Argon2 (passlib) |
| **Email** | FastAPI-Mail |
| **Konteyner** | Docker + Docker Compose |
| **Validatsiya** | Pydantic v2 |


---

## ⚙️ O'rnatish va ishga tushirish

### Docker orqali (tavsiya etiladi)

#### 1. Reponi klonlash

```bash
git clone https://github.com/Manuchexra/last_auth.git
cd last_auth/auth
```

#### 2. `.env` faylini sozlash

`.env` faylini to'ldiring:

```env
# App
DEBUG=True

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=auth_db
POSTGRES_PORT=5432

# Redis
REDIS_PORT=6379

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
EMAIL_USER=your_email@gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# pgAdmin
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin

PYTHONUNBUFFERED=1
```

#### 3. Docker Compose bilan ishga tushirish

```bash
docker compose up --build
```

Servislar ishlayotganda:

| Servis | Manzil |
|---|---|
| 🚀 FastAPI | http://localhost:8000 |
| 📖 Swagger UI | http://localhost:8000/docs |
| 🗄️ pgAdmin | http://localhost:5050 |

---

### Lokal muhitda ishga tushirish (Docker'siz)

```bash
# Virtual muhit
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# Kutubxonalar
pip install -r requirements.txt

# Serverni yoqish
uvicorn main:app --reload
```

> ⚠️ PostgreSQL va Redis mahalliy kompyuterda o'rnatilgan bo'lishi kerak.

---

## 🔗 API Endpointlari

Barcha endpoint'lar `/auth` prefiksi bilan boshlanadi.

| Method | URL | Tavsif | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | Yangi hisob yaratish | ✅ |
| `POST` | `/auth/login` | Tizimga kirish (cookie) | ✅ |
| `POST` | `/auth/logout` | Tizimdan chiqish | ✅ |
| `POST` | `/auth/refresh` | Access token yangilash | Cookie |
| `GET` | `/auth/me` | Joriy foydalanuvchi | ✅ |
| `GET` | `/auth/verify-email?token=...` | Email tasdiqlash | ✅ |
| `GET` | `/` | Server holati | ✅ |

---

## 🍪 Token arxitekturasi

```
Login qilganda:
  ├── access_token  → Cookie (httpOnly, 15 daqiqa)
  └── refresh_token → Cookie (httpOnly, /auth/refresh, 7 kun)
                             ↓
                        Redis da saqlanadi

Token muddati tugasa:
  POST /auth/refresh → yangi access_token olinadi
```

---

## 🐳 Docker servislari

`docker-compose.yml` da 4 ta servis mavjud:

| Servis | Image | Port |
|---|---|---|
| `backend` | Dockerfile (FastAPI) | 8000 |
| `db` | postgres:15-alpine | 5432 |
| `redis` | redis:7-alpine | 6379 |
| `pgadmin` | dpage/pgadmin4 | 5050 |

---


# 1-bosqich: Build (Kutubxonalarni yig'ish)
FROM python:3.12-slim AS builder


# Atrof-muhit o'zgaruvchilari
# → keraksiz .pyc fayllarni o‘chiradi
# → loglarni real-time chiqaradi  
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFERED=1       

WORKDIR /app

# Tizim bog'liqliklarini o'rnatish (Faqat build uchun keraklilari)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Venv yaratish va kutubxonalarni o'rnatish
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2-bosqich: Runtime (Asosiy imeyj)
FROM python:3.12-slim

# Atrof-muhit o'zgaruvchilarini sozlash
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app


# Faqat runtime uchun kerakli kutubxonalar (Postgres ulanishi va sog'liqni tekshirish uchun)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Builder bosqichidan faqat venvni ko'chirib o'tkazish
COPY --from=builder /opt/venv /opt/venv

# Xavfsizlik uchun root bo'lmagan foydalanuvchi yaratish
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser /app

USER appuser

# Loyiha fayllarini ko'chirish
COPY --chown=appuser:appuser . .

# Portni ochish
EXPOSE 8000

# Dasturni ishga tushirish
CMD ["sh", "-c", "cd auth && uvicorn main:app --host 0.0.0.0 --port 8000"]

# 7TREST Backend — Qurilish Kompaniyasi Ombor Boshqaruv Tizimi

Qurilish kompaniyalari uchun maxsus ishlab chiqilgan zamonaviy ombor va loyiha boshqaruv tizimining backend qismi.

## Texnologiyalar

| Texnologiya | Versiya | Vazifasi |
|-------------|---------|----------|
| Python | 3.12+ | Dasturlash tili |
| Django | 6.0.3 | Web framework |
| Django REST Framework | 3.17.1 | REST API |
| SimpleJWT | 5.5.1 | JWT autentifikatsiya |
| PostgreSQL / SQLite | 14+ | Ma'lumotlar bazasi |
| drf-spectacular | 0.29.0 | Swagger/OpenAPI hujjati |
| django-filter | 25.2 | Filtrlash |
| openpyxl | 3.1.5 | Excel eksport |
| reportlab | 4.4.10 | PDF generatsiya |
| python-telegram-bot | 22.7 | Telegram integratsiya |
| django-cors-headers | 4.9.0 | CORS himoyasi |
| Pillow | 12.2.0 | Rasm qayta ishlash |

## Loyiha Strukturasi

```
backend-7/
├── config/
│   ├── settings.py              # Asosiy sozlamalar
│   ├── urls.py                  # URL routing
│   └── wsgi.py                  # WSGI sozlama
├── core/
│   ├── permissions.py           # 4 ta rol uchun ruxsatlar (10+ klass)
│   ├── pagination.py            # Custom pagination (20/sahifa, max 100)
│   └── utils.py                 # Auto-number generator (BATCH/INV/ORD/TRF/EST)
├── apps/
│   ├── authentication/          # Login, logout, token refresh, parol tiklash
│   ├── users/                   # CustomUser model (phone-based auth) + CRUD
│   ├── warehouses/              # Ombor CRUD + mas'ul xodim biriktirish
│   ├── products/                # Category, Unit, Product modellari
│   ├── batches/                 # Batch + BatchMovement (inventar kuzatuvi)
│   ├── invoices/                # ShotInvoice + PDF/Excel eksport
│   ├── orders/                  # Order + OrderItem + StatusHistory
│   ├── suppliers/               # Yetkazib beruvchilar + statistika + qarz
│   ├── transfers/               # Omborlar arasi o'tkazmalar
│   ├── objects/                 # Qurilish obyektlari + materiallar + xarajatlar
│   ├── estimates/               # Smeta (byudjet rejasi va taqqoslash)
│   ├── payments/                # To'lovlar + qarz xulosasi
│   ├── reports/                 # Hisobotlar + Dashboard + Charts
│   ├── notifications/           # Bildirishnomalar (LOW/EMPTY stock alert)
│   └── telegram_bot/            # Telegram bot integratsiyasi
├── media/                       # Yuklangan fayllar (avatar, rasmlar)
├── requirements.txt             # Python paketlar ro'yxati
├── manage.py                    # Django CLI
└── .env                         # Muhit o'zgaruvchilari (git'ga kirmaydi)
```

## Ma'lumotlar Bazasi Modellari

```
CustomUser ─────────────── Warehouse
    │                          │
    │                   ┌──────┼──────────────┐
    │                   │      │              │
    │                 Batch   Order         Transfer
    │                   │      │              │
    │            ┌──────┤    OrderItem    TransferItem
    │            │      │      │
    │     BatchMovement │   OrderStatusHistory
    │            │      │
    │     ShotInvoice   │
    │            │      │
    │         Payment   │
    │            │      │
    │         Supplier  │
    │                   │
    │     ConstructionObject
    │            │
    │     ┌──────┤
    │     │      │
    │ ObjectMaterial  ObjectExpense
    │     │
    │  Estimate ── EstimateItem
    │
    ├── Notification
    └── TelegramUser

Product ── Category
    │
    └── Unit
```

### Model tafsilotlari

| Model | Maydonlar | Kalit xususiyatlar |
|-------|-----------|-------------------|
| **CustomUser** | phone (unique), email, role, warehouse, avatar | USERNAME_FIELD = phone, 4 ta rol |
| **Category** | name (unique), description | Metall, Qurilish, Elektr... |
| **Unit** | name (unique), abbreviation (unique) | kg, ta, m, l, t, m2... |
| **Warehouse** | name, address, capacity, responsible_user, is_active | Mas'ul xodim biriktirish |
| **Product** | name, category, unit, price, min_quantity, image | 23 ta qurilish mahsuloti |
| **Batch** | batch_number (auto), product, warehouse, quantity, status | BATCH-2026-0001, auto LOW/EMPTY |
| **BatchMovement** | batch, type (IN/OUT/ADJUSTMENT), quantity, balance | Har bir o'zgarish qayd etiladi |
| **ShotInvoice** | invoice_number (auto), batch, supplier, status | INV-2026-0001, PENDING/PAID/CANCELLED |
| **Order** | order_number (auto), type (IN/OUT), status | ORD-2026-0001, 5 ta holat |
| **OrderItem** | order, product, batch, quantity, price, total | Auto hisoblash |
| **Supplier** | name, inn, phone, rating (1-5), is_active | Yetkazib beruvchilar bazasi |
| **Transfer** | transfer_number (auto), from/to warehouse, driver, status | TRF-2026-0001, omborlar arasi |
| **TransferItem** | transfer, batch, product, quantity, received_quantity | Qabul qilish tasdiqlash |
| **ConstructionObject** | name, address, budget, status, responsible_user | PLANNING/ACTIVE/COMPLETED/SUSPENDED |
| **ObjectMaterial** | object, product, planned_quantity, used_quantity | Reja va haqiqiy taqqoslash |
| **ObjectExpense** | object, batch, quantity, total_amount | Xarajat kuzatuvi |
| **Estimate** | estimate_number (auto), object, status | EST-2026-0001, DRAFT/APPROVED/REJECTED |
| **EstimateItem** | estimate, product, quantity, price_per_unit, total | Smeta bandlari |
| **Payment** | invoice, supplier, amount, payment_method | CASH/BANK_TRANSFER/OTHER |
| **Notification** | type, title, message, is_read, data (JSON) | Auto stock alert |
| **TelegramUser** | user, telegram_chat_id, is_active | Bot bog'lanishi |

## Foydalanuvchi Rollari

| Funksiya | ADMIN | KATTA OMBOR | KICHIK OMBOR | HISOBCHI |
|----------|-------|-------------|--------------|---------|
| Foydalanuvchilar | CRUD | Ko'rish | — | — |
| Omborlar | CRUD | CRUD (o'chirish yo'q) | Faqat o'ziniki | Ko'rish |
| Mahsulotlar | CRUD | CRUD | Ko'rish | Ko'rish |
| Partiyalar | CRUD | CRUD | Faqat o'z ombori | Ko'rish |
| Buyurtmalar | CRUD + status | CRUD + status | Faqat o'z ombori | Ko'rish |
| Shot fakturalar | CRUD | CRUD | — | CRUD |
| Yetkazib beruvchilar | CRUD | CRUD | Ko'rish | Ko'rish |
| O'tkazmalar | CRUD | CRUD | Ko'rish | Ko'rish |
| Qurilish obyektlari | CRUD | CRUD | Ko'rish | Ko'rish |
| Smetalar | CRUD | Ko'rish | — | Ko'rish |
| To'lovlar | CRUD | CRUD | — | CRUD |
| Hisobotlar | Barchasi | Barchasi | Faqat o'z ombori | Barchasi |
| Telegram | CRUD | Bog'lanish | Bog'lanish | Bog'lanish |

## API Endpointlari

### Autentifikatsiya (`/api/auth/`)

| Metod | Endpoint | Tavsif |
|-------|----------|--------|
| POST | `/api/auth/login/` | Telefon + parol bilan kirish |
| POST | `/api/auth/token/refresh/` | Access token yangilash |
| POST | `/api/auth/logout/` | Tizimdan chiqish |
| GET | `/api/auth/me/` | Joriy foydalanuvchi |
| PUT | `/api/auth/change-password/` | Parol o'zgartirish |
| POST | `/api/auth/forgot-password/` | Parolni tiklash |

### CRUD Endpointlari

| Resurs | List/Create | Detail | Maxsus |
|--------|-------------|--------|--------|
| Users | `GET/POST /api/users/` | `GET/PUT/DELETE /api/users/{id}/` | `PUT /api/users/{id}/role/` |
| Categories | `GET/POST /api/categories/` | `GET/PUT/DELETE /api/categories/{id}/` | — |
| Units | `GET/POST /api/units/` | `GET/PUT/DELETE /api/units/{id}/` | — |
| Warehouses | `GET/POST /api/warehouses/` | `GET/PUT/DELETE /api/warehouses/{id}/` | — |
| Products | `GET/POST /api/products/` | `GET/PUT/DELETE /api/products/{id}/` | — |
| Batches | `GET/POST /api/batches/` | `GET/PUT/DELETE /api/batches/{id}/` | `GET .../movements/` |
| Movements | `GET/POST /api/movements/` | `GET /api/movements/{id}/` | — |
| Invoices | `GET/POST /api/invoices/` | `GET/PUT/DELETE /api/invoices/{id}/` | `GET .../pdf/`, `GET .../export/` |
| Orders | `GET/POST /api/orders/` | `GET/PUT/DELETE /api/orders/{id}/` | `PUT .../status/` |
| Suppliers | `GET/POST /api/suppliers/` | `GET/PUT/DELETE /api/suppliers/{id}/` | `GET .../invoices/`, `GET .../stats/` |
| Transfers | `GET/POST /api/transfers/` | `GET/DELETE /api/transfers/{id}/` | `PUT .../deliver/` |
| Objects | `GET/POST /api/objects/` | `GET/PUT/DELETE /api/objects/{id}/` | `GET/POST .../materials/`, `GET/POST .../expenses/`, `GET .../summary/` |
| Estimates | `GET/POST /api/estimates/` | `GET/PUT/DELETE /api/estimates/{id}/` | `PUT .../approve/`, `GET .../compare/` |
| Payments | `GET/POST /api/payments/` | `DELETE /api/payments/{id}/` | `GET /api/payments/debt-summary/` |
| Notifications | `GET /api/notifications/` | `GET /api/notifications/{id}/` | `PUT .../read/`, `PUT .../read-all/` |
| Telegram | — | — | `POST .../connect/`, `GET .../status/`, `DELETE .../disconnect/` |

### Hisobotlar va Dashboard

| Metod | Endpoint | Tavsif |
|-------|----------|--------|
| GET | `/api/dashboard/stats/` | Umumiy statistika |
| GET | `/api/reports/inventory/` | Inventar hisoboti |
| GET | `/api/reports/movements/` | Harakatlar hisoboti |
| GET | `/api/reports/low-stock/` | Kam qolgan mahsulotlar |
| GET | `/api/reports/warehouse-summary/` | Ombor xulosasi |
| GET | `/api/reports/export/excel/` | Excel eksport |
| GET | `/api/reports/export/pdf/` | PDF eksport |
| GET | `/api/reports/dashboard/charts/` | Dashboard grafiklari |
| GET | `/api/docs/` | Swagger API hujjati |

### Pagination formati

```json
{
  "count": 48,
  "total_pages": 3,
  "current_page": 1,
  "page_size": 20,
  "next": "http://.../api/batches/?page=2",
  "previous": null,
  "results": [...]
}
```

## Avtomatik Funksiyalar

### Auto-raqamlash

| Model | Format | Misol |
|-------|--------|-------|
| Batch | BATCH-{YIL}-{RAQAM} | BATCH-2026-0001 |
| Invoice | INV-{YIL}-{RAQAM} | INV-2026-0001 |
| Order | ORD-{YIL}-{RAQAM} | ORD-2026-0001 |
| Transfer | TRF-{YIL}-{RAQAM} | TRF-2026-0001 |
| Estimate | EST-{YIL}-{RAQAM} | EST-2026-0001 |

### Batch status avtomatik yangilanishi

```
quantity > min_quantity  -> NORMAL (yashil)
quantity <= min_quantity -> LOW (sariq) + notification + telegram alert
quantity <= 0           -> EMPTY (qizil) + notification + telegram alert
```

### Telegram bildirishnomalar

- Partiya LOW/EMPTY holatga o'tsa -> ADMIN va KATTA_OMBOR_ADMINI'larga xabar
- Yangi o'tkazma yaratilsa -> manzil ombor xodimlariga xabar
- Yangi buyurtma yaratilsa -> adminlarga xabar
- HTML formatlash va emoji bilan chiroyli xabarlar

### JWT Token boshqaruvi

- Access token: 12 soat
- Refresh token: 7 kun
- Avtomatik token rotation (yangilaganda yangi token)
- Token blacklisting (logout da)

## Xavfsizlik

| Chora | Holati |
|-------|--------|
| JWT autentifikatsiya | Ha |
| Rol asosidagi ruxsatlar | Ha (4 darajali, 10+ permission klass) |
| CORS himoyasi | Ha (localhost:3000, localhost:5173) |
| Parol hashing | Ha (Django default) |
| Token blacklisting | Ha |
| Token rotation | Ha |
| SQL injection himoyasi | Ha (Django ORM) |
| XSS himoyasi | Ha |
| CSRF himoyasi | Ha (JWT header) |

## Ishga Tushirish

### Talablar

- Python 3.12+
- PostgreSQL 14+ (ixtiyoriy, SQLite ham ishlaydi)

### O'rnatish

```bash
cd backend-7
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### .env faylni sozlash

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
# PostgreSQL uchun:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=7trest_db
# DB_USER=postgres
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=5432
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### Ma'lumotlar bazasi

```bash
python manage.py migrate
python manage.py create_admin     # Admin yaratish (+998901234567 / Admin1234!)
python manage.py seed_data        # Test ma'lumotlar (23 mahsulot, 48 partiya, 12 buyurtma...)
```

### Serverni ishga tushirish

```bash
python manage.py runserver 0.0.0.0:8000
```

### Kirish

- **Swagger API:** http://localhost:8000/api/docs/
- **Admin panel:** http://localhost:8000/admin/
- **Login:** `+998901234567` / `Admin1234!`

## Seed Data (Test Ma'lumotlari)

| Ma'lumot turi | Soni |
|--------------|------|
| O'lchov birliklari | 8 (kg, ta, l, m, m2, t, pkt, qut) |
| Kategoriyalar | 6 |
| Omborlar | 4 |
| Foydalanuvchilar | 6 |
| Mahsulotlar | 23 |
| Partiyalar | 48 |
| Shot fakturalar | 15 |
| Buyurtmalar | 12 |
| Yetkazib beruvchilar | 5 |
| O'tkazmalar | 5 |
| Qurilish obyektlari | 4 |
| Smetalar | 4 |
| To'lovlar | 10+ |
| Bildirishnomalar | 19 |

## Litsenziya

- **Loyiha:** 7TREST
- **Versiya:** 1.0.0
- **Brending:** Matrix1

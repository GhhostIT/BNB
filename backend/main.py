import os
import hmac
import hashlib
from urllib.parse import parse_qsl
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BOT_TOKEN = os.getenv("8948268391:AAFO-nS88Lzr-p_JreaGGFbKHYO8CEN8t6o", "")

app = FastAPI(title="Telegram Book Tracker AP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_telegram_data(init_data: str) -> bool:
    if not init_data:
        return True  # Для локального тестирования без Telegram
    if not BOT_TOKEN:
        return True  # Если токен не задан в энах, проникаем в режим отладки
    try:
        parsed_data = dict(parse_qsl(init_data))
        if "hash" not in parsed_data:
            return False
        received_hash = parsed_data.pop("hash")
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        return calculated_hash == received_hash
    except Exception:
        return False

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/books")
def get_books(x_init_data: str = Header(None)):
    if not verify_telegram_data(x_init_data):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Стартовый набор данных для демонстрации на полках
    return [
        {
            "id": 1,
            "title": "Чистый код",
            "author": "Роберт Мартин",
            "section": "home",
            "status": "reading",
            "badge": "Читаю",
            "badgeClass": "badge-reading",
            "icon": "💻"
        },
        {
            "id": 2,
            "title": "1984",
            "author": "Джордж Оруэлл",
            "section": "ebook",
            "status": "planned",
            "badge": "В планах",
            "badgeClass": "badge-planned",
            "icon": "👁"
        },
        {
            "id": 3,
            "title": "Дюна",
            "author": "Фрэнк Герберт",
            "section": "home",
            "status": "planned",
            "badge": "В планах",
            "badgeClass": "badge-planned",
            "icon": "⏳"
        },
        {
            "id": 4,
            "title": "Граф Монте-Кристо",
            "author": "Александр Дюма",
            "section": "library",
            "status": "library",
            "badge": "Сдать ч/з 3 дн",
            "badgeClass": "badge-library",
            "icon": "🏛"
        }
    ]

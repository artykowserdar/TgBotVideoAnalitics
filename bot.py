import os
import re

import psycopg2
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv  # добавляем
from groq import Groq

# Загружаем .env
load_dotenv()

# Конфигурация из окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

if not BOT_TOKEN or not GROQ_API_KEY:
    raise ValueError("BOT_TOKEN и GROQ_API_KEY нужны в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
client = Groq(api_key=GROQ_API_KEY)

# Тот же SYSTEM_PROMPT, что и раньше
SYSTEM_PROMPT = """
Ты эксперт по генерации ТОЛЬКО SQL-запросов для PostgreSQL на основе запроса пользователя на русском.
ВСЕГДА выводи ТОЛЬКО один чистый SQL-запрос, который возвращает ровно одно число.
НИЧЕГО БОЛЬШЕ НЕ ПИШИ: без объяснений, без markdown, без кавычек, без ```sql:disable-run
Начинай сразу с SELECT.

Схема базы:
- videos: id (uuid), creator_id (text), video_created_at (timestamptz), views_count (int финальные), likes_count (int), comments_count (int), reports_count (int)
- video_snapshots: video_id (uuid), created_at (timestamptz - время снапшота), delta_views_count (int - прирост просмотров за час), delta_likes_count и т.д.

Для дат используй date(created_at) = 'YYYY-MM-DD' или BETWEEN.
Преобразуй русские даты правильно, например "28 ноября 2025" → '2025-11-28'.

Примеры (точно следуй формату вывода):
Сколько всего видео есть в системе? → SELECT COUNT(*) FROM videos;
Сколько видео набрало больше 100 000 просмотров за всё время? → SELECT COUNT(*) FROM videos WHERE views_count > 100000;
На сколько просмотров в сумме выросли все видео 28 ноября 2025? → SELECT COALESCE(SUM(delta_views_count), 0) FROM video_snapshots WHERE date(created_at) = '2025-11-28';
Сколько разных видео получали новые просмотры 27 ноября 2025? → SELECT COUNT(DISTINCT video_id) FROM video_snapshots WHERE date(created_at) = '2025-11-27' AND delta_views_count > 0;
"""

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@dp.message_handler()
async def handle_query(message: types.Message):
    user_query = message.text.strip()
    if not user_query:
        await message.reply("Пустой запрос.")
        return

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # или "mixtral-8x7b-32768" — обе бесплатны и отлично генерируют SQL
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0.0,
            max_tokens=300
        )
        sql = response.choices[0].message.content.strip()

        # Новый код: очищаем от возможного мусора
        sql = sql.strip()
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        sql = sql.strip().rstrip(";") + ";"  # обеспечиваем завершение;
        if not sql.lower().startswith("select"):
            sql = "SELECT " + sql  # редкий fallback

        # Защита: убеждаемся, что это SELECT и нет опасных команд
        sql_lower = sql.lower()

        # Check if starts with SELECT (allow whitespace and comments)
        if not re.search(r'^\s*select\b', sql_lower):
            await message.reply("Некорректный SQL.")
            return

        # Check for dangerous keywords as whole words only
        dangerous_keywords = ["insert", "update", "delete", "drop", "create", "alter", "truncate", "execute"]
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', sql_lower) for keyword in dangerous_keywords):
            await message.reply("Некорректный SQL.")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchone()[0]
        cur.close()
        conn.close()

        await message.reply(str(result))

    except Exception as e:
        print(f"Error: {e}")  # логируем в консоль
        await message.reply("Произошла ошибка при обработке запроса.")

if __name__ == '__main__':
    print("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
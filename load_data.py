import json
import os

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv  # добавляем

# Загружаем .env
load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# Connect to PostgreSQL (use env vars in production)
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Load JSON
with open('videos.json', 'r') as f:  # Assume the file is named videos.json
    data = json.load(f)

# Prepare data for batch insert
videos_data = [
    (
        v['id'], v['creator_id'], v['video_created_at'], v['views_count'],
        v['likes_count'], v['comments_count'], v['reports_count'],
        v['created_at'], v['updated_at']
    ) for v in data['videos']
]

snapshots_data = []
for v in data['videos']:
    for s in v['snapshots']:
        snapshots_data.append(
            (
                s['id'], s['video_id'], s['views_count'], s['likes_count'],
                s['comments_count'], s['reports_count'], s['delta_views_count'],
                s['delta_likes_count'], s['delta_comments_count'], s['delta_reports_count'],
                s['created_at'], s['updated_at']
            )
        )

# Insert videos
if videos_data:
    execute_values(
        cur,
        """
        INSERT INTO videos (id, creator_id, video_created_at, views_count, likes_count, 
                            comments_count, reports_count, created_at, updated_at) 
        VALUES %s
        ON CONFLICT (id) DO NOTHING
        """,
        videos_data
    )

# Insert snapshots
if snapshots_data:
    execute_values(
        cur,
        """
        INSERT INTO video_snapshots (id, video_id, views_count, likes_count, comments_count, 
                                     reports_count, delta_views_count, delta_likes_count, 
                                     delta_comments_count, delta_reports_count, created_at, updated_at) 
        VALUES %s
        ON CONFLICT (id) DO NOTHING
        """,
        snapshots_data
    )

conn.commit()
cur.close()
conn.close()
print("Data loaded successfully.")

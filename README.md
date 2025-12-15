## Telegram Bot for Video Analytics

### Overview
This project implements a Telegram bot that answers natural language queries (in Russian) about video statistics by generating SQL queries via an LLM and executing them on a PostgreSQL database. The data is loaded from a provided JSON file into two tables: `videos` and `video_snapshots`.

Architecture:
- **Database**: PostgreSQL with two tables (see schema in create_tables.sql).
- **Data Loading**: A Python script parses the JSON and inserts data using psycopg2.
- **Bot**: Built with aiogram. On receiving a message, it sends the query to OpenAI (GPT-4o) with a system prompt describing the schema and examples. The LLM generates SQL, which is executed on the DB, and the result (a single number) is returned.
- **NLP Approach**: Few-shot prompting with schema description and examples to guide SQL generation. Dates are parsed by the LLM into ISO format. To prevent hallucinations, temperature is set to 0, and output is strictly SQL. If using xAI's Grok API instead, replace the OpenAI client with the xAI client (see https://x.ai/api for setup).

### Setup and Running Locally
1. **Prerequisites**:
   - Python 3.10+
   - PostgreSQL installed and running.
   - OpenAI API key (or xAI API key).
   - Telegram Bot Token (from @BotFather).

2. **Environment Variables**:
   - Create `.env` file:
   - BOT_TOKEN=your_telegram_bot_token 
   - OPENAI_API_KEY=your_openai_api_key 
   - DB_NAME=your_db_name 
   - DB_USER=your_db_user 
   - DB_PASSWORD=your_db_password 
   - DB_HOST=localhost 
   - DB_PORT=5432 
   - textLoad with `python-dotenv` if needed (add to requirements).

3. **Install Dependencies**:
   ```bash
    pip install -r requirements.txt

4. **Create Database Tables**:
   - Run `create_tables.sql` in your PostgreSQL DB:
      ```bash
     psql -U your_user -d your_db -f create_tables.sql

5. **Load Data**:
   - Download the JSON file (or use the provided one as videos.json).
   - Run:
      ```bash
      python load_data.py

6. **Run the Bot**:
   ```bash
   python bot.py

The bot will start polling and respond to messages.

### Docker (Optional)
- Dockerfile example:
   ```bash
    FROM python:3.12-slim
    WORKDIR /app
    COPY . .
    RUN pip install -r requirements.txt
    CMD ["python", "bot.py"]
    textBuild and run:
    docker build -t video-bot .
    docker run --env-file .env video-bot

textNote: PostgreSQL should be in a separate container or hosted.

### LLM Prompt Details
The system prompt includes:
- Schema description.
- Instructions to output only SQL.
- Date parsing from Russian to ISO.
- Examples for common queries to guide the model.

If switching to xAI Grok API:
- Install `groq` or similar client.
- Replace `client.chat.completions.create` with the equivalent call (model='grok-beta').
- For details on xAI API, visit https://x.ai/api.

### Testing
- Start the bot.
- Send example queries in Telegram.
- For production, deploy on a server (e.g., Heroku, VPS) to keep it running.
   
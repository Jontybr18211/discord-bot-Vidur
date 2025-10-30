import discord
import os
from dotenv import load_dotenv
import asyncio
import google.generativeai as genai
import asyncpg


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")


try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    exit()



async def init_db(pool):
    """Initializes the database and creates the messages table if it doesn't exist."""
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                channel_id BIGINT NOT NULL,
                author_id BIGINT,
                author_name TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    print("Database schema initialized.")

async def save_message(pool, channel_id, role, content, author_id=None, author_name=None):
    """Saves a message to the database."""
    try:
        async with pool.acquire() as conn:
            # Postgres uses $1, $2, etc. for placeholders, not ?
            await conn.execute("INSERT INTO messages (channel_id, author_id, author_name, role, content) VALUES ($1, $2, $3, $4, $5)",
                               (channel_id, author_id, author_name, role, content))
    except Exception as e:
        print(f"Failed to save message to DB: {e}")

async def get_history(pool, channel_id):
    """Retrieves the chat history for a channel, formatted for the Gemini API."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT role, content FROM (SELECT * FROM messages WHERE channel_id = $1 ORDER BY timestamp DESC LIMIT 20) AS sub ORDER BY timestamp ASC",
                                    (channel_id,))
            
            # Format for the genai.start_chat(history=...) method
            history = []
            for row in rows:
                history.append({"role": row['role'], "parts": [row['content']]})
            return history
    except Exception as e:
        print(f"Failed to get history from DB: {e}")
        return []

async def clear_history(pool, channel_id):
    """Deletes all messages for a specific channel."""
    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM messages WHERE channel_id = $1", (channel_id,))
    except Exception as e:
        print(f"Failed to clear history from DB: {e}")

async def send_message_in_chunks(channel, text, chunk_size=1990):
    """Splits a long message into chunks and sends them."""
    if len(text) <= chunk_size:
        await channel.send(text)
        return
    chunks = []
    current_chunk = ""
    for line in text.split('\n'):
        if len(current_chunk) + len(line) + 1 > chunk_size:
            chunks.append(current_chunk)
            current_chunk = ""
        if len(line) > chunk_size:
            for i in range(0, len(line), chunk_size):
                chunks.append(line[i:i + chunk_size])
        else:
            current_chunk += line + "\n"
    if current_chunk:
        chunks.append(current_chunk)
    for chunk in chunks:
        if chunk.strip():
            await channel.send(chunk)
            await asyncio.sleep(0.5)


class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None
        self.pool = None
        
        try:
            self.model = genai.GenerativeModel("gemini-2.5-pro")
            print("Gemini 2.5 Pro Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
        
    async def on_ready(self):
        print(f"Bot logged in as {self.user}")
        if self.model is None:
            print("WARNING: Bot is running but Model failed to load.")
        
        try:
            if DATABASE_URL:
                self.pool = await asyncpg.create_pool(DATABASE_URL)
                if self.pool:
                    print("Database connection pool created.")
                    await init_db(self.pool)
            else:
                print("DATABASE_URL not set. Database features will be disabled.")
        except Exception as e:
            print(f"Failed to connect to database: {e}")

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if self.model is None:
            await message.channel.send("Sorry, I'm not feeling well (model failed to load).")
            return
        
        # Check if the database is connected
        if self.pool is None:
            await message.channel.send("Sorry, I can't remember anything (database is not connected).")
            return

        # !reset ---
        if message.content == "!reset":
            channel_id = message.channel.id
            # All DB calls now use 'await' and pass 'self.pool'
            await clear_history(self.pool, channel_id)
            await message.channel.send("🤖 My memory for this channel has been cleared from the database.")
            return

        
        if message.content.startswith("!ask "):
            query = message.content[5:]
            channel_id = message.channel.id

            try:
                history = await get_history(self.pool, channel_id)
                chat = self.model.start_chat(history=history)
                async with message.channel.typing():
                    response = await chat.send_message_async(query)
                    
                    if response.text:
                        await save_message(self.pool, channel_id, "user", query,
                                           author_id=message.author.id,
                                           author_name=message.author.name)
                        
                        await save_message(self.pool, channel_id, "model", response.text,
                                           author_id=self.user.id,
                                           author_name=self.user.name)
                        await send_message_in_chunks(message.channel, response.text)
                    else:
                        await message.channel.send("I couldn't generate a response for that.")

            except Exception as e:
                print(f"Error during content generation: {e}")
                await message.channel.send(f"An error occurred: {e}")


intents = discord.Intents.default()
intents.message_content = True

client = MyBot(intents=intents)
client.run(DISCORD_TOKEN)
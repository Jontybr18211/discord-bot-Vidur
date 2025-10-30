import discord
import os
from dotenv import load_dotenv
import asyncio
import google.generativeai as genai
import sqlite3

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
      genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
      print(f"Error configuring Gemini: {e}")
      exit()


def init_db():
      """Initializes the database and creates the messages table if it doesn't exist."""
      conn = sqlite3.connect('chat_history.db')
      c = conn.cursor()
      c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  channel_id INTEGER NOT NULL,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
      ''')
      conn.commit()
      conn.close()

def save_message(channel_id, role, content):
      """Saves a message to the database."""
      try:
            conn = sqlite3.connect('chat_history.db')
            c = conn.cursor()
            c.execute("INSERT INTO messages (channel_id, role, content) VALUES (?, ?, ?)",
                        (channel_id, role, content))
            conn.commit()
            conn.close()
      except Exception as e:
            print(f"Failed to save message to DB: {e}")

def get_history(channel_id):
      """Retrieves the chat history for a channel, formatted for the Gemini API."""
      try:
            conn = sqlite3.connect('chat_history.db')
            c = conn.cursor()
            # Get the last 20 messages to keep the context window reasonable
            c.execute("SELECT role, content FROM (SELECT * FROM messages WHERE channel_id = ? ORDER BY timestamp DESC LIMIT 20) ORDER BY timestamp ASC",
                        (channel_id,))
            rows = c.fetchall()
            conn.close()
            
            # Format for the genai.start_chat(history=...) method
            history = []
            for row in rows:
                  history.append({"role": row[0], "parts": [row[1]]})
            return history
      except Exception as e:
            print(f"Failed to get history from DB: {e}")
            return []

def clear_history(channel_id):
      """Deletes all messages for a specific channel."""
      try:
            conn = sqlite3.connect('chat_history.db')
            c = conn.cursor()
            c.execute("DELETE FROM messages WHERE channel_id = ?", (channel_id,))
            conn.commit()
            conn.close()
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
        try:
            self.model = genai.GenerativeModel("gemini-2.5-pro") 
            print("Gemini 2.5 Pro Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
        
        
        init_db()
        print("Database initialized.")

    async def on_ready(self):
        print(f"Bot logged in as {self.user}")
        if self.model is None:
            print("WARNING: Bot is running but Model failed to load.")

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if self.model is None:
            await message.channel.send("Sorry, I'm not feeling well (model failed to load).")
            return

        # !reset ---
        if message.content == "!reset":
            channel_id = message.channel.id
            clear_history(channel_id)
            await message.channel.send("🤖 My memory for this channel has been cleared from the database.")
            return

        
        if message.content.startswith("!ask "):
            query = message.content[5:]
            channel_id = message.channel.id

            try:
                # 1. Get this channel's history from the database
                history = get_history(channel_id)
                
                # 2. Start a new chat session *with* that history
                chat = self.model.start_chat(history=history)

                # 3. Send the new message to the chat
                async with message.channel.typing():
                    response = await chat.send_message_async(query)
                    
                    if response.text:
                        # 4. Save the new messages to the database
                        save_message(channel_id, "user", query)
                        save_message(channel_id, "model", response.text)
                        
                        # 5. Send the response to Discord
                        await send_message_in_chunks(message.channel, response.text)
                    else:
                        await message.channel.send("I couldn't generate a response for that.")

            except Exception as e:
                # This is the essential try/except
                print(f"Error during content generation: {e}")
                await message.channel.send(f"An error occurred: {e}")

intents = discord.Intents.default()
intents.message_content = True

client = MyBot(intents=intents)
client.run(DISCORD_TOKEN)
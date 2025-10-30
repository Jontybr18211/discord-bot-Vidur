# for test purpose
import discord
import os
from dotenv import load_dotenv
import asyncio
import google.generativeai as genai

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    exit()

# --- NEW FUNCTION ---
async def send_message_in_chunks(channel, text, chunk_size=1990):
    """Splits a long message into chunks and sends them."""
    if len(text) <= chunk_size:
        await channel.send(text)
        return

    # Split the message into chunks
    chunks = []
    current_chunk = ""
    for line in text.split('\n'):
        if len(current_chunk) + len(line) + 1 > chunk_size:
            chunks.append(current_chunk)
            current_chunk = ""
        
        # If a single line is too long, split it hard
        if len(line) > chunk_size:
            for i in range(0, len(line), chunk_size):
                chunks.append(line[i:i + chunk_size])
        else:
            current_chunk += line + "\n"

    if current_chunk:
        chunks.append(current_chunk)

    # Send each chunk
    for chunk in chunks:
        if chunk.strip():  # Avoid sending empty messages
            await channel.send(chunk)
            await asyncio.sleep(0.5) # Small delay to avoid rate limiting


class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # Let's use gemini-1.5-flash. It's fast and perfect for a bot.
            self.model = genai.GenerativeModel("gemini-1.5-flash") 
            print("Gemini Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

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

        if message.content.startswith("!ask "):
            query = message.content[5:]

            try:
                async with message.channel.typing():
                    response = await self.model.generate_content_async(query)
                    
                    if response.text:
                        # --- MODIFIED SECTION ---
                        # Instead of sending directly...
                        # await message.channel.send(response.text) 
                        
                        # ...use the new function to send it in chunks.
                        await send_message_in_chunks(message.channel, response.text)
                        # --- END MODIFIED SECTION ---
                    else:
                        await message.channel.send("I couldn't generate a response for that.")

            except Exception as e:
                print(f"Error during content generation: {e}")
                await message.channel.send(f"An error occurred: {e}")

# --- Set up Intents and Run ---
intents = discord.Intents.default()
intents.message_content = True

client = MyBot(intents=intents)
client.run(DISCORD_TOKEN)
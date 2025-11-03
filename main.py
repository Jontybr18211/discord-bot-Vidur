import discord
import os
import asyncio
import google.generativeai as genai


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

async def send_message_in_chunks(channel, text, chunk_size=1990):
    if len(text) <= chunk_size:
        await channel.send(text)
        return

    chunks = []
    current = ""

    for line in text.split("\n"):
        if len(current) + len(line) + 1 > chunk_size:
            chunks.append(current)
            current = ""

        if len(line) > chunk_size:
            for i in range(0, len(line), chunk_size):
                chunks.append(line[i:i + chunk_size])
        else:
            current += line + "\n"

    if current:
        chunks.append(current)

    for chunk in chunks:
        await channel.send(chunk)
        await asyncio.sleep(0.4)  # Prevent Discord spam limit


class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        print("✅ Gemini model loaded successfully.")

    async def on_ready(self):
        print(f"🤖 Bot logged in as {self.user}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("!ask "):
            query = message.content[5:]

            try:
                async with message.channel.typing():
                    response = await self.model.generate_content_async(query)

                    if response.text:
                        await send_message_in_chunks(message.channel, response.text)

                    else:
                        await message.channel.send("❓ Gemini returned no output.")

            except Exception as e:
                print(f"Gemini error: {e}")
                await message.channel.send("⚠️ Error generating response.")


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

client = MyBot(intents=intents)
client.run(DISCORD_TOKEN)

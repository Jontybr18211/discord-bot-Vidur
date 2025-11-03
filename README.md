

-----



# Vidur Bot: Your Personal AI Assistant for Discord

**A smart, responsive Discord bot powered by Google's latest Gemini AI, ready to answer your questions and chat 24/7.**

<p align="center">
  <img src="./vidur-bot-header.png" alt="Vidur Bot Header" width="400"/>
</p>

-----

## 🤖 About Vidur

Vidur is a powerful, yet simple-to-use Discord bot that integrates directly with Google's most advanced AI. It's built to be a fast, knowledgeable, and helpful companion in your server.

Whether you need to brainstorm ideas, ask a complex question, get help with a problem, or just have a fun chat, Vidur is always online and ready to help.

## ✨ Features

  * **Powered by Gemini 2.5 Pro:** Get high-quality, articulate, and accurate responses from Google's cutting-edge AI model. (Upgraded from an earlier version for enhanced performance).
  * **Always Online:** Hosted on Railway, Vidur runs 24/7 as a background worker, ensuring it's always available when you need it.
  * **Chunked Responses:** Long answers are automatically split into easy-to-read messages to bypass Discord's character limit.
  * **Simple to Use:** No complex setup. Just add it to your server and start chatting with the `!ask` command.

-----

## 🚀 Add Vidur to Your Server

Want to try Vidur right now? It's easy\!

Click the link below to invite Vidur to your Discord server. You'll just need to select your server and approve the necessary permissions (like "Send Messages" and "Read Message History").

[![Add to Discord](https://img.shields.io/badge/Add%20to-Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1433309753555157156&permissions=3941734153713728&integration_type=0&scope=bot)

-----

## 💡 How to Use

Using Vidur is as simple as sending a message.

  * **Main Command:** `!ask <your-question>`

Simply type `!ask` followed by any prompt or question you have.

**Example:**
`!ask What are the main differences between Python and JavaScript?`

Vidur will show a "typing..." status while it generates the response and then send the answer in the channel.

-----

## 🛠️ How to Build Your Own Bot

Want to build and host your own version of Vidur? Here is a complete guide from start to finish.

### Prerequisites

  * A [GitHub](https://github.com/) account.
  * A [Discord](https://discord.com/) account with a server you own.
  * A [Google AI Studio](https://aistudio.google.com/) account (for the Gemini API key).
  * A [Railway.app](https://railway.app/) account.

-----

### Step 1: Create the Discord Bot Application

1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications) and log in.
2.  Click the **"New Application"** button and give your bot a name.
3.  Go to the **"Bot"** tab in the left-hand menu.
4.  Under "Privileged Gateway Intents," enable the **"MESSAGE CONTENT INTENT"**. This is required for the bot to read your `!ask` commands.
5.  Click the **"Reset Token"** button to reveal your bot's token. **Copy this token and save it somewhere secure.** This is your `DISCORD_TOKEN`.

-----

### Step 2: Get Your API Keys

1.  **Discord Token:** You already have this from Step 1.
2.  **Gemini API Key:**
      * Go to [Google AI Studio](https://aistudio.google.com/).
      * Click **"Get API key"** and create a new API key in a new or existing project.
      * **Copy this API key and save it.** This is your `GEMINI_API_KEY`.
      * Make sure the Google Cloud project for this key has the **"Vertex AI Generative AI API"** enabled and **Billing** set up.

-----

### Step 3: Code Your Bot (Python)

You will need the `discord.py` and `google-generativeai` Python libraries.

1.  **Create Your Files:**

      * `main.py` (This will be your main bot code)
      * `requirements.txt` (This tells Railway what packages to install)

2.  **`requirements.txt` file:**

      * Add the names of the libraries your project needs, such as `discord.py` and `google-generativeai`.

3.  **`main.py` file:**

      * Your script will need to import the libraries and get the API keys from the environment variables.
      * It should configure the Gemini model (e.g., `genai.GenerativeModel("gemini-2.5-pro")`).
      * You'll need to set up the bot's `on_message` event to listen for the `!ask` command.
      * Finally, you'll run the client using the `DISCORD_TOKEN`.

4.  **Push to GitHub:** Create a new GitHub repository and push your `main.py` and `requirements.txt` files to it.

-----

### Step 4: Host on Railway

1.  **Create a New Project:**

      * Log in to [Railway.app](https://railway.app/).
      * From your dashboard, click **"New Project"** and select **"Deploy from GitHub repo"**.
      * Select your bot's GitHub repository.

2.  **Set Environment Variables:**

      * After the project is created, click on your new service.
      * Go to the **"Variables"** tab.
      * Add your two secret keys:
          * `DISCORD_TOKEN` = (The token you got from Discord)
          * `GEMINI_API_KEY` = (The key you got from Google AI Studio)
      * You do **not** need a `.env` file for Railway. It injects these variables automatically.

3.  **Configure as a Worker (Important\!):**

      * A Discord bot is a background service, not a web page. You must tell Railway to run it as a "worker" so it stays online 24/7.
      * Go to the **"Settings"** tab for your service.
      * Scroll down to the **"Networking"** section.
      * Find the **"Healthcheck Path"** field. **Delete any text** in this field (like `/`) and leave it **completely blank**.
      * This tells Railway *not* to expect a web response, and it will run your script as a persistent service.

4.  **Set a Start Command:**

      * In the **"Settings"** tab, find the **"Deploy"** section.
      * In the **"Custom Start Command"** field, tell Railway how to run your script (e.g., `python main.py`).

5.  **Deploy:**

      * Go to the **"Deployments"** tab. Your project may have already deployed.
      * If you had to make changes (like adding variables), a new deployment will trigger.
      * Watch the **"Deploy Logs"**. You should see messages from your script indicating the bot has successfully logged in.

Your bot is now online, hosted on Railway\!

## 💻 Tech Stack

  * **Language:** [Python](https://www.python.org/)
  * **Discord API:** [discord.py](https://discordpy.readthedocs.io/en/stable/)
  * **AI Model:** [Google Gemini 2.5 Pro](https://deepmind.google/technologies/gemini/)
  * **Hosting:** [Railway.app](https://railway.app/)

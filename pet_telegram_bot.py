from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import json, os

# File to store pet states
STATE_FILE = "pets.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# Initialize state
pets = load_state()
def get_pet(user_id):
    if user_id not in pets:
        pets[user_id] = {"hunger": 50, "happiness": 50, "energy": 50, "pet": "🐶"}
    return pets[user_id]

main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🍖 Feed"), KeyboardButton("🎾 Play")],
        [KeyboardButton("😴 Sleep"), KeyboardButton("📊 Status")]
    ],
    resize_keyboard=True
)

GIFS = {
    "feed": "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDF3c21nZXQ2MjQydzZrNWJtbGMyb3pqbHJxbXppcXY3NjJmc2k0cCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jp2KXzsPtoKFG/giphy.gif",
    "play": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExdG5od3kzZGlpZ2p2YjU1bHN0d3dwNmdtdGtiaDkxNTN2OGY4aW9qaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZFFVNwIbjsKtP3lHYK/giphy.gif",
    "tired": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExamJ3NDFzazY0bHUxZTQzMWVqcXB6MmI3cmZ3cmt5ZnlnODN0eDJuMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/8m1PiTyqxmsmOsIQNp/giphy.gif",
    "status": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjB4ZTJqeHptbnZncmx0YTIxN25kM2F3bzMyMGM0M3d2enh3ZmQ0OCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/gKHGnB1ml0moQdjhEJ/giphy.gif",
    "hungry": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGs4c3Nsdmdlbzg0ZjJqY3N0dTZ0Z2FoYTM2MmhwMDRqOGQ3c3JxbCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/vifKOydHeZ8MqMoZlM/giphy.gif",
    "sleep": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTZnOHI1bHA5NWFhaWd6eXJzNDd2NXl0bWNtMTI4ajcwaDZidWgycyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/rGznn87ld7o7S/giphy.gif"
}

# def action_keyboard():
#     keyboard = [
#         [InlineKeyboardButton("🍖 Feed", callback_data="feed"),
#          InlineKeyboardButton("🎾 Play", callback_data="play")],
#         [InlineKeyboardButton("😴 Sleep", callback_data="sleep"),
#          InlineKeyboardButton("📊 Status", callback_data="status")]
#     ]
#     return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    get_pet(user_id)  # ensure pet exists
    await update.message.reply_text(
        "🐶 Your pet is waiting! Choose an action:",
        reply_markup=main_keyboard
    )

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str):
    pet = get_pet(user_id)
    if pet["energy"] == 0:  # if no energy left, auto-sleep
        await auto_sleep(update, user_id)
    else:
        pet["hunger"] = min(100, pet["hunger"] + 20)
        pet["energy"] = max(0, pet["energy"] - 30)
        await update.message.reply_animation(GIFS["feed"], caption="🍖 You fed your pet! Hunger +20")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str):
    pet = get_pet(user_id)
    if pet["energy"] == 0:  # if no energy left, auto-sleep
        await auto_sleep(update, user_id)
    elif pet["hunger"] == 0:  # if no energy left, auto-sleep
        await auto_feed(update, user_id)
    else:
        pet["happiness"] = min(100, pet["happiness"] + 15)
        pet["energy"] = max(0, pet["energy"] - 50)
        pet["hunger"] = max(0, pet["hunger"] - 30)
        await update.message.reply_animation(GIFS["play"], caption="🎾 You played with your pet! Happiness +15")


async def sleep(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str):
    pet = get_pet(user_id)
    pet["energy"] = min(100, pet["energy"] + 75)
    pet["happiness"] = max(0, pet["happiness"] - 50)
    pet["hunger"] = max(0, pet["hunger"] - 50)
    await update.message.reply_animation(GIFS["sleep"], caption="😴 Your pet is sleeping. Energy +75")

# --- Auto sleep when energy hits 0 ---
async def auto_sleep(update: Update, user_id: str):
    await update.message.reply_animation(GIFS["tired"], caption="💤 Your pet got too tired, you have to let it sleep first!")

# --- Auto eat when hunger hits 0 ---
async def auto_feed(update: Update, user_id: str):
    await update.message.reply_animation(GIFS["hungry"], caption="💤 Your pet got too hungry, you have to feed it first!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str):
    pet = get_pet(user_id)
    await update.message.reply_animation(
        GIFS["status"],
        caption=(f"{pet['pet']} Pet Status:\n"
                 f"🍖 Hunger: {pet['hunger']}\n"
                 f"🎉 Happiness: {pet['happiness']}\n"
                 f"⚡ Energy: {pet['energy']}")
    )

# async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     user_id = str(query.from_user.id)
    
#     if query.data == "feed":
#         text = await feed(update, context, user_id)
#     elif query.data == "play":
#         text = await play(update, context, user_id)
#     elif query.data == "sleep":
#         text = await sleep(update, context, user_id)
#     elif query.data == "status":
#         text = await status(update, context, user_id)
#     else:
#         text = "❓ Unknown action"

#     await query.answer()
#     await query.message.reply_text(text=text, reply_markup=action_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if text == "🍖 Feed":
        await feed(update, context, user_id)
    elif text == "🎾 Play":
        await play(update, context, user_id)
    elif text == "😴 Sleep":
        await sleep(update, context, user_id)
    elif text == "📊 Status":
        await status(update, context, user_id)
    else: 
        await update.message.reply_text("❓ Unknown action", reply_markup=main_keyboard)



def main():
    app = Application.builder().token("7330811920:AAE_6v4hs3pOSKND_TXLiiZtrBDv4PSngq0").build()

    app.add_handler(CommandHandler("start", start))
    # app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    #app.add_handler(CommandHandler("feed", feed))
    #app.add_handler(CommandHandler("play", play))
    #app.add_handler(CommandHandler("sleep", sleep))
    #app.add_handler(CommandHandler("status", status))
    
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

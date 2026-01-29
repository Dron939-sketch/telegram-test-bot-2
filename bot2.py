import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from archetypes import ARCHETYPES  # ← Импортируем описания

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = os.getenv("TOKEN_BOT2")

# Хранилище данных пользователей
user_data = {}

# ========== КОНСТАНТЫ ==========

SUITS = {
    "♠️": "Социальная (Сила)",
    "♥️": "Телесная",
    "♣️": "Познавательная",
    "♦️": "Эмоциональная"
}

RANKS = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]

QUESTIONS = {
    "♠️": [
        "1️⃣ Кто-то использует вас в своих целях?",
        "2️⃣ Вы чувствуете себя слабым в отношениях с людьми?",
        "3️⃣ Вы боитесь конфликтов и избегаете их?",
        "4️⃣ Вы часто подчиняетесь чужой воле?",
        "5️⃣ Вы терпите унижения ради сохранения отношений?",
        "6️⃣ Вы боитесь власти и авторитетов?",
        "7️⃣ Вы чувствуете, что не можете защитить себя?",
        "8️⃣ Вы избегаете ответственности за свою жизнь?",
        "9️⃣ Вы ждёте, что кто-то решит ваши проблемы?"
    ],
    "♥️": [
        "1️⃣ Вы игнорируете сигналы своего тела?",
        "2️⃣ Вы терпите боль и дискомфорт?",
        "3️⃣ Вы боитесь болезней?",
        "4️⃣ Вы не доверяете своему телу?",
        "5️⃣ Вы чувствуете, что тело вас подводит?",
        "6️⃣ Вы стыдитесь своего тела?",
        "7️⃣ Вы не чувствуете удовольствия от жизни?",
        "8️⃣ Вы живёте только в голове, забывая о теле?",
        "9️⃣ Вы боитесь старости и смерти?"
    ],
    "♣️": [
        "1️⃣ Вы боитесь выглядеть глупым?",
        "2️⃣ Вы избегаете новых знаний?",
        "3️⃣ Вы чувствуете, что не понимаете мир?",
        "4️⃣ Вы боитесь ошибиться?",
        "5️⃣ Вы не доверяете своему мнению?",
        "6️⃣ Вы постоянно сомневаетесь в своих решениях?",
        "7️⃣ Вы боитесь критики?",
        "8️⃣ Вы чувствуете, что вас обманывают?",
        "9️⃣ Вы не можете отличить правду от лжи?"
    ],
    "♦️": [
        "1️⃣ Вы чувствуете, что вас не любят?",
        "2️⃣ Вы боитесь одиночества?",
        "3️⃣ Вы зависите от чужого мнения?",
        "4️⃣ Вы не можете сказать 'нет'?",
        "5️⃣ Вы жертвуете собой ради других?",
        "6️⃣ Вы боитесь быть отвергнутым?",
        "7️⃣ Вы не чувствуете любви к себе?",
        "8️⃣ Вы боитесь близости?",
        "9️⃣ Вы не можете выразить свои чувства?"
    ]
}

# ========== КОМАНДЫ ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id
    user_data[user_id] = {"step": "choose_suit"}
    
    keyboard = [
        [InlineKeyboardButton("♠️ Социальная (Сила)", callback_data="suit_♠️")],
        [InlineKeyboardButton("♥️ Телесная", callback_data="suit_♥️")],
        [InlineKeyboardButton("♣️ Познавательная", callback_data="suit_♣️")],
        [InlineKeyboardButton("♦️ Эмоциональная", callback_data="suit_♦️")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎴 **Добро пожаловать в Архетипическую диагностику!**\n\n"
        "Выберите сферу жизни для диагностики:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # Выбор масти
    if data.startswith("suit_"):
        suit = data.split("_")[1]
        user_data[user_id] = {
            "suit": suit,
            "step": "questions",
            "answers": [],
            "question_index": 0
        }
        await ask_question(query, user_id)
    
    # Ответы на вопросы
    elif data.startswith("answer_"):
        answer = data.split("_")[1]
        user_data[user_id]["answers"].append(answer)
        user_data[user_id]["question_index"] += 1
        
        if user_data[user_id]["question_index"] < 9:
            await ask_question(query, user_id)
        else:
            await show_result(query, user_id)
    
    # Новая диагностика
    elif data == "new_test":
        user_data[user_id] = {"step": "choose_suit"}
        keyboard = [
            [InlineKeyboardButton("♠️ Социальная (Сила)", callback_data="suit_♠️")],
            [InlineKeyboardButton("♥️ Телесная", callback_data="suit_♥️")],
            [InlineKeyboardButton("♣️ Познавательная", callback_data="suit_♣️")],
            [InlineKeyboardButton("♦️ Эмоциональная", callback_data="suit_♦️")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎴 Выберите сферу для новой диагностики:",
            reply_markup=reply_markup
        )

async def ask_question(query, user_id):
    """Задать вопрос"""
    suit = user_data[user_id]["suit"]
    index = user_data[user_id]["question_index"]
    question = QUESTIONS[suit][index]
    
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data="answer_yes")],
        [InlineKeyboardButton("❌ Нет", callback_data="answer_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"**Вопрос {index + 1}/9:**\n\n{question}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_result(query, user_id):
    """Показать результат"""
    suit = user_data[user_id]["suit"]
    answers = user_data[user_id]["answers"]
    
    # Подсчёт "Да"
    yes_count = answers.count("yes")
    
    # Определение ранга карты
    if yes_count <= 1:
        rank = "A"
    elif yes_count == 2:
        rank = "K"
    elif yes_count == 3:
        rank = "Q"
    elif yes_count == 4:
        rank = "J"
    elif yes_count == 5:
        rank = "10"
    elif yes_count == 6:
        rank = "9"
    elif yes_count == 7:
        rank = "8"
    elif yes_count == 8:
        rank = "7"
    else:
        rank = "6"
    
    card_key = f"{suit}-{rank}"
    result = ARCHETYPES.get(card_key, {})
    
    # Формирование результата
    message = f"""
🎴 **ВАША КАРТА: {suit} {rank}**

{result.get('title', 'Нет данных')}

{result.get('problem', '')}

{result.get('level', '')}

{result.get('description', '')}

📖 {result.get('fairy_tale', '')}

🔗 [Подробнее]({result.get('link', '')})
"""
    
    keyboard = [[InlineKeyboardButton("🔄 Новая диагностика", callback_data="new_test")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text(
        "🎴 **Как пользоваться ботом:**\n\n"
        "1. Нажмите /start\n"
        "2. Выберите сферу жизни\n"
        "3. Ответьте на 9 вопросов\n"
        "4. Получите свой архетип\n\n"
        "Команды:\n"
        "/start - Начать диагностику\n"
        "/help - Помощь",
        parse_mode="Markdown"
    )

# ========== ЗАПУСК БОТА ==========

def main():
    """Запуск бота"""
    if not TOKEN:
        logger.error("❌ Токен не найден! Установите переменную TOKEN_BOT2")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запуск
    logger.info("✅ Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

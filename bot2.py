import os
import logging
from collections import Counter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from archetypes import ARCHETYPES

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ ТОКЕН ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# ============================================
# ДАННЫЕ ТЕСТА
# ============================================

# ЭТАП 1: Определение программы (24 вопроса)
STAGE_1_QUESTIONS = [
    # Блок СБ (6 вопросов)
    {"text": "Ты чувствуешь себя бессильным перед обстоятельствами?", "program": "СБ"},
    {"text": "Ты часто ввязываешься в конфликты?", "program": "СБ"},
    {"text": "Ты манипулируешь людьми, чтобы получить желаемое?", "program": "СБ"},
    {"text": "Ты следуешь правилам системы?", "program": "СБ"},
    {"text": "Люди идут за тобой?", "program": "СБ"},
    {"text": "Ты чувствуешь ответственность за других?", "program": "СБ"},
    
    # Блок ТФ (6 вопросов)
    {"text": "Твоё тело часто болит или болеет?", "program": "ТФ"},
    {"text": "Ты терпишь физическую боль?", "program": "ТФ"},
    {"text": "Ты зарабатываешь своим телом (спорт, красота, физический труд)?", "program": "ТФ"},
    {"text": "Ты следуешь правилам здорового образа жизни?", "program": "ТФ"},
    {"text": "Твоё тело — твоя гордость?", "program": "ТФ"},
    {"text": "Ты помогаешь другим с их телом (врач, тренер, массажист)?", "program": "ТФ"},
    
    # Блок УБ (6 вопросов)
    {"text": "Ты часто не понимаешь, что происходит вокруг?", "program": "УБ"},
    {"text": "Ты любишь спорить и доказывать свою правоту?", "program": "УБ"},
    {"text": "Ты используешь знания для манипуляций?", "program": "УБ"},
    {"text": "Ты эксперт в своей области?", "program": "УБ"},
    {"text": "Ты видишь связи между явлениями?", "program": "УБ"},
    {"text": "Ты передаёшь знания другим?", "program": "УБ"},
    
    # Блок ЧВ (6 вопросов)
    {"text": "Ты чувствуешь себя нелюбимым?", "program": "ЧВ"},
    {"text": "Ты постоянно ищешь любовь?", "program": "ЧВ"},
    {"text": "Ты манипулируешь чувствами других?", "program": "ЧВ"},
    {"text": "Ты в стабильных отношениях?", "program": "ЧВ"},
    {"text": "Ты умеешь любить?", "program": "ЧВ"},
    {"text": "Ты помогаешь другим с их отношениями?", "program": "ЧВ"}
]

# ЭТАП 2: Определение уровня (12 вопросов)
STAGE_2_QUESTIONS = [
    {"text": "Ты чувствуешь себя жертвой обстоятельств?", "level": "6"},
    {"text": "Ты постоянно борешься и конфликтуешь?", "level": "7"},
    {"text": "Ты действуешь через манипуляции и хитрость?", "level": "8"},
    {"text": "Ты следуешь правилам и работаешь в системе?", "level": "9"},
    {"text": "Ты ведёшь за собой людей?", "level": "10"},
    {"text": "Ты выполняешь свою роль безупречно?", "level": "J"},
    {"text": "Ты передаёшь мастерство другим?", "level": "Q"},
    {"text": "Ты создаёшь системы и правила?", "level": "K"},
    {"text": "Ты свободен от своей программы?", "level": "A"},
    {"text": "Ты чувствуешь внутреннюю свободу?", "level": "A"},
    {"text": "Ты живёшь вне игры?", "level": "A"},
    {"text": "Ты просто есть?", "level": "A"}
]

# Названия программ
PROGRAM_NAMES = {
    'СБ': '♠️ Силовая программа',
    'ТФ': '♥️ Телесная программа',
    'УБ': '♣️ Познавательная программа',
    'ЧВ': '♦️ Эмоциональная программа'
}

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_progress_bar(current, total, length=10):
    """Создаёт визуальную полосу прогресса"""
    filled = int(length * current / total)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar} {current}/{total}"

# ============================================
# КОМАНДЫ БОТА
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало работы с ботом"""
    user = update.effective_user
    context.user_data.clear()
    
    welcome_text = f"""Привет, {user.first_name}! 👋

🎴 Добро пожаловать в диагностику архетипов!

🎯 Что тебя ждёт:

1️⃣ Определение программы (24 вопроса)
   → Узнаешь свою базовую программу

2️⃣ Определение уровня (12 вопросов)
   → Найдём твой текущий уровень развития

3️⃣ Персональный архетип
   → Получишь полное описание + сказку

⏱ Займёт 10-15 минут

Готов начать?"""
    
    keyboard = [[InlineKeyboardButton("🚀 Начать тест", callback_data="start_test")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# ============================================
# ЭТАП 1: ОПРЕДЕЛЕНИЕ ПРОГРАММЫ
# ============================================

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает тест"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['stage'] = 'stage_1'
    context.user_data['stage_1_answers'] = {'СБ': 0, 'ТФ': 0, 'УБ': 0, 'ЧВ': 0}
    context.user_data['stage_2_answers'] = []
    context.user_data['current_question'] = 0
    
    intro_text = """🎯 ЭТАП 1: ОПРЕДЕЛЕНИЕ ПРОГРАММЫ

Сейчас я задам тебе 24 вопроса.

Отвечай честно, выбирай то, что ближе именно тебе.

Здесь нет правильных или неправильных ответов!

Готов?"""
    
    keyboard = [[InlineKeyboardButton("✅ Начать", callback_data="begin_stage_1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(intro_text, reply_markup=reply_markup)

async def begin_stage_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает вопросы этапа 1"""
    query = update.callback_query
    await query.answer()
    
    await send_stage_1_question(query, context)

async def send_stage_1_question(query, context):
    """Отправляет вопрос этапа 1"""
    question_num = context.user_data['current_question']
    
    if question_num >= len(STAGE_1_QUESTIONS):
        await finish_stage_1(query, context)
        return
    
    question = STAGE_1_QUESTIONS[question_num]
    progress = get_progress_bar(question_num, len(STAGE_1_QUESTIONS))
    
    text = f"""📊 ЭТАП 1: Определение программы

{progress}

❓ Вопрос {question_num + 1} из {len(STAGE_1_QUESTIONS)}:

{question['text']}"""
    
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="s1_yes")],
        [InlineKeyboardButton("Нет", callback_data="s1_no")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def handle_stage_1_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ этапа 1"""
    query = update.callback_query
    await query.answer()
    
    answer = query.data.replace("s1_", "")
    question_num = context.user_data['current_question']
    question = STAGE_1_QUESTIONS[question_num]
    
    if answer == 'yes':
        context.user_data['stage_1_answers'][question['program']] += 1
    
    context.user_data['current_question'] += 1
    
    # Подбадривание каждые 6 вопросов
    if (question_num + 1) % 6 == 0 and (question_num + 1) < len(STAGE_1_QUESTIONS):
        encouragement = f"""✅ Отлично! Пройдено {question_num + 1} из 24 вопросов.

Продолжаем..."""
        keyboard = [[InlineKeyboardButton("➡️ Продолжить", callback_data="continue_s1")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(encouragement, reply_markup=reply_markup)
    else:
        await send_stage_1_question(query, context)

async def continue_s1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Продолжает этап 1 после подбадривания"""
    query = update.callback_query
    await query.answer()
    await send_stage_1_question(query, context)

async def finish_stage_1(query, context):
    """Завершение этапа 1"""
    answers = context.user_data['stage_1_answers']
    program = max(answers, key=answers.get)
    context.user_data['program'] = program
    context.user_data['current_question'] = 0
    context.user_data['stage'] = 'stage_2'
    
    result_text = f"""✅ ЭТАП 1 ЗАВЕРШЁН!

Твоя программа: {PROGRAM_NAMES[program]}

🎯 ЭТАП 2: ОПРЕДЕЛЕНИЕ УРОВНЯ

Теперь определим твой уровень развития.

Вопрос 1 из 12:

Готов?"""
    
    keyboard = [[InlineKeyboardButton("✅ Начать этап 2", callback_data="begin_stage_2")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_text, reply_markup=reply_markup)

# ============================================
# ЭТАП 2: ОПРЕДЕЛЕНИЕ УРОВНЯ
# ============================================

async def begin_stage_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает вопросы этапа 2"""
    query = update.callback_query
    await query.answer()
    
    await send_stage_2_question(query, context)

async def send_stage_2_question(query, context):
    """Отправляет вопрос этапа 2"""
    question_num = context.user_data['current_question']
    
    if question_num >= len(STAGE_2_QUESTIONS):
        await finish_stage_2(query, context)
        return
    
    question = STAGE_2_QUESTIONS[question_num]
    progress = get_progress_bar(question_num, len(STAGE_2_QUESTIONS))
    
    text = f"""📊 ЭТАП 2: Определение уровня

{progress}

❓ Вопрос {question_num + 1} из {len(STAGE_2_QUESTIONS)}:

{question['text']}"""
    
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="s2_yes")],
        [InlineKeyboardButton("Нет", callback_data="s2_no")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def handle_stage_2_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ этапа 2"""
    query = update.callback_query
    await query.answer()
    
    answer = query.data.replace("s2_", "")
    question_num = context.user_data['current_question']
    question = STAGE_2_QUESTIONS[question_num]
    
    if answer == 'yes':
        context.user_data['stage_2_answers'].append(question['level'])
    
    context.user_data['current_question'] += 1
    
    # Подбадривание каждые 4 вопроса
    if (question_num + 1) % 4 == 0 and (question_num + 1) < len(STAGE_2_QUESTIONS):
        encouragement = f"""✅ Отлично! Пройдено {question_num + 1} из 12 вопросов.

Продолжаем..."""
        keyboard = [[InlineKeyboardButton("➡️ Продолжить", callback_data="continue_s2")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(encouragement, reply_markup=reply_markup)
    else:
        await send_stage_2_question(query, context)

async def continue_s2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Продолжает этап 2 после подбадривания"""
    query = update.callback_query
    await query.answer()
    await send_stage_2_question(query, context)

async def finish_stage_2(query, context):
    """Завершение этапа 2 и вывод результата"""
    level_answers = context.user_data['stage_2_answers']
    
    if not level_answers:
        level = '6'
    else:
        level = Counter(level_answers).most_common(1)[0][0]
    
    program = context.user_data['program']
    archetype_key = f"{program}-{level}"
    
    archetype = ARCHETYPES.get(archetype_key)
    
    if not archetype:
        await query.edit_message_text(
            "❌ Ошибка: архетип не найден. Нажми /start, чтобы начать заново."
        )
        return
    
    result = (
        f"🎴 {archetype['card']} {archetype['title']}\n\n"
        f"👤 КТО ТЫ:\n{archetype['who']}\n\n"
        f"💭 НАРРАТИВ:\n{archetype['narrative']}\n\n"
        f"🌑 ТЕНЬ:\n{archetype['shadow']}\n\n"
        f"🪤 ЛОВУШКА:\n{archetype['trap']}\n\n"
        f"❓ ЧТО ДЕЛАТЬ:\n{archetype['what_to_do']}\n\n"
        f"📈 КАК РАСТИ:\n{archetype['how_to_grow']}\n\n"
        f"💰 ДЕНЬГИ:\n{archetype['money']}\n\n"
        f"📖 СКАЗКА: {archetype['fairy_tale']}\n"
        f"🔗 Читать: {archetype['link']}\n\n"
        f"✍️ Автор методики: Мейстер А.Ю."
    )
    
    keyboard = [
        [InlineKeyboardButton("📖 Открыть сказку", url=archetype['link'])],
        [InlineKeyboardButton("🔄 Пройти тест заново", callback_data="start_test")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result, reply_markup=reply_markup)

# ============================================
# ОБРАБОТЧИК CALLBACK
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на кнопки"""
    query = update.callback_query
    data = query.data
    
    if data == "start_test":
        await start_test(update, context)
    elif data == "begin_stage_1":
        await begin_stage_1(update, context)
    elif data.startswith("s1_"):
        await handle_stage_1_answer(update, context)
    elif data == "continue_s1":
        await continue_s1(update, context)
    elif data == "begin_stage_2":
        await begin_stage_2(update, context)
    elif data.startswith("s2_"):
        await handle_stage_2_answer(update, context)
    elif data == "continue_s2":
        await continue_s2(update, context)

# ============================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================

def main():
    """Запуск бота"""
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("✅ Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

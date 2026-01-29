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

# Описания программ
PROGRAM_DESCRIPTIONS = {
    'СБ': 'Ты ориентируешься на власть, силу и влияние. Для тебя важно, кто главный и кто принимает решения.',
    'ТФ': 'Ты ориентируешься на тело, здоровье и физические ощущения. Для тебя важно, как ты себя чувствуешь физически.',
    'УБ': 'Ты ориентируешься на знания, понимание и логику. Для тебя важно разобраться, как всё устроено.',
    'ЧВ': 'Ты ориентируешься на чувства, отношения и любовь. Для тебя важно, кто и как к тебе относится.'
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

Этот тест поможет определить твой текущий уровень развития.

🎯 Что тебя ждёт:

1️⃣ **ЭТАП 1: Определение программы** (24 вопроса)
   → Узнаешь свою базовую программу (СБ, ТФ, УБ или ЧВ)

2️⃣ **ЭТАП 2: Определение уровня** (12 вопросов)
   → Найдём твой текущий уровень развития (6, 7, 8, 9, 10, J, Q, K, A)

3️⃣ **Персональный архетип**
   → Получишь полное описание + сказку для работы

⏱ Займёт 10-15 минут

📌 Отвечай честно, как есть сейчас, а не как хотелось бы.

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
    
    intro_text = """🎯 **ЭТАП 1: ОПРЕДЕЛЕНИЕ ПРОГРАММЫ**

Сейчас я задам тебе 24 вопроса, чтобы определить твою базовую программу.

📋 Вопросы разделены на 4 блока:
• ♠️ Силовая программа (СБ) — 6 вопросов
• ♥️ Телесная программа (ТФ) — 6 вопросов
• ♣️ Познавательная программа (УБ) — 6 вопросов
• ♦️ Эмоциональная программа (ЧВ) — 6 вопросов

⚡ Отвечай быстро, первое, что приходит в голову.

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
    
    # Определяем текущий блок
    if question_num < 6:
        block = "♠️ Блок СБ (Силовая программа)"
    elif question_num < 12:
        block = "♥️ Блок ТФ (Телесная программа)"
    elif question_num < 18:
        block = "♣️ Блок УБ (Познавательная программа)"
    else:
        block = "♦️ Блок ЧВ (Эмоциональная программа)"
    
    text = f"""📊 **ЭТАП 1: Определение программы**

{block}

{progress}

❓ **Вопрос {question_num + 1} из {len(STAGE_1_QUESTIONS)}:**

{question['text']}"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data="s1_yes")],
        [InlineKeyboardButton("❌ Нет", callback_data="s1_no")]
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
    
    # Подбадривание каждые 6 вопросов (после каждого блока)
    if (question_num + 1) % 6 == 0 and (question_num + 1) < len(STAGE_1_QUESTIONS):
        block_num = (question_num + 1) // 6
        encouragement = f"""✅ **Блок {block_num} завершён!**

Отлично! Пройдено {question_num + 1} из 24 вопросов.

Продолжаем следующий блок..."""
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
    
    # Показываем результаты по всем программам
    results_text = "📊 **Твои результаты по программам:**\n\n"
    for prog, count in sorted(answers.items(), key=lambda x: x[1], reverse=True):
        results_text += f"{PROGRAM_NAMES[prog]}: {count}/6\n"
    
    result_text = f"""✅ **ЭТАП 1 ЗАВЕРШЁН!**

{results_text}

🎯 **Твоя основная программа:**
{PROGRAM_NAMES[program]}

💡 {PROGRAM_DESCRIPTIONS[program]}

---

🎯 **ЭТАП 2: ОПРЕДЕЛЕНИЕ УРОВНЯ**

Теперь определим твой уровень развития внутри этой программы.

Это поможет понять, на каком этапе пути ты находишься сейчас.

Готов продолжить?"""
    
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
    
    intro_text = """🎯 **ЭТАП 2: ОПРЕДЕЛЕНИЕ УРОВНЯ**

Сейчас я задам тебе 12 вопросов, чтобы определить твой уровень развития.

📊 Уровни развития:
• 6 — Жертва
• 7 — Боец
• 8 — Манипулятор
• 9 — Исполнитель
• 10 — Лидер
• J (Валет) — Мастер
• Q (Дама) — Учитель
• K (Король) — Создатель
• A (Туз) — Свободный

⚡ Отвечай честно, как есть сейчас.

Готов?"""
    
    keyboard = [[InlineKeyboardButton("✅ Начать", callback_data="start_stage_2_questions")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(intro_text, reply_markup=reply_markup)

async def start_stage_2_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    text = f"""📊 **ЭТАП 2: Определение уровня**

{progress}

❓ **Вопрос {question_num + 1} из {len(STAGE_2_QUESTIONS)}:**

{question['text']}"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data="s2_yes")],
        [InlineKeyboardButton("❌ Нет", callback_data="s2_no")]
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
        encouragement = f"""✅ **Отлично!**

Пройдено {question_num + 1} из 12 вопросов.

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
    
    # Определяем уровень
    if not level_answers:
        level = '6'
    else:
        # Подсчитываем самый частый ответ
        level_counts = Counter(level_answers)
        level = level_counts.most_common(1)[0][0]
    
    program = context.user_data['program']
    archetype_key = f"{program}-{level}"
    
    archetype = ARCHETYPES.get(archetype_key)
    
    if not archetype:
        await query.edit_message_text(
            f"❌ **Ошибка:** архетип {archetype_key} не найден.\n\n"
            "Нажми /start, чтобы начать заново."
        )
        return
    
    # Формируем результат
    result = (
        f"🎉 **ТЕСТ ЗАВЕРШЁН!**\n\n"
        f"🎴 **Твой архетип:**\n"
        f"{archetype['card']} **{archetype['title']}**\n\n"
        f"---\n\n"
        f"👤 **КТО ТЫ:**\n{archetype['who']}\n\n"
        f"💭 **НАРРАТИВ:**\n{archetype['narrative']}\n\n"
        f"🌑 **ТЕНЬ:**\n{archetype['shadow']}\n\n"
        f"🪤 **ЛОВУШКА:**\n{archetype['trap']}\n\n"
        f"❓ **ЧТО ДЕЛАТЬ:**\n{archetype['what_to_do']}\n\n"
        f"📈 **КАК РАСТИ:**\n{archetype['how_to_grow']}\n\n"
        f"💰 **ДЕНЬГИ:**\n{archetype['money']}\n\n"
        f"📖 **СКАЗКА:** {archetype['fairy_tale']}\n\n"
        f"---\n\n"
        f"✍️ Автор методики: Мейстер А.Ю."
    )
    
    keyboard = [
        [InlineKeyboardButton("📖 Открыть сказку", url=archetype['link'])],
        [InlineKeyboardButton("🔄 Пройти тест заново", callback_data="start_test")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result, reply_markup=reply_markup, disable_web_page_preview=True)

# ============================================
# ОБРАБОТЧИК CALLBACK
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на кнопки"""
    query = update.callback_query
    data = query.data
    
    handlers = {
        "start_test": start_test,
        "begin_stage_1": begin_stage_1,
        "continue_s1": continue_s1,
        "begin_stage_2": begin_stage_2,
        "start_stage_2_questions": start_stage_2_questions,
        "continue_s2": continue_s2,
    }
    
    if data in handlers:
        await handlers[data](update, context)
    elif data.startswith("s1_"):
        await handle_stage_1_answer(update, context)
    elif data.startswith("s2_"):
        await handle_stage_2_answer(update, context)

# ============================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================

def main():
    """Запуск бота"""
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    
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

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from archetypes import ARCHETYPES

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
STAGE_1, STAGE_2 = range(2)

# Вопросы ЭТАП 1 (24 вопроса для определения программы)
STAGE_1_QUESTIONS = [
    # Блок 1: Силовая программа (СБ)
    {
        "text": "1️⃣ Когда кто-то пытается тебя контролировать, ты:",
        "answers": ["Подчиняюсь, чтобы избежать конфликта", "Сопротивляюсь открыто", "Ищу способ обойти контроль", "Принимаю правила игры"],
        "program": "СБ"
    },
    {
        "text": "2️⃣ Твоя реакция на несправедливость:",
        "answers": ["Терплю и молчу", "Вступаю в борьбу", "Ищу обходные пути", "Действую по закону"],
        "program": "СБ"
    },
    {
        "text": "3️⃣ Как ты относишься к власти?",
        "answers": ["Боюсь её", "Борюсь с ней", "Манипулирую ею", "Уважаю, если она справедлива"],
        "program": "СБ"
    },
    {
        "text": "4️⃣ В конфликте ты:",
        "answers": ["Избегаю и ухожу", "Дерусь до конца", "Играю на слабостях противника", "Ищу компромисс"],
        "program": "СБ"
    },
    {
        "text": "5️⃣ Что для тебя сила?",
        "answers": ["То, что меня подавляет", "То, что я использую", "То, чем я манипулирую", "Инструмент для порядка"],
        "program": "СБ"
    },
    {
        "text": "6️⃣ Твоё отношение к иерархии:",
        "answers": ["Я внизу", "Я против неё", "Я играю в ней", "Я часть системы"],
        "program": "СБ"
    },
    
    # Блок 2: Телесная программа (ТФ)
    {
        "text": "7️⃣ Как ты относишься к своему телу?",
        "answers": ["Оно меня предаёт", "Я заставляю его работать", "Я использую его как капитал", "Я забочусь о нём по правилам"],
        "program": "ТФ"
    },
    {
        "text": "8️⃣ Когда ты болеешь:",
        "answers": ["Я чувствую себя жертвой", "Я терплю и продолжаю", "Я ищу быстрое решение", "Я следую протоколу лечения"],
        "program": "ТФ"
    },
    {
        "text": "9️⃣ Твоё отношение к боли:",
        "answers": ["Боль — моя судьба", "Боль — это слабость", "Боль — это сигнал", "Боль — это то, что нужно лечить"],
        "program": "ТФ"
    },
    {
        "text": "🔟 Как ты зарабатываешь?",
        "answers": ["Я почти не зарабатываю", "Физическим трудом", "Своим телом (спорт, красота)", "Стабильной работой"],
        "program": "ТФ"
    },
    {
        "text": "1️⃣1️⃣ Твоё отношение к здоровью:",
        "answers": ["Я всегда болен", "Я игнорирую здоровье", "Я инвестирую в тело", "Я следую ЗОЖ"],
        "program": "ТФ"
    },
    {
        "text": "1️⃣2️⃣ Что для тебя тело?",
        "answers": ["Враг", "Инструмент", "Капитал", "Храм"],
        "program": "ТФ"
    },
    
    # Блок 3: Познавательная программа (УБ)
    {
        "text": "1️⃣3️⃣ Как ты относишься к знаниям?",
        "answers": ["Я ничего не понимаю", "Я спорю, чтобы доказать правоту", "Я использую знания для манипуляций", "Я изучаю систематически"],
        "program": "УБ"
    },
    {
        "text": "1️⃣4️⃣ Когда ты не понимаешь что-то:",
        "answers": ["Я сдаюсь", "Я спорю", "Я делаю вид, что понимаю", "Я изучаю вопрос"],
        "program": "УБ"
    },
    {
        "text": "1️⃣5️⃣ Твоё отношение к истине:",
        "answers": ["Истина недостижима", "Истина — это то, что я докажу", "Истина — это инструмент", "Истина — это то, что проверено"],
        "program": "УБ"
    },
    {
        "text": "1️⃣6️⃣ Как ты учишься?",
        "answers": ["Мне трудно учиться", "Я учусь через спор", "Я учусь, чтобы манипулировать", "Я учусь по системе"],
        "program": "УБ"
    },
    {
        "text": "1️⃣7️⃣ Что для тебя знание?",
        "answers": ["То, чего мне не хватает", "То, что я доказываю", "То, чем я манипулирую", "То, что я накапливаю"],
        "program": "УБ"
    },
    {
        "text": "1️⃣8️⃣ Твоё отношение к ошибкам:",
        "answers": ["Я постоянно ошибаюсь", "Я не признаю ошибок", "Я скрываю ошибки", "Я учусь на ошибках"],
        "program": "УБ"
    },
    
    # Блок 4: Эмоциональная программа (ЧВ)
    {
        "text": "1️⃣9️⃣ Как ты относишься к любви?",
        "answers": ["Меня никто не любит", "Я ищу любовь, но не нахожу", "Я манипулирую чувствами", "Я в стабильных отношениях"],
        "program": "ЧВ"
    },
    {
        "text": "2️⃣0️⃣ Когда тебя отвергают:",
        "answers": ["Я чувствую себя недостойным", "Я продолжаю искать", "Я мщу", "Я принимаю и иду дальше"],
        "program": "ЧВ"
    },
    {
        "text": "2️⃣1️⃣ Твоё отношение к близости:",
        "answers": ["Я боюсь близости", "Я жажду близости", "Я использую близость", "Я строю близость"],
        "program": "ЧВ"
    },
    {
        "text": "2️⃣2️⃣ Как ты проявляешь любовь?",
        "answers": ["Я не умею любить", "Я отдаю всё", "Я контролирую через любовь", "Я забочусь и поддерживаю"],
        "program": "ЧВ"
    },
    {
        "text": "2️⃣3️⃣ Что для тебя любовь?",
        "answers": ["То, чего мне не хватает", "То, что я ищу", "То, чем я манипулирую", "То, что я строю"],
        "program": "ЧВ"
    },
    {
        "text": "2️⃣4️⃣ Твоё отношение к одиночеству:",
        "answers": ["Я всегда один", "Я боюсь одиночества", "Мне комфортно одному", "Я выбираю, когда быть одному"],
        "program": "ЧВ"
    }
]

# Вопросы ЭТАП 2 (12 вопросов для определения уровня)
STAGE_2_QUESTIONS = {
    "СБ": [
        {"text": "Ты чувствуешь себя бессильным перед системой?", "level": 6},
        {"text": "Ты постоянно в конфликтах?", "level": 7},
        {"text": "Ты используешь хитрость вместо прямой силы?", "level": 8},
        {"text": "Ты работаешь в иерархии и следуешь правилам?", "level": 9},
        {"text": "Люди идут за тобой?", "level": 10},
        {"text": "Ты нашёл своё призвание (защитник/судья)?", "level": "J"},
        {"text": "Ты обучаешь других воинов/лидеров?", "level": "Q"},
        {"text": "Ты создал систему власти?", "level": "K"},
        {"text": "Ты свободен от власти и силы?", "level": "A"},
        {"text": "Ты чувствуешь, что сила — это иллюзия?", "level": "A"},
        {"text": "Ты служишь силе, а не владеешь ею?", "level": "J"},
        {"text": "Ты передаёшь мастерство силы?", "level": "Q"}
    ],
    "ТФ": [
        {"text": "Твоё тело постоянно болеет?", "level": 6},
        {"text": "Ты терпишь боль или насилуешь тело?", "level": 7},
        {"text": "Ты зарабатываешь своим телом?", "level": 8},
        {"text": "Ты следуешь протоколам ЗОЖ?", "level": 9},
        {"text": "Твоё тело — твоя гордость?", "level": 10},
        {"text": "Ты помогаешь другим обрести здоровье?", "level": "J"},
        {"text": "Ты учишь исцелению?", "level": "Q"},
        {"text": "Ты создал систему здоровья?", "level": "K"},
        {"text": "Ты свободен от тела?", "level": "A"},
        {"text": "Ты не боишься болезней и смерти?", "level": "A"},
        {"text": "Ты лечишь других?", "level": "J"},
        {"text": "Ты передаёшь знания о теле?", "level": "Q"}
    ],
    "УБ": [
        {"text": "Ты чувствуешь себя глупым?", "level": 6},
        {"text": "Ты постоянно споришь?", "level": 7},
        {"text": "Ты используешь знания для манипуляций?", "level": 8},
        {"text": "Ты эксперт в своей области?", "level": 9},
        {"text": "Ты создаёшь концепции и теории?", "level": 10},
        {"text": "Ты обучаешь других?", "level": "J"},
        {"text": "Ты учишь методу познания?", "level": "Q"},
        {"text": "Ты создал новую парадигму мышления?", "level": "K"},
        {"text": "Ты свободен от знания?", "level": "A"},
        {"text": "Ты видишь, что знание — это конструкция?", "level": "A"},
        {"text": "Ты передаёшь знания?", "level": "J"},
        {"text": "Ты учишь думать?", "level": "Q"}
    ],
    "ЧВ": [
        {"text": "Ты чувствуешь себя нелюбимым?", "level": 6},
        {"text": "Ты постоянно ищешь любовь?", "level": 7},
        {"text": "Ты манипулируешь чувствами?", "level": 8},
        {"text": "Ты в стабильных отношениях?", "level": 9},
        {"text": "Ты любишь по-настоящему?", "level": 10},
        {"text": "Ты помогаешь другим любить?", "level": "J"},
        {"text": "Ты учишь безусловной любви?", "level": "Q"},
        {"text": "Ты создал систему любви?", "level": "K"},
        {"text": "Ты — сама любовь?", "level": "A"},
        {"text": "Ты любишь всё и всех?", "level": "A"},
        {"text": "Ты исцеляешь сердца?", "level": "J"},
        {"text": "Ты передаёшь дар любви?", "level": "Q"}
    ]
}

# Промежуточные экраны подбадривания
ENCOURAGEMENT_SCREENS = [
    "🌟 Отлично! Ты уже прошёл четверть пути!\n\n💪 Продолжай — каждый ответ приближает тебя к истине.",
    "🔥 Половина позади! Ты молодец!\n\n🎯 Твой архетип уже начинает проявляться...",
    "✨ Три четверти пройдено!\n\n🚀 Ещё немного — и ты узнаешь, кто ты на самом деле!",
    "🎭 Последний рывок!\n\n🏆 Твой архетип почти раскрыт!"
]

# Стартовое сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диагностики"""
    welcome_text = """
♠️♥️♣️♦️ **ВАРИАТИКА: АРХЕТИПИЧЕСКАЯ ДИАГНОСТИКА** ♦️♣️♥️♠️

🎭 **Добро пожаловать в путешествие к себе!**

Эта диагностика поможет тебе:
✅ Понять свою базовую программу
✅ Определить уровень развития
✅ Увидеть теневые стороны
✅ Найти путь роста

📊 **Как это работает:**

**ЭТАП 1** (24 вопроса)
→ Определяем твою программу:
   ♠️ Силовая (СБ)
   ♥️ Телесная (ТФ)
   ♣️ Познавательная (УБ)
   ♦️ Эмоциональная (ЧВ)

**ЭТАП 2** (12 вопросов)
→ Определяем твой уровень:
   6, 7, 8, 9, 10, J, Q, K, A

**ЭТАП 3**
→ Получаешь полное описание архетипа

⏱ **Время:** 10-15 минут
🎯 **Результат:** Твоя карта развития

Готов начать? Нажми /test
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало теста"""
    context.user_data['stage'] = 1
    context.user_data['question_index'] = 0
    context.user_data['answers'] = {'СБ': 0, 'ТФ': 0, 'УБ': 0, 'ЧВ': 0}
    context.user_data['level_answers'] = []
    
    await ask_question(update, context)
    return STAGE_1

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Задать вопрос"""
    stage = context.user_data['stage']
    question_index = context.user_data['question_index']
    
    if stage == 1:
        # ЭТАП 1: Определение программы
        if question_index < len(STAGE_1_QUESTIONS):
            question = STAGE_1_QUESTIONS[question_index]
            
            # Промежуточные экраны подбадривания (каждые 6 вопросов)
            if question_index > 0 and question_index % 6 == 0:
                encouragement_index = (question_index // 6) - 1
                if encouragement_index < len(ENCOURAGEMENT_SCREENS):
                    await update.message.reply_text(
                        ENCOURAGEMENT_SCREENS[encouragement_index],
                        parse_mode='Markdown'
                    )
            
            # Создаём клавиатуру с вариантами ответов
            keyboard = [[answer] for answer in question['answers']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                f"📋 **ЭТАП 1/2**\n\n{question['text']}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            # ЭТАП 1 завершён, переходим к ЭТАП 2
            await start_stage_2(update, context)
            return STAGE_2
    
    elif stage == 2:
        # ЭТАП 2: Определение уровня
        program = context.user_data['program']
        questions = STAGE_2_QUESTIONS[program]
        
        if question_index < len(questions):
            question = questions[question_index]
            
            # Промежуточные экраны (каждые 4 вопроса)
            if question_index > 0 and question_index % 4 == 0:
                await update.message.reply_text(
                    f"🎯 Вопрос {question_index + 1}/12\n\n💫 Твой уровень проявляется...",
                    parse_mode='Markdown'
                )
            
            keyboard = [["Да", "Нет"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                f"📋 **ЭТАП 2/2**\n\n{question['text']}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            # ЭТАП 2 завершён, показываем результат
            await show_result(update, context)
            return ConversationHandler.END
    
    return stage

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа"""
    stage = context.user_data['stage']
    question_index = context.user_data['question_index']
    answer = update.message.text
    
    if stage == 1:
        # ЭТАП 1: Подсчёт баллов по программам
        question = STAGE_1_QUESTIONS[question_index]
        program = question['program']
        context.user_data['answers'][program] += 1
        
        context.user_data['question_index'] += 1
        return await ask_question(update, context)
    
    elif stage == 2:
        # ЭТАП 2: Определение уровня
        program = context.user_data['program']
        question = STAGE_2_QUESTIONS[program][question_index]
        
        if answer == "Да":
            context.user_data['level_answers'].append(question['level'])
        
        context.user_data['question_index'] += 1
        return await ask_question(update, context)

async def start_stage_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переход к ЭТАП 2"""
    # Определяем программу с максимальным количеством баллов
    answers = context.user_data['answers']
    program = max(answers, key=answers.get)
    context.user_data['program'] = program
    
    program_names = {
        'СБ': '♠️ СИЛОВАЯ ПРОГРАММА',
        'ТФ': '♥️ ТЕЛЕСНАЯ ПРОГРАММА',
        'УБ': '♣️ ПОЗНАВАТЕЛЬНАЯ ПРОГРАММА',
        'ЧВ': '♦️ ЭМОЦИОНАЛЬНАЯ ПРОГРАММА'
    }
    
    transition_text = f"""
🎉 **ЭТАП 1 ЗАВЕРШЁН!**

🎯 **Твоя базовая программа:**
{program_names[program]}

---

📊 **ЭТАП 2: ОПРЕДЕЛЕНИЕ УРОВНЯ**

Сейчас мы определим, на каком уровне развития ты находишься:

6️⃣ — Начальный уровень
7️⃣ — Борьба
8️⃣ — Манипуляция
9️⃣ — Профессионализм
🔟 — Мастерство
🃏 — Служение
👑 — Учительство
👑 — Создание системы
🌟 — Трансценденция

Готов? Продолжаем!
"""
    
    await update.message.reply_text(transition_text, parse_mode='Markdown')
    
    context.user_data['stage'] = 2
    context.user_data['question_index'] = 0
    
    await ask_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать результат"""
    program = context.user_data['program']
    level_answers = context.user_data['level_answers']
    
    # Определяем уровень (самый частый ответ)
    if level_answers:
        from collections import Counter
        level = Counter(level_answers).most_common(1)[0][0]
    else:
        level = 6  # По умолчанию
    
    # Получаем архетип
    archetype_key = f"{program}-{level}"
    archetype = ARCHETYPES.get(archetype_key)
    
    if not archetype:
        await update.message.reply_text("❌ Ошибка: архетип не найден.")
        return ConversationHandler.END
    
    # Формируем результат
    result_text = f"""
🎭 **РЕЗУЛЬТАТ ДИАГНОСТИКИ**

━━━━━━━━━━━━━━━━━━━━━

{archetype['card']} **{archetype['title']}**

━━━━━━━━━━━━━━━━━━━━━

**👤 КТО ТЫ:**
{archetype['who']}

**💭 ТВОЙ НАРРАТИВ:**
{archetype['narrative']}

**🌑 ТЕНЕВАЯ СТОРОНА:**
{archetype['shadow']}

**🕸 ЛОВУШКА:**
{archetype['trap']}

**🎯 ЧТО ДЕЛАТЬ:**
{archetype['what_to_do']}

**🚀 КАК РАСТИ:**
{archetype['how_to_grow']}

**💰 ДЕНЬГИ:**
{archetype['money']}

━━━━━━━━━━━━━━━━━━━━━

📖 **ТВОЯ СКАЗКА:** {archetype['fairy_tale']}

🔗 **ЧИТАТЬ ПОДРОБНЕЕ:**
{archetype['link']}

━━━━━━━━━━━━━━━━━━━━━

✨ **Автор типологии ВАРИАТИКА:**
**Мейстер А.Ю.**

━━━━━━━━━━━━━━━━━━━━━

🔄 Хочешь пройти ещё раз? → /test
❓ Есть вопросы? → /help
"""
    
    await update.message.reply_text(
        result_text,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    help_text = """
📚 **ПОМОЩЬ**

**Команды:**
/start — Начать заново
/test — Пройти диагностику
/help — Эта справка

**О типологии:**
ВАРИАТИКА — это система архетипической диагностики, созданная Мейстером А.Ю.

Она основана на 4 программах:
♠️ Силовая (СБ)
♥️ Телесная (ТФ)
♣️ Познавательная (УБ)
♦️ Эмоциональная (ЧВ)

И 9 уровнях развития:
6, 7, 8, 9, 10, J, Q, K, A

**Контакты:**
По вопросам типологии обращайтесь к автору.
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диагностики"""
    await update.message.reply_text(
        "❌ Диагностика отменена.\n\nЧтобы начать заново, нажми /test",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    """Запуск бота"""
    # Вставь сюда свой токен
    TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    application = Application.builder().token(TOKEN).build()
    
    # Обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('test', test)],
        states={
            STAGE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            STAGE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    
    # Запуск бота
    print("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

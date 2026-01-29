import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)
from archetypes import ARCHETYPES

# ========== НАСТРОЙКИ ==========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ ОШИБКА: Переменная TELEGRAM_BOT_TOKEN не установлена!")

# ========== СОСТОЯНИЯ ==========
STAGE_1_BLOCK_1 = 1
STAGE_1_BLOCK_2 = 2
STAGE_1_BLOCK_3 = 3
STAGE_1_BLOCK_4 = 4
STAGE_1_BLOCK_5 = 5
STAGE_1_BLOCK_6 = 6
STAGE_2 = 7

# ========== ЭТАП 1: ВОПРОСЫ ПО БЛОКАМ (24 вопроса) ==========
STAGE_1_QUESTIONS = {
    "block_1": {
        "title": "🔥 БЛОК 1: ДЕТСКИЕ РАНЫ",
        "description": "Эти вопросы помогут понять, какая травма сформировала твою базовую программу.",
        "questions": [
            {
                "text": "Что было самым страшным в детстве?",
                "options": {
                    "СБ": "Что меня накажут, побьют или унизят",
                    "ТФ": "Что я заболею или умру",
                    "УБ": "Что я окажусь глупым или не пойму что-то важное",
                    "ЧВ": "Что меня не будут любить или бросят"
                }
            },
            {
                "text": "Когда родители ругались, ты думал:",
                "options": {
                    "СБ": "«Это из-за меня. Я виноват»",
                    "ТФ": "«Мне страшно. Я хочу спрятаться»",
                    "УБ": "«Я не понимаю, что происходит»",
                    "ЧВ": "«Они разлюбят друг друга. Меня тоже разлюбят»"
                }
            },
            {
                "text": "Чего тебе не хватало в детстве?",
                "options": {
                    "СБ": "Защиты. Чтобы кто-то сильный защитил меня",
                    "ТФ": "Заботы. Чтобы кто-то позаботился о моём теле",
                    "УБ": "Понимания. Чтобы кто-то объяснил, как устроен мир",
                    "ЧВ": "Любви. Чтобы меня любили просто так"
                }
            },
            {
                "text": "Какая фраза родителей ранила сильнее всего?",
                "options": {
                    "СБ": "«Ты слабак», «Ты ничего не можешь»",
                    "ТФ": "«Ты больной», «С тобой что-то не так»",
                    "УБ": "«Ты тупой», «Ты ничего не понимаешь»",
                    "ЧВ": "«Ты плохой», «Тебя никто не будет любить»"
                }
            }
        ]
    },
    "block_2": {
        "title": "😨 БЛОК 2: БАЗОВЫЙ СТРАХ",
        "description": "Какой страх управляет твоей жизнью?",
        "questions": [
            {
                "text": "Чего ты боишься больше всего?",
                "options": {
                    "СБ": "Что меня уничтожат, подавят, сломают",
                    "ТФ": "Что я заболею, умру, стану инвалидом",
                    "УБ": "Что я окажусь дураком, не пойму что-то важное",
                    "ЧВ": "Что меня бросят, разлюбят, останусь один"
                }
            },
            {
                "text": "Что происходит, когда тебе страшно?",
                "options": {
                    "СБ": "Я замираю или нападаю",
                    "ТФ": "Тело сжимается, болит живот, трудно дышать",
                    "УБ": "Голова пустая, не могу думать",
                    "ЧВ": "Сердце сжимается, хочется плакать"
                }
            },
            {
                "text": "От чего ты убегаешь?",
                "options": {
                    "СБ": "От конфликтов, от тех, кто сильнее",
                    "ТФ": "От боли, от болезней, от врачей",
                    "УБ": "От сложных задач, от экзаменов",
                    "ЧВ": "От отношений, от близости, от любви"
                }
            },
            {
                "text": "Какой кошмар снится чаще всего?",
                "options": {
                    "СБ": "Меня преследуют, нападают, я не могу убежать",
                    "ТФ": "Я падаю, тону, задыхаюсь, умираю",
                    "УБ": "Я на экзамене, ничего не знаю, все смеются",
                    "ЧВ": "Меня бросают, я один, меня никто не любит"
                }
            }
        ]
    },
    "block_3": {
        "title": "🛡️ БЛОК 3: СТРАТЕГИЯ ВЫЖИВАНИЯ",
        "description": "Как ты защищаешься от страха?",
        "questions": [
            {
                "text": "Как ты справляешься с угрозой?",
                "options": {
                    "СБ": "Терплю, молчу или дерусь",
                    "ТФ": "Ухожу в болезнь, игнорирую тело",
                    "УБ": "Делаю вид, что всё понимаю",
                    "ЧВ": "Ищу любовь, цепляюсь за отношения"
                }
            },
            {
                "text": "Что ты делаешь, когда тебе плохо?",
                "options": {
                    "СБ": "Злюсь, нападаю или прячусь",
                    "ТФ": "Болею, ем, пью, курю",
                    "УБ": "Читаю, учусь, ищу информацию",
                    "ЧВ": "Ищу утешения, звоню друзьям, плачу"
                }
            },
            {
                "text": "Какая твоя суперсила?",
                "options": {
                    "СБ": "Я могу терпеть или драться",
                    "ТФ": "Я чувствую своё тело",
                    "УБ": "Я могу понять что угодно",
                    "ЧВ": "Я умею любить"
                }
            },
            {
                "text": "Что ты говоришь себе, когда страшно?",
                "options": {
                    "СБ": "«Надо терпеть» или «Надо драться»",
                    "ТФ": "«Надо выжить» или «Надо вылечиться»",
                    "УБ": "«Надо понять» или «Надо научиться»",
                    "ЧВ": "«Надо найти любовь»"
                }
            }
        ]
    },
    "block_4": {
        "title": "💔 БЛОК 4: ОТНОШЕНИЯ",
        "description": "Как ты строишь отношения с людьми?",
        "questions": [
            {
                "text": "Какие отношения у тебя чаще всего?",
                "options": {
                    "СБ": "Я подчиняюсь или доминирую",
                    "ТФ": "Я болею, меня жалеют",
                    "УБ": "Я учу или учусь",
                    "ЧВ": "Я люблю или меня любят"
                }
            },
            {
                "text": "Почему у тебя не складываются отношения?",
                "options": {
                    "СБ": "Я боюсь, что меня подавят",
                    "ТФ": "Я болею, меня не хотят",
                    "УБ": "Я слишком умный или глупый",
                    "ЧВ": "Я боюсь, что меня бросят"
                }
            },
            {
                "text": "Что ты ждёшь от партнёра?",
                "options": {
                    "СБ": "Чтобы он защитил меня",
                    "ТФ": "Чтобы он позаботился о моём теле",
                    "УБ": "Чтобы он был умным",
                    "ЧВ": "Чтобы он любил меня безусловно"
                }
            },
            {
                "text": "Почему ты расстаёшься?",
                "options": {
                    "СБ": "Он подавляет меня",
                    "ТФ": "Он не заботится о моём теле",
                    "УБ": "Он не понимает меня",
                    "ЧВ": "Он разлюбил меня"
                }
            }
        ]
    },
    "block_5": {
        "title": "💰 БЛОК 5: ДЕНЬГИ И СВОБОДА",
        "description": "Как ты зарабатываешь и тратишь деньги?",
        "questions": [
            {
                "text": "Как ты зарабатываешь деньги?",
                "options": {
                    "СБ": "Я терплю или дерусь за деньги",
                    "ТФ": "Я продаю своё тело",
                    "УБ": "Я продаю свои знания",
                    "ЧВ": "Я продаю свои чувства"
                }
            },
            {
                "text": "На что ты тратишь деньги?",
                "options": {
                    "СБ": "На защиту",
                    "ТФ": "На здоровье",
                    "УБ": "На обучение",
                    "ЧВ": "На отношения"
                }
            },
            {
                "text": "Почему у тебя нет денег?",
                "options": {
                    "СБ": "Меня используют",
                    "ТФ": "Я болею",
                    "УБ": "Я не умею зарабатывать",
                    "ЧВ": "Я трачу всё на других"
                }
            },
            {
                "text": "Что для тебя свобода?",
                "options": {
                    "СБ": "Никто не может меня подавить",
                    "ТФ": "Моё тело здорово и сильно",
                    "УБ": "Я понимаю, как устроен мир",
                    "ЧВ": "Меня любят и я люблю"
                }
            }
        ]
    },
    "block_6": {
        "title": "🎯 БЛОК 6: МИССИЯ",
        "description": "Зачем ты живёшь?",
        "questions": [
            {
                "text": "В чём смысл твоей жизни?",
                "options": {
                    "СБ": "Стать сильным, защитить слабых",
                    "ТФ": "Быть здоровым, помочь другим",
                    "УБ": "Понять мир, научить других",
                    "ЧВ": "Любить и быть любимым"
                }
            },
            {
                "text": "Что ты хочешь оставить после себя?",
                "options": {
                    "СБ": "Систему справедливости",
                    "ТФ": "Здоровое поколение",
                    "УБ": "Знания",
                    "ЧВ": "Любовь"
                }
            },
            {
                "text": "Кем ты хочешь стать?",
                "options": {
                    "СБ": "Воином, судьёй",
                    "ТФ": "Целителем",
                    "УБ": "Учителем",
                    "ЧВ": "Любящим"
                }
            },
            {
                "text": "Что ты хочешь услышать в конце жизни?",
                "options": {
                    "СБ": "«Ты был сильным и справедливым»",
                    "ТФ": "«Ты был здоровым и помог другим»",
                    "УБ": "«Ты был мудрым и научил других»",
                    "ЧВ": "«Ты любил и был любим»"
                }
            }
        ]
    }
}

# ========== ЭТАП 2: ВОПРОСЫ ПО УРОВНЯМ ДИЛТСА (12 вопросов) ==========
STAGE_2_QUESTIONS = [
    {
        "level": "🌍 УРОВЕНЬ 1: ОКРУЖЕНИЕ",
        "text": "Где ты живёшь?",
        "options": {
            "6": "В аду. Меня окружают враги",
            "7": "В зоне боевых действий",
            "8": "В джунглях. Я манипулирую",
            "9": "В системе. Я работаю по правилам",
            "10": "В команде. Я веду людей",
            "J": "На поле боя. Я выполняю роль",
            "Q": "В мастерской. Я учу других",
            "K": "В своём мире. Я создаю правила",
            "A": "Везде и нигде. Я свободен"
        }
    },
    {
        "level": "🌍 УРОВЕНЬ 1: ОКРУЖЕНИЕ",
        "text": "Кто тебя окружает?",
        "options": {
            "6": "Враги, больные, дураки",
            "7": "Конкуренты, противники",
            "8": "Жертвы моих манипуляций",
            "9": "Коллеги, начальники",
            "10": "Команда, последователи",
            "J": "Ученики, пациенты",
            "Q": "Мастера и ученики",
            "K": "Создатели, идеологи",
            "A": "Все и никто"
        }
    },
    {
        "level": "🏃 УРОВЕНЬ 2: ПОВЕДЕНИЕ",
        "text": "Что ты делаешь каждый день?",
        "options": {
            "6": "Терплю, болею, страдаю",
            "7": "Дерусь, лечусь, спорю",
            "8": "Манипулирую, интригую",
            "9": "Работаю по правилам",
            "10": "Веду команду",
            "J": "Выполняю роль",
            "Q": "Обучаю мастерству",
            "K": "Создаю системы",
            "A": "Живу"
        }
    },
    {
        "level": "🏃 УРОВЕНЬ 2: ПОВЕДЕНИЕ",
        "text": "Как ты проводишь свободное время?",
        "options": {
            "6": "Жалуюсь, болею, страдаю",
            "7": "Дерусь, лечусь, учусь",
            "8": "Плету интриги",
            "9": "Отдыхаю по расписанию",
            "10": "Веду проекты",
            "J": "Тренируюсь, лечу, учу",
            "Q": "Передаю знания",
            "K": "Создаю новое",
            "A": "Просто есть"
        }
    },
    {
        "level": "💪 УРОВЕНЬ 3: СПОСОБНОСТИ",
        "text": "Что ты умеешь?",
        "options": {
            "6": "Терпеть, болеть, страдать",
            "7": "Драться, терпеть боль",
            "8": "Манипулировать",
            "9": "Работать по правилам",
            "10": "Вести людей",
            "J": "Воевать, лечить, учить",
            "Q": "Передавать мастерство",
            "K": "Создавать системы",
            "A": "Всё и ничего"
        }
    },
    {
        "level": "💪 УРОВЕНЬ 3: СПОСОБНОСТИ",
        "text": "Чему ты можешь научить?",
        "options": {
            "6": "Ничему. Я сам ничего не умею",
            "7": "Как драться, терпеть",
            "8": "Как манипулировать",
            "9": "Как работать по правилам",
            "10": "Как вести людей",
            "J": "Как быть воином, целителем",
            "Q": "Как стать мастером",
            "K": "Как создать новую систему",
            "A": "Как быть свободным"
        }
    },
    {
        "level": "🧠 УРОВЕНЬ 4: УБЕЖДЕНИЯ",
        "text": "Во что ты веришь?",
        "options": {
            "6": "Мир жесток. Я слабый",
            "7": "Надо драться, лечиться",
            "8": "Сила — это власть",
            "9": "Надо следовать правилам",
            "10": "Я могу вести людей",
            "J": "Я воин, целитель, учитель",
            "Q": "Я мастер. Я передаю знания",
            "K": "Я создаю новый мир",
            "A": "Всё — иллюзия"
        }
    },
    {
        "level": "🧠 УРОВЕНЬ 4: УБЕЖДЕНИЯ",
        "text": "Почему ты так живёшь?",
        "options": {
            "6": "Потому что я не могу иначе",
            "7": "Потому что надо выживать",
            "8": "Потому что так я контролирую",
            "9": "Потому что так правильно",
            "10": "Потому что люди идут за мной",
            "J": "Потому что это моя роль",
            "Q": "Потому что я передаю мастерство",
            "K": "Потому что я меняю мир",
            "A": "Потому что я свободен"
        }
    },
    {
        "level": "👤 УРОВЕНЬ 5: ИДЕНТИЧНОСТЬ",
        "text": "Кто ты?",
        "options": {
            "6": "Жертва, больной, дурак",
            "7": "Боец, борец",
            "8": "Манипулятор",
            "9": "Профессионал, эксперт",
            "10": "Лидер, мыслитель",
            "J": "Воин, целитель, учитель",
            "Q": "Мастер",
            "K": "Создатель, законодатель",
            "A": "Никто и все"
        }
    },
    {
        "level": "👤 УРОВЕНЬ 5: ИДЕНТИЧНОСТЬ",
        "text": "Как ты себя называешь?",
        "options": {
            "6": "Я неудачник, больной",
            "7": "Я боец, борец",
            "8": "Я игрок, кукловод",
            "9": "Я профессионал, эксперт",
            "10": "Я лидер, мыслитель",
            "J": "Я воин, целитель, учитель",
            "Q": "Я мастер",
            "K": "Я создатель",
            "A": "Я — это я"
        }
    },
    {
        "level": "🎯 УРОВЕНЬ 6: МИССИЯ",
        "text": "Зачем ты здесь?",
        "options": {
            "6": "Не знаю. Страдать?",
            "7": "Чтобы выжить",
            "8": "Чтобы контролировать",
            "9": "Чтобы работать",
            "10": "Чтобы вести людей",
            "J": "Чтобы защищать, лечить, учить",
            "Q": "Чтобы передавать мастерство",
            "K": "Чтобы создать новый мир",
            "A": "Чтобы быть"
        }
    },
    {
        "level": "🎯 УРОВЕНЬ 6: МИССИЯ",
        "text": "Что ты оставишь после себя?",
        "options": {
            "6": "Ничего",
            "7": "Следы борьбы",
            "8": "Интриги и манипуляции",
            "9": "Хорошо выполненную работу",
            "10": "Команду, проект",
            "J": "Учеников, пациентов",
            "Q": "Школу, систему обучения",
            "K": "Новую парадигму",
            "A": "Пример свободы"
        }
    }
]

# ========== ФУНКЦИИ ==========
def calculate_progress(current: int, total: int) -> str:
    """Вычисляет прогресс"""
    progress = int((current / total) * 100)
    filled = int(progress / 10)
    bar = "▓" * filled + "░" * (10 - filled)
    return f"{bar} {progress}%"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    welcome_text = (
        f"🃏 <b>ДОБРО ПОЖАЛОВАТЬ В КАРТОЧНЫЙ ТЕСТ АРХЕТИПОВ!</b>\n\n"
        f"Привет, {user.first_name}! 👋\n\n"
        f"Этот тест поможет тебе понять:\n"
        f"• <b>Кто ты</b> на самом деле\n"
        f"• <b>Почему</b> ты так живёшь\n"
        f"• <b>Что</b> тебя останавливает\n"
        f"• <b>Как</b> выйти на новый уровень\n\n"
        f"📊 <b>Структура теста:</b>\n\n"
        f"<b>ЭТАП 1: Определение программы (24 вопроса)</b>\n"
        f"• Блок 1: Детские раны (4 вопроса)\n"
        f"• Блок 2: Базовый страх (4 вопроса)\n"
        f"• Блок 3: Стратегия выживания (4 вопроса)\n"
        f"• Блок 4: Отношения (4 вопроса)\n"
        f"• Блок 5: Деньги и свобода (4 вопроса)\n"
        f"• Блок 6: Миссия (4 вопроса)\n\n"
        f"<b>ЭТАП 2: Определение уровня (12 вопросов)</b>\n"
        f"• 6 уровней по пирамиде Дилтса\n\n"
        f"⏱️ <b>Время прохождения:</b> 10-15 минут\n"
        f"🎯 <b>Результат:</b> Твой архетип + план роста\n\n"
        f"Готов узнать правду о себе?"
    )
    keyboard = [[InlineKeyboardButton("🚀 Начать тест", callback_data="start_test")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML")

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало теста"""
    query = update.callback_query
    await query.answer()
    context.user_data["stage_1_answers"] = {"СБ": 0, "ТФ": 0, "УБ": 0, "ЧВ": 0}
    context.user_data["stage_2_answers"] = {"6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "J": 0, "Q": 0, "K": 0, "A": 0}
    context.user_data["current_block"] = "block_1"
    context.user_data["current_question"] = 0
    
    block = STAGE_1_QUESTIONS["block_1"]
    intro_text = (
        f"{block['title']}\n\n"
        f"{block['description']}\n\n"
        f"Вопросов в блоке: 4\n"
        f"Всего вопросов в ЭТАПЕ 1: 24\n\n"
        f"Готов начать?"
    )
    keyboard = [[InlineKeyboardButton("▶️ Начать блок", callback_data="start_block_1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(intro_text, reply_markup=reply_markup)
    return STAGE_1_BLOCK_1

async def ask_stage_1_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Задаёт вопрос ЭТАПА 1"""
    query = update.callback_query
    await query.answer()
    
    current_block = context.user_data["current_block"]
    current_question = context.user_data["current_question"]
    block = STAGE_1_QUESTIONS[current_block]
    question = block["questions"][current_question]
    
    block_num = int(current_block.split("_")[1])
    total_done = (block_num - 1) * 4 + current_question
    progress = calculate_progress(total_done, 24)
    
    question_text = (
        f"{block['title']}\n\n"
        f"<b>Вопрос {current_question + 1}/4:</b>\n\n"
        f"{question['text']}\n\n"
        f"{progress}"
    )
    
    keyboard = []
    for program, answer in question["options"].items():
        keyboard.append([InlineKeyboardButton(answer, callback_data=f"stage1_{program}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(question_text, reply_markup=reply_markup, parse_mode="HTML")

async def handle_stage_1_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа ЭТАПА 1"""
    query = update.callback_query
    await query.answer()
    
    program = query.data.split("_")[1]
    context.user_data["stage_1_answers"][program] += 1
    context.user_data["current_question"] += 1
    
    current_block = context.user_data["current_block"]
    current_question = context.user_data["current_question"]
    block = STAGE_1_QUESTIONS[current_block]
    
    if current_question >= len(block["questions"]):
        return await finish_block(update, context)
    return await ask_stage_1_question(update, context)

async def finish_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение блока"""
    query = update.callback_query
    current_block = context.user_data["current_block"]
    block_num = int(current_block.split("_")[1])
    
    if block_num == 6:
        return await finish_stage_1(update, context)
    
    next_block = f"block_{block_num + 1}"
    context.user_data["current_block"] = next_block
    context.user_data["current_question"] = 0
    block = STAGE_1_QUESTIONS[next_block]
    
    completion_text = (
        f"✅ <b>БЛОК {block_num} ЗАВЕРШЁН!</b>\n\n"
        f"Переходим к следующему блоку:\n\n"
        f"{block['title']}\n\n"
        f"{block['description']}\n\n"
        f"Вопросов в блоке: 4"
    )
    keyboard = [[InlineKeyboardButton("▶️ Начать блок", callback_data=f"start_block_{block_num + 1}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(completion_text, reply_markup=reply_markup, parse_mode="HTML")
    return STAGE_1_BLOCK_1 + block_num

async def finish_stage_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение ЭТАПА 1"""
    query = update.callback_query
    answers = context.user_data["stage_1_answers"]
    program = max(answers, key=answers.get)
    
    program_names = {
        "СБ": "♠️ СИЛОВАЯ ПРОГРАММА",
        "ТФ": "♥️ ТЕЛЕСНАЯ ПРОГРАММА",
        "УБ": "♣️ ПОЗНАВАТЕЛЬНАЯ ПРОГРАММА",
        "ЧВ": "♦️ ЭМОЦИОНАЛЬНАЯ ПРОГРАММА"
    }
    program_desc = {
        "СБ": "Ты живёшь в мире силы. Хищник или жертва.",
        "ТФ": "Ты живёшь в теле. Здоровье или болезнь.",
        "УБ": "Ты живёшь в уме. Знание или незнание.",
        "ЧВ": "Ты живёшь в сердце. Любовь или нелюбовь."
    }
    context.user_data["program"] = program
    
    result_text = (
        f"🎉 <b>ЭТАП 1 ЗАВЕРШЁН!</b>\n\n"
        f"Твоя базовая программа:\n\n"
        f"<b>{program_names[program]}</b>\n\n"
        f"{program_desc[program]}\n\n"
        f"<b>Статистика ответов:</b>\n"
        f"♠️ Силовая: {answers['СБ']}/24\n"
        f"♥️ Телесная: {answers['ТФ']}/24\n"
        f"♣️ Познавательная: {answers['УБ']}/24\n"
        f"♦️ Эмоциональная: {answers['ЧВ']}/24\n\n"
        f"Теперь определим твой уровень развития.\n\n"
        f"<b>ЭТАП 2: Определение уровня (12 вопросов)</b>\n\n"
        f"Готов продолжить?"
    )
    keyboard = [[InlineKeyboardButton("▶️ Начать ЭТАП 2", callback_data="start_stage_2")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(result_text, reply_markup=reply_markup, parse_mode="HTML")
    return STAGE_2

async def start_stage_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало ЭТАПА 2"""
    query = update.callback_query
    await query.answer()
    context.user_data["current_question"] = 0
    return await ask_stage_2_question(update, context)

async def ask_stage_2_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Задаёт вопрос ЭТАПА 2"""
    query = update.callback_query
    await query.answer()
    
    current_question = context.user_data["current_question"]
    question = STAGE_2_QUESTIONS[current_question]
    progress = calculate_progress(current_question, 12)
    
    question_text = (
        f"{question['level']}\n\n"
        f"<b>Вопрос {current_question + 1}/12:</b>\n\n"
        f"{question['text']}\n\n"
        f"{progress}"
    )
    keyboard = []
    for level, answer in question["options"].items():
        keyboard.append([InlineKeyboardButton(answer, callback_data=f"stage2_{level}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(question_text, reply_markup=reply_markup, parse_mode="HTML")

async def handle_stage_2_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа ЭТАПА 2"""
    query = update.callback_query
    await query.answer()
    
    level = query.data.split("_")[1]
    context.user_data["stage_2_answers"][level] += 1
    context.user_data["current_question"] += 1
    current_question = context.user_data["current_question"]
    
    if current_question >= len(STAGE_2_QUESTIONS):
        return await show_result(update, context)
    return await ask_stage_2_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ результата"""
    query = update.callback_query
    program = context.user_data["program"]
    answers = context.user_data["stage_2_answers"]
    level = max(answers, key=answers.get)
    
    archetype_key = f"{program}-{level}"
    archetype = ARCHETYPES.get(archetype_key)
    
    if not archetype:
        await query.edit_message_text("Ошибка: архетип не найден")
        return ConversationHandler.END
    
    result_text = (
        f"🎉 <b>ТВОЙ АРХЕТИП ОПРЕДЕЛЁН!</b>\n\n"
        f"{archetype['card']} <b>{archetype['title']}</b>\n\n"
        f"<b>КТО ТЫ:</b>\n{archetype['who']}\n\n"
        f"<b>ТВОЙ НАРРАТИВ:</b>\n{archetype['narrative']}\n\n"
        f"<b>ТЕНЕВАЯ СТОРОНА:</b>\n{archetype['shadow']}\n\n"
        f"<b>ЛОВУШКА УРОВНЯ:</b>\n{archetype['trap']}\n\n"
        f"<b>ЧТО ДЕЛАТЬ:</b>\n{archetype['what_to_do']}\n\n"
        f"<b>КАК РАСТИ:</b>\n{archetype['how_to_grow']}\n\n"
        f"<b>ТРИГГЕР ПЕРЕХОДА:</b>\n{archetype['trigger']}\n\n"
        f"<b>ДЕНЬГИ:</b>\n{archetype['money']}\n\n"
        f"<b>ТВОЯ СКАЗКА:</b>\n{archetype['fairy_tale']}\n\n"
        f"📖 <b>Читать полное описание:</b>\n{archetype['link']}\n\n"
        f"💬 <b>Хочешь разобраться глубже?</b>\nНапиши автору: @ziksa"
    )
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти тест заново", callback_data="start_test")],
        [InlineKeyboardButton("💬 Написать автору", url="https://t.me/ziksa")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(result_text, reply_markup=reply_markup, parse_mode="HTML")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена теста"""
    await update.message.reply_text("Тест отменён. Напиши /start, чтобы начать заново.")
    return ConversationHandler.END

def main():
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(start_test, pattern="^start_test$")
        ],
        states={
            STAGE_1_BLOCK_1: [
                CallbackQueryHandler(ask_stage_1_question, pattern="^start_block_1$"),
                CallbackQueryHandler(handle_stage_1_answer, pattern="^stage1_")
            ],
            STAGE_1_BLOCK_2: [
                CallbackQueryHandler(ask_stage_1_question, pattern="^start_block_2$"),
                CallbackQueryHandler(handle_stage_1_answer, pattern="^stage1_")
            ],
            STAGE_1_BLOCK_3: [
                CallbackQueryHandler(ask_stage_1_question, pattern="^start_block_3$"),
                CallbackQueryHandler(handle_stage_1_answer, pattern="^stage1_")
            ],
            STAGE_1_BLOCK_4: [
                CallbackQueryHandler(ask_stage_1_question, pattern="^start_block_4$"),
                CallbackQueryHandler(handle_stage_1_answer, pattern="^stage1_")
            ],
            STAGE_1_BLOCK_5: [
                CallbackQueryHandler(ask_stage_1_question, pattern="^start_block_5$"),
                CallbackQueryHandler(handle_stage_1_answer, pattern="^stage1_")
            ],
            STAGE_1_BLOCK_6: [
                CallbackQueryHandler(ask_stage_1_question, pattern="^start_block_6$"),
                CallbackQueryHandler(handle_stage_1_answer, pattern="^stage1_")
            ],
            STAGE_2: [
                CallbackQueryHandler(start_stage_2, pattern="^start_stage_2$"),
                CallbackQueryHandler(handle_stage_2_answer, pattern="^stage2_")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(conv_handler)
    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()

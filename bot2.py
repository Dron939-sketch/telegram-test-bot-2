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

# ⚠️ ТОКЕН ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ ОШИБКА: Переменная TELEGRAM_BOT_TOKEN не установлена!")

# ========== СОСТОЯНИЯ ==========
STAGE_1_BLOCK_1 = 1  # Детские раны
STAGE_1_BLOCK_2 = 2  # Базовый страх
STAGE_1_BLOCK_3 = 3  # Стратегия выживания
STAGE_1_BLOCK_4 = 4  # Отношения
STAGE_1_BLOCK_5 = 5  # Деньги и свобода
STAGE_1_BLOCK_6 = 6  # Миссия
STAGE_2 = 7          # Этап 2: Определение уровня

# ========== ЭТАП 1: ВОПРОСЫ ПО БЛОКАМ (24 вопроса) ==========

STAGE_1_QUESTIONS = {
    # ========== БЛОК 1: ДЕТСКИЕ РАНЫ (4 вопроса) ==========
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
    
    # ========== БЛОК 2: БАЗОВЫЙ СТРАХ (4 вопроса) ==========
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
                    "УБ": "От сложных задач, от экзаменов, от ситуаций, где нужно думать",
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
    
    # ========== БЛОК 3: СТРАТЕГИЯ ВЫЖИВАНИЯ (4 вопроса) ==========
    "block_3": {
        "title": "🛡️ БЛОК 3: СТРАТЕГИЯ ВЫЖИВАНИЯ",
        "description": "Как ты защищаешься от страха?",
        "questions": [
            {
                "text": "Как ты справляешься с угрозой?",
                "options": {
                    "СБ": "Терплю, молчу или дерусь",
                    "ТФ": "Ухожу в болезнь, игнорирую тело",
                    "УБ": "Делаю вид, что всё понимаю, или избегаю ситуаций",
                    "ЧВ": "Ищу любовь, цепляюсь за отношения или избегаю их"
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
                    "ЧВ": "«Надо найти любовь» или «Надо полюбить себя»"
                }
            }
        ]
    },
    
    # ========== БЛОК 4: ОТНОШЕНИЯ (4 вопроса) ==========
    "block_4": {
        "title": "💔 БЛОК 4: ОТНОШЕНИЯ",
        "description": "Как ты строишь отношения с людьми?",
        "questions": [
            {
                "text": "Какие отношения у тебя чаще всего?",
                "options": {
                    "СБ": "Я подчиняюсь или доминирую",
                    "ТФ": "Я болею, меня жалеют или я забочусь о других",
                    "УБ": "Я учу или учусь",
                    "ЧВ": "Я люблю или меня любят"
                }
            },
            {
                "text": "Почему у тебя не складываются отношения?",
                "options": {
                    "СБ": "Я боюсь, что меня подавят, или я сам подавляю",
                    "ТФ": "Я болею, меня не хотят, или я не хочу больных",
                    "УБ": "Я слишком умный или слишком глупый",
                    "ЧВ": "Я боюсь, что меня бросят, или я сам бросаю"
                }
            },
            {
                "text": "Что ты ждёшь от партнёра?",
                "options": {
                    "СБ": "Чтобы он защитил меня или подчинился",
                    "ТФ": "Чтобы он позаботился о моём теле",
                    "УБ": "Чтобы он был умным или восхищался моим умом",
                    "ЧВ": "Чтобы он любил меня безусловно"
                }
            },
            {
                "text": "Почему ты расстаёшься?",
                "options": {
                    "СБ": "Он подавляет меня или я подавляю его",
                    "ТФ": "Он не заботится о моём теле или я устал заботиться",
                    "УБ": "Он не понимает меня или я не понимаю его",
                    "ЧВ": "Он разлюбил меня или я разлюбил его"
                }
            }
        ]
    },
    
    # ========== БЛОК 5: ДЕНЬГИ И СВОБОДА (4 вопроса) ==========
    "block_5": {
        "title": "💰 БЛОК 5: ДЕНЬГИ И СВОБОДА",
        "description": "Как ты зарабатываешь и тратишь деньги?",
        "questions": [
            {
                "text": "Как ты зарабатываешь деньги?",
                "options": {
                    "СБ": "Я терплю или дерусь за деньги",
                    "ТФ": "Я продаю своё тело (физический труд, внешность)",
                    "УБ": "Я продаю свои знания (консультации, обучение)",
                    "ЧВ": "Я продаю свои чувства (забота, любовь, эмпатия)"
                }
            },
            {
                "text": "На что ты тратишь деньги?",
                "options": {
                    "СБ": "На защиту (охрана, страховка, адвокаты)",
                    "ТФ": "На здоровье (врачи, спорт, еда)",
                    "УБ": "На обучение (курсы, книги, тренинги)",
                    "ЧВ": "На отношения (подарки, свидания, путешествия)"
                }
            },
            {
                "text": "Почему у тебя нет денег?",
                "options": {
                    "СБ": "Меня используют или я боюсь просить больше",
                    "ТФ": "Я болею или трачу всё на лечение",
                    "УБ": "Я не умею зарабатывать или боюсь продавать",
                    "ЧВ": "Я трачу всё на других или боюсь быть богатым"
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
    
    # ========== БЛОК 6: МИССИЯ (4 вопроса) ==========
    "block_6": {
        "title": "🎯 БЛОК 6: МИССИЯ",
        "description": "Зачем ты живёшь?",
        "questions": [
            {
                "text": "В чём смысл твоей жизни?",
                "options": {
                    "СБ": "Стать сильным, защитить слабых",
                    "ТФ": "Быть здоровым, помочь другим быть здоровыми",
                    "УБ": "Понять мир, научить других",
                    "ЧВ": "Любить и быть любимым"
                }
            },
            {
                "text": "Что ты хочешь оставить после себя?",
                "options": {
                    "СБ": "Систему справедливости, защиту слабых",
                    "ТФ": "Здоровое поколение, новую парадигму здоровья",
                    "УБ": "Знания, новую парадигму познания",
                    "ЧВ": "Любовь, новую парадигму отношений"
                }
            },
            {
                "text": "Кем ты хочешь стать?",
                "options": {
                    "СБ": "Воином, судьёй, законодателем",
                    "ТФ": "Целителем, мастером тела, создателем системы здоровья",
                    "УБ": "Учителем, мастером познания, создателем парадигмы",
                    "ЧВ": "Любящим, целителем сердец, создателем пространства любви"
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
    # ========== УРОВЕНЬ 1: ОКРУЖЕНИЕ (2 вопроса) ==========
    {
        "level": "🌍 УРОВЕНЬ 1: ОКРУЖЕНИЕ",
        "text": "Где ты живёшь?",
        "options": {
            "6": "В аду. Меня окружают враги/болезни/дураки/нелюбящие",
            "7": "В зоне боевых действий. Я постоянно дерусь",
            "8": "В джунглях. Я манипулирую, чтобы выжить",
            "9": "В системе. Я работаю по правилам",
            "10": "В команде. Я веду людей",
            "J": "На поле боя/в клинике/в школе. Я выполняю роль",
            "Q": "В мастерской. Я учу других",
            "K": "В своём мире. Я создаю правила",
            "A": "Везде и нигде. Я свободен"
        }
    },
    {
        "level": "🌍 УРОВЕНЬ 1: ОКРУЖЕНИЕ",
        "text": "Кто тебя окружает?",
        "options": {
            "6": "Враги, больные, дураки, нелюбящие",
            "7": "Конкуренты, противники",
            "8": "Жертвы моих манипуляций",
            "9": "Коллеги, начальники",
            "10": "Команда, последователи",
            "J": "Ученики, пациенты, подопечные",
            "Q": "Мастера и ученики",
            "K": "Создатели, идеологи",
            "A": "Все и никто"
        }
    },
    
    # ========== УРОВЕНЬ 2: ПОВЕДЕНИЕ (2 вопроса) ==========
    {
        "level": "🏃 УРОВЕНЬ 2: ПОВЕДЕНИЕ",
        "text": "Что ты делаешь каждый день?",
        "options": {
            "6": "Терплю, болею, тупею, страдаю",
            "7": "Дерусь, лечусь, спорю, ищу любовь",
            "8": "Манипулирую, интригую",
            "9": "Работаю по правилам",
            "10": "Веду команду",
            "J": "Выполняю роль (воин/целитель/учитель)",
            "Q": "Обучаю мастерству",
            "K": "Создаю системы",
            "A": "Живу"
        }
    },
    {
        "level": "🏃 УРОВЕНЬ 2: ПОВЕДЕНИЕ",
        "text": "Как ты проводишь свободное время?",
        "options": {
            "6": "Жалуюсь, болею, тупею, страдаю",
            "7": "Дерусь, лечусь, учусь, ищу любовь",
            "8": "Плету интриги",
            "9": "Отдыхаю по расписанию",
            "10": "Веду проекты",
            "J": "Тренируюсь, лечу, учу",
            "Q": "Передаю знания",
            "K": "Создаю новое",
            "A": "Просто есть"
        }
    },
    
    # ========== УРОВЕНЬ 3: СПОСОБНОСТИ (2 вопроса) ==========
    {
        "level": "💪 УРОВЕНЬ 3: СПОСОБНОСТИ",
        "text": "Что ты умеешь?",
        "options": {
            "6": "Терпеть, болеть, не понимать, страдать",
            "7": "Драться, терпеть боль, спорить, искать любовь",
            "8": "Манипулировать, интриговать",
            "9": "Работать по правилам",
            "10": "Вести людей",
            "J": "Воевать/лечить/учить безупречно",
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
            "7": "Как драться/терпеть/спорить",
            "8": "Как манипулировать",
            "9": "Как работать по правилам",
            "10": "Как вести людей",
            "J": "Как быть воином/целителем/учителем",
            "Q": "Как стать мастером",
            "K": "Как создать новую систему",
            "A": "Как быть свободным"
        }
    },
    
    # ========== УРОВЕНЬ 4: УБЕЖДЕНИЯ (2 вопроса) ==========
    {
        "level": "🧠 УРОВЕНЬ 4: УБЕЖДЕНИЯ",
        "text": "Во что ты веришь?",
        "options": {
            "6": "Мир жесток. Я слабый/больной/глупый/нелюбимый",
            "7": "Надо драться/лечиться/учиться/искать любовь",
            "8": "Сила/здоровье/знание/любовь — это власть",
            "9": "Надо следовать правилам",
            "10": "Я могу вести людей",
            "J": "Я воин/целитель/учитель. Это моя миссия",
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
            "8": "Потому что так я контролирую ситуацию",
            "9": "Потому что так правильно",
            "10": "Потому что люди идут за мной",
            "J": "Потому что это моя роль",
            "Q": "Потому что я передаю мастерство",
            "K": "Потому что я меняю мир",
            "A": "Потому что я свободен"
        }
    },
    
    # ========== УРОВЕНЬ 5: ИДЕНТИЧНОСТЬ (2 вопроса) ==========
    {
        "level": "👤 УРОВЕНЬ 5: ИДЕНТИЧНОСТЬ",
        "text": "Кто ты?",
        "options": {
            "6": "Жертва/больной/дурак/нелюбимый",
            "7": "Боец/борец с болью/спорщик/охотник за любовью",
            "8": "Манипулятор",
            "9": "Профессионал/зожник/эксперт/партнёр",
            "10": "Лидер/атлет/мыслитель/любящий",
            "J": "Воин/целитель/учитель",
            "Q": "Мастер",
            "K": "Создатель/законодатель",
            "A": "Никто и все"
        }
    },
    {
        "level": "👤 УРОВЕНЬ 5: ИДЕНТИЧНОСТЬ",
        "text": "Как ты себя называешь?",
        "options": {
            "6": "Я неудачник/больной/тупой/нелюбимый",
            "7": "Я боец/борец/спорщик/искатель",
            "8": "Я игрок/кукловод",
            "9": "Я профессионал/зожник/эксперт/партнёр",
            "10": "Я лидер/атлет/мыслитель/любящий",
            "J": "Я воин/целитель/учитель",
            "Q": "Я мастер",
            "K": "Я создатель",
            "A": "Я — это я"
        }
    },
    
    # ========== УРОВЕНЬ 6: МИССИЯ (2 вопроса) ==========
    {
        "level": "🎯 УРОВЕНЬ 6: МИССИЯ",
        "text": "Зачем ты здесь?",
        "options": {
            "6": "Не знаю. Страдать?",
            "7": "Чтобы выжить",
            "8": "Чтобы контролировать",
            "9": "Чтобы работать",
            "10": "Чтобы вести людей",
            "J": "Чтобы защищать/лечить/учить",
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

def calculate_progress(current_question: int, total_questions: int) -> str:
    """Вычисляет прогресс в процентах"""
    progress = int((current_question / total_questions) * 100)
    filled = int(progress / 10)
    bar = "▓" * filled + "░" * (10 - filled)
    return f"{bar} {progress}%"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    
    welcome_text = f"""
🃏 **ДОБРО ПОЖАЛОВАТЬ В КАРТОЧНЫЙ ТЕСТ АРХЕТИПОВ!**

Привет, {user.first_name}! 👋

Этот тест поможет тебе понять:
• **Кто ты** на самом деле
• **Почему** ты так живёшь
• **Что** тебя останавливает
• **Как** выйти на новый уровень

📊 **Структура теста:**

**ЭТАП 1: Определение программы (24 вопроса)**
• Блок 1: Детские раны (4 вопроса)
• Блок 2: Базовый страх (4 вопроса)
• Блок 3: Стратегия выживания (4 вопроса)
• Блок 4: Отношения (4 вопроса)
• Блок 5: Деньги и свобода (4 вопроса)
• Блок 6: Миссия (4 вопроса)

**ЭТАП 2: Определение уровня (12 вопросов)**
• 6 уровней по пирамиде Дилтса
• От окружения до миссии

⏱️ **Время прохождения:** 10-15 минут

🎯 **Результат:** Твой архетип + подробное описание + план роста

Готов узнать правду о себе?
"""
    
    keyboard = [[InlineKeyboardButton("🚀 Начать тест", callback_data="start_test")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало теста - БЛОК 1"""
    query = update.callback_query
    await query.answer()
    
    # Инициализация данных
    context.user_data["stage_1_answers"] = {"СБ": 0, "ТФ": 0, "УБ": 0, "ЧВ": 0}
    context.user_data["stage_2_answers"] = {"6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "J": 0, "Q": 0, "K": 0, "A": 0}
    context.user_data["current_block"] = "block_1"
    context.user_data["current_question"] = 0
    
    # Показываем описание БЛОКА 1
    block = STAGE_1_QUESTIONS["block_1"]
    intro_text = f"""
{block['title']}

{block['description']}

Вопросов в блоке: 4
Всего вопросов в ЭТАПЕ 1: 24

Готов начать?
"""
    
    keyboard = [[InlineKeyboardButton("▶️ Начать блок", callback_data="start_block_1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        intro_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return STAGE_1_BLOCK_1

async def ask_stage_1_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Задаёт вопрос из ЭТАПА 1"""
    query = update.callback_query
    await query.answer()
    
    current_block = context.user_data["current_block"]
    current_question = context.user_data["current_question"]
    
    block = STAGE_1_QUESTIONS[current_block]
    question = block["questions"][current_question]
    
    # Вычисляем общий прогресс
    block_num = int(current_block.split("_")[1])
    total_questions_done = (block_num - 1) * 4 + current_question
    progress = calculate_progress(total_questions_done, 24)
    
    question_text = f"""
{block['title']}

**Вопрос {current_question + 1}/4:**

{question['text']}

{progress}
"""
    
    # Создаём кнопки с вариантами ответов
    keyboard = []
    for program, answer in question["options"].items():
        keyboard.append([InlineKeyboardButton(
            answer,
            callback_data=f"stage1_{program}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        question_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_stage_1_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа ЭТАПА 1"""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем ответ
    program = query.data.split("_")[1]
    context.user_data["stage_1_answers"][program] += 1
    
    # Переходим к следующему вопросу
    context.user_data["current_question"] += 1
    current_block = context.user_data["current_block"]
    current_question = context.user_data["current_question"]
    
    block = STAGE_1_QUESTIONS[current_block]
    
    # Если блок закончен
    if current_question >= len(block["questions"]):
        return await finish_block(update, context)
    
    # Иначе задаём следующий вопрос
    return await ask_stage_1_question(update, context)

async def finish_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение блока"""
    query = update.callback_query
    
    current_block = context.user_data["current_block"]
    block_num = int(current_block.split("_")[1])
    
    # Если это последний блок ЭТАПА 1
    if block_num == 6:
        return await finish_stage_1(update, context)
    
    # Иначе переходим к следующему блоку
    next_block = f"block_{block_num + 1}"
    context.user_data["current_block"] = next_block
    context.user_data["current_question"] = 0
    
    block = STAGE_1_QUESTIONS[next_block]
    
    completion_text = f"""
✅ **БЛОК {block_num} ЗАВЕРШЁН!**

Переходим к следующему блоку:

{block['title']}

{block['description']}

Вопросов в блоке: 4
"""
    
    keyboard = [[InlineKeyboardButton("▶️ Начать блок", callback_data=f"start_block_{block_num + 1}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        completion_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    # Возвращаем состояние для следующего блока
    return STAGE_1_BLOCK_1 + block_num

async def finish_stage_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение ЭТАПА 1 и определение программы"""
    query = update.callback_query
    
    answers = context.user_data["stage_1_answers"]
    program = max(answers, key=answers.get)
    
    program_names = {
        "СБ": "♠️ СИЛОВАЯ ПРОГРАММА",
        "ТФ": "♥️ ТЕЛЕСНАЯ ПРОГРАММА",
        "УБ": "♣️ ПОЗНАВАТЕЛЬНАЯ ПРОГРАММА",
        "ЧВ": "♦️ ЭМОЦИОНАЛЬНАЯ ПРОГРАММА"
    }
    
    program_descriptions = {
        "СБ": "Ты живёшь в мире силы. Хищник или жертва. Твоя задача — научиться управлять силой.",
        "ТФ": "Ты живёшь в теле. Здоровье или болезнь. Твоя задача — научиться слушать тело.",
        "УБ": "Ты живёшь в уме. Знание или незнание. Твоя задача — научиться познавать.",
        "ЧВ": "Ты живёшь в сердце. Любовь или нелюбовь. Твоя задача — научиться любить."
    }
    
    context.user_data["program"] = program
    
    result_text = f"""
🎉 **ЭТАП 1 ЗАВЕРШЁН!**

Твоя базовая программа:

**{program_names[program]}**

{program_descriptions[program]}

---

**Статистика ответов:**
♠️ Силовая: {answers['СБ']}/24
♥️ Телесная: {answers['ТФ']}/24
♣️ Познавательная: {answers['УБ']}/24
♦️ Эмоциональная: {answers['ЧВ']}/24

---

Теперь определим твой уровень развития в этой программе.

**ЭТАП 2: Определение уровня (12 вопросов)**

Мы пройдём по 6 уровням пирамиды Дилтса:
1. Окружение
2. Поведение
3. Способности
4. Убеждения
5. Идентичность
6. Миссия

Готов продолжить?
"""
    
    keyboard = [[InlineKeyboardButton("▶️ Начать ЭТАП 2", callback_data="start_stage_2")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        result_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return STAGE_2

async def start_stage_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало ЭТАПА 2"""
    query = update.callback_query
    await query.answer()
    
    context.user_data["current_question"] = 0
    
    return await ask_stage_2_question(update, context)

async def ask_stage_2_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Задаёт вопрос из ЭТАПА 2"""
    query = update.callback_query
    await query.answer()
    
    current_question = context.user_data["current_question"]
    question = STAGE_2_QUESTIONS[current_question]
    
    progress = calculate_progress(current_question, 12)
    
    question_text = f"""
{question['level']}

**Вопрос {current_question + 1}/12:**

{question['text']}

{progress}
"""
    
    # Создаём кнопки с вариантами ответов
    keyboard = []
    for level, answer in question["options"].items():
        keyboard.append([InlineKeyboardButton(
            answer,
            callback_data=f"stage2_{level}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        question_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_stage_2_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа ЭТАПА 2"""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем ответ
    level = query.data.split("_")[1]
    context.user_data["stage_2_answers"][level] += 1
    
    # Переходим к следующему вопросу
    context.user_data["current_question"] += 1
    current_question = context.user_data["current_question"]
    
    # Если тест закончен
    if current_question >= len(STAGE_2_QUESTIONS):
        return await show_result(update, context)
    
    # Иначе задаём следующий вопрос
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
    
    result_text = f"""
🎉 **ТВОЙ АРХЕТИП ОПРЕДЕЛЁН!**

{archetype['card']} **{archetype['title']}**

---

**КТО ТЫ:**
{archetype['who']}

---

**ТВОЙ НАРРАТИВ:**
{archetype['narrative']}

---

**ТЕНЕВАЯ СТОРОНА:**
{archetype['shadow']}

---

**ЛОВУШКА УРОВНЯ:**
{archetype['trap']}

---

**ЧТО ДЕЛАТЬ:**
{archetype['what_to_do']}

---

**КАК РАСТИ:**
{archetype['how_to_grow']}

---

**ТРИГГЕР ПЕРЕХОДА:**
{archetype['trigger']}

---

**ДЕНЬГИ:**
{archetype['money']}

---

**ТВОЯ СКАЗКА:**
{archetype['fairy_tale']}

---

📖 **Читать полное описание:**
{archetype['link']}

---

💬 **Хочешь разобраться глубже?**
Напиши автору: @ziksa
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти тест заново", callback_data="start_test")],
        [InlineKeyboardButton("💬 Написать автору", url="https://t.me/ziksa")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        result_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена теста"""
    await update.message.reply_text("Тест отменён. Напиши /start, чтобы начать заново.")
    return ConversationHandler.END

def main():
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    
    # Обработчик разговора
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

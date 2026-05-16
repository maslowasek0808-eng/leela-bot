import os
import random
import json
import asyncio
from datetime import datetime
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ══════════════════════════════════════════════
#  КОНФИГУРАЦИЯ
# ══════════════════════════════════════════════

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ══════════════════════════════════════════════
#  72 КЛЕТКИ ЛИЛЫ
# ══════════════════════════════════════════════

CELLS = {
    1:  {"name": "Рождение", "desc": "Начало пути. Момент появления в мире — чистый, без суждений. Всё возможно."},
    2:  {"name": "Иллюзия", "desc": "Майя. То, что кажется реальным, но скрывает глубинную природу вещей."},
    3:  {"name": "Гнев", "desc": "Огонь внутри. Энергия, которая может разрушать или очищать — зависит от осознанности."},
    4:  {"name": "Жадность", "desc": "Цепляние за большее. Страх, что того, что есть, недостаточно."},
    5:  {"name": "Гордость", "desc": "Отождествление с достижениями. Тонкая преграда между уверенностью и высокомерием."},
    6:  {"name": "Земля", "desc": "Притхви. Стабильность, опора, заземление. То, на что можно встать."},
    7:  {"name": "Обман", "desc": "Ложь себе или другим. Место, где правда скрыта за удобным объяснением."},
    8:  {"name": "Воздух", "desc": "Движение, перемены, свежесть. Состояние лёгкости и открытости к новому."},
    9:  {"name": "Огонь", "desc": "Трансформация. То, что сжигает старое, чтобы освободить место для нового."},
    10: {"name": "Вода", "desc": "Поток, адаптация, очищение. Способность принять форму любого сосуда."},
    11: {"name": "Доброта", "desc": "Тепло без условий. Действие из сердца, не из расчёта."},
    12: {"name": "Знание", "desc": "Информация, ставшая пониманием. Разница между знать и чувствовать."},
    13: {"name": "Тщеславие", "desc": "Игра для внешней аудитории. Жизнь напоказ, а не изнутри."},
    14: {"name": "Небеса", "desc": "Состояние лёгкости и блаженства. Временная остановка в покое."},
    15: {"name": "Убийство", "desc": "Разрушение чего-то живого — идеи, отношения, части себя. Иногда необходимое."},
    16: {"name": "Жестокость", "desc": "Действие без сострадания. Место, где нечувствительность стала нормой."},
    17: {"name": "Великодушие", "desc": "Отдавать больше, чем требуется. Открытость сердца без счёта."},
    18: {"name": "Доступность", "desc": "Быть открытым. Позволять жизни и людям приходить без защитных стен."},
    19: {"name": "Вера", "desc": "Опора без видимых доказательств. Доверие процессу, который больше тебя."},
    20: {"name": "Эго-план", "desc": "Жизнь по сценарию ума. Планы, которые защищают от неизвестного."},
    21: {"name": "Враждебность", "desc": "Закрытость и сопротивление. Мир воспринимается как угроза."},
    22: {"name": "Равновесие", "desc": "Устойчивость среди движения. Не безразличие, а внутренняя тишина."},
    23: {"name": "Раскаяние", "desc": "Честный взгляд назад. Не самобичевание, а признание и отпускание."},
    24: {"name": "Чистилище", "desc": "Переходное состояние. Ни там, ни здесь — но движение происходит."},
    25: {"name": "Змея тщеславия", "desc": "Падение с высоты самомнения. Урок о настоящей ценности."},
    26: {"name": "Безрассудство", "desc": "Действие без осознанности. Импульс, который опережает понимание."},
    27: {"name": "Мудрость", "desc": "Понимание, которое пришло через опыт, а не через книги."},
    28: {"name": "Зависть", "desc": "Боль от чужого счастья. Сигнал о том, чего хочется, но страшно признать."},
    29: {"name": "Беспечность", "desc": "Лёгкость бытия. Способность не цепляться за результат."},
    30: {"name": "Очарование", "desc": "Состояние влюблённости в жизнь. Когда мир снова становится волшебным."},
    31: {"name": "Прощение", "desc": "Освобождение от груза обиды — в первую очередь для себя."},
    32: {"name": "Скупость", "desc": "Страх отдавать. Убеждение, что ресурса не хватит на всех."},
    33: {"name": "Благодать", "desc": "Состояние, которое нельзя заработать. Оно просто приходит."},
    34: {"name": "Реальность", "desc": "Вещи такими, какие они есть — без прикрас и без страха."},
    35: {"name": "Дурные намерения", "desc": "Действие из тени. Место, где мотив скрыт даже от себя."},
    36: {"name": "Сострадание", "desc": "Чувствовать боль другого, не растворяясь в ней. Быть рядом."},
    37: {"name": "Щедрость", "desc": "Отдавать не из избытка, а из доверия. Знание, что вернётся."},
    38: {"name": "Самопознание", "desc": "Путешествие внутрь. Вопрос: кто я на самом деле?"},
    39: {"name": "Импульсивность", "desc": "Реакция вместо ответа. Тело действует раньше, чем успевает осознать."},
    40: {"name": "Щедрость духа", "desc": "Делиться не вещами, а вниманием, временем, присутствием."},
    41: {"name": "Очищение", "desc": "Отпускание того, что уже отжило. Пространство для нового."},
    42: {"name": "Знание принципов", "desc": "Понимание законов, по которым устроен мир и ты сам."},
    43: {"name": "Ясность", "desc": "Момент, когда туман рассеивается. Всё становится просто и очевидно."},
    44: {"name": "Потакание себе", "desc": "Избегание дискомфорта любой ценой. Комфорт как ловушка."},
    45: {"name": "Неуместность", "desc": "Ощущение, что не на своём месте. Приглашение найти своё."},
    46: {"name": "Правило", "desc": "Структура, которая помогает или ограничивает — зависит от осознанности."},
    47: {"name": "Высшая сила", "desc": "Соприкосновение с тем, что больше личного «я». Смирение как сила."},
    48: {"name": "Совесть", "desc": "Внутренний голос, который знает правду. Слышать его — уже смелость."},
    49: {"name": "Непостоянство", "desc": "Всё меняется. Цепляться — значит страдать. Отпускать — значит течь."},
    50: {"name": "Самовластие", "desc": "Ответственность за свою жизнь. Никто другой не сделает это за тебя."},
    51: {"name": "Астральный план", "desc": "Пространство между мирами. Интуиция, сны, предчувствия."},
    52: {"name": "Нейтралитет", "desc": "Наблюдать без суждения. Пространство до оценки."},
    53: {"name": "Энергия", "desc": "Жизненная сила. Откуда она приходит и куда уходит в вашей жизни."},
    54: {"name": "Хаос", "desc": "Порядок, который ещё не проявился. Место рождения нового."},
    55: {"name": "Земной план", "desc": "Повседневная реальность. Тело, деньги, отношения, работа."},
    56: {"name": "Зависть духа", "desc": "Желание чужого пути. Забывание о своём уникальном маршруте."},
    57: {"name": "Милость", "desc": "Получать не то, что заработал, а то, что нужно. Принять это."},
    58: {"name": "Единство", "desc": "Ощущение связи со всем. Граница между «я» и «мир» становится прозрачной."},
    59: {"name": "Откровение", "desc": "Внезапное понимание. Пазл складывается. Что-то проясняется навсегда."},
    60: {"name": "Духовный план", "desc": "Измерение смысла. Вопрос: зачем всё это?"},
    61: {"name": "Блаженство", "desc": "Полнота без причины. Счастье, которое не зависит от обстоятельств."},
    62: {"name": "Высшее знание", "desc": "Понимание, которое невозможно объяснить словами — только прожить."},
    63: {"name": "Карма", "desc": "Причинно-следственная связь. То, что посеяно — прорастает."},
    64: {"name": "Трансцендентность", "desc": "Выход за пределы привычного «я». Кратковременная свобода от роли."},
    65: {"name": "Преданность", "desc": "Верность пути даже когда непонятно зачем. Доверие процессу."},
    66: {"name": "Космическое сознание", "desc": "Всё есть одно. Разделение — иллюзия. Редкое состояние единства."},
    67: {"name": "Абсолют", "desc": "За пределами всех пар противоположностей. Тишина за шумом."},
    68: {"name": "Освобождение", "desc": "Мокша. Конец игры. Не победа над чем-то — растворение в понимании."},
    69: {"name": "Земля (возврат)", "desc": "После высоты — возвращение к основам. Интеграция опыта в обычную жизнь."},
    70: {"name": "Ум", "desc": "Инструмент познания. Слуга или господин — зависит от осознанности."},
    71: {"name": "Сознание", "desc": "То, что наблюдает за умом. Свидетель всего происходящего."},
    72: {"name": "Чистое бытие", "desc": "Существование до мысли. Просто быть — без добавлений."},
}

# Змеи: с какой клетки → на какую опускают
SNAKES = {
    17: 7, 54: 19, 62: 42, 64: 2, 92: 51  # классическая Лила
}
# Только те змеи, чьи клетки есть в нашем поле 1-72
SNAKES = {k: v for k, v in SNAKES.items() if k <= 72 and v <= 72}
SNAKES.update({17: 7, 54: 19, 62: 42})

# Стрелы: с какой клетки → на какую поднимают
ARROWS = {
    6: 28, 14: 47, 22: 60, 36: 55, 52: 72
}
ARROWS = {k: v for k, v in ARROWS.items() if k <= 72 and v <= 72}

# ══════════════════════════════════════════════
#  ХРАНИЛИЩЕ (в памяти, для простоты)
# ══════════════════════════════════════════════

# sessions[user_id] = {
#   "state": str,
#   "query": str,
#   "readiness": float,
#   "cell": int,
#   "path": [int],
#   "insights": [str],
#   "events": [str],
#   "roll_count": int,
# }
sessions = {}

def get_session(user_id):
    if user_id not in sessions:
        sessions[user_id] = {
            "state": "idle",
            "query": "",
            "readiness": 0.5,
            "cell": 0,
            "path": [],
            "insights": [],
            "events": [],
            "roll_count": 0,
        }
    return sessions[user_id]

# ══════════════════════════════════════════════
#  CLAUDE API
# ══════════════════════════════════════════════

async def call_claude(prompt: str, system: str = "") -> str:
    if not ANTHROPIC_API_KEY:
        return "[Ключ API не настроен]"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 600,
                "system": system or "Ты мудрый проводник трансформационной игры Лила. Отвечай по-русски, тихо и внимательно. Без пафоса.",
                "messages": [{"role": "user", "content": prompt}],
            }
        )
        data = resp.json()
        return data["content"][0]["text"]

async def analyze_query(query: str) -> float:
    """Скрытый анализ запроса. Возвращает коэффициент готовности 0.0–1.0"""
    prompt = f"""Оцени запрос игрока по 5 критериям от 0 до 1:
1. specificity — конкретность вопроса
2. depth — есть ли внутренний слой за симптомом
3. emotionality — эмоциональная вовлечённость
4. responsibility — игрок видит себя частью ситуации
5. awareness — осознание, что ответ внутри

Запрос: «{query}»

Верни ТОЛЬКО JSON без пояснений:
{{"specificity":0.5,"depth":0.5,"emotionality":0.5,"responsibility":0.5,"awareness":0.5}}"""

    try:
        result = await call_claude(prompt, "Отвечай только JSON, без лишних слов.")
        # Извлекаем JSON из ответа
        start = result.find("{")
        end = result.rfind("}") + 1
        scores = json.loads(result[start:end])
        weights = {"specificity": 0.15, "depth": 0.25,
                   "emotionality": 0.20, "responsibility": 0.25, "awareness": 0.15}
        return min(1.0, max(0.0, sum(scores.get(k, 0.5) * w for k, w in weights.items())))
    except Exception:
        return 0.5

async def reflect_query(query: str) -> str:
    prompt = f"""Игрок написал запрос для входа в трансформационную игру Лила:
«{query}»

Напиши одно тёплое предложение — отрази суть запроса, не оценивая.
Начни с «Я слышу» или «Похоже» или «Кажется».
Максимум 2 предложения. Никаких советов."""
    return await call_claude(prompt)

async def generate_cell_text(cell_number: int, query: str) -> str:
    cell = CELLS.get(cell_number, {"name": "Неизвестная клетка", "desc": ""})
    prompt = f"""Ты проводник в игре Лила. Игрок попал на клетку.

Клетка {cell_number} — «{cell["name"]}»
Суть клетки: {cell["desc"]}
Запрос игрока: «{query}»

Напиши текст из 3 частей (без заголовков, единым потоком):
1. Смысл клетки — 2 предложения, суть состояния
2. Связь с запросом — 1 предложение как это касается их вопроса
3. Вопрос — один открытый вопрос для размышления

Тон: тихий, внимательный. Не используй слово «путь». Максимум 120 слов."""
    return await call_claude(prompt)

async def explain_simpler(cell_number: int, query: str) -> str:
    cell = CELLS.get(cell_number, {"name": "?", "desc": ""})
    prompt = f"""Объясни клетку {cell_number} «{cell["name"]}» простыми словами.
Контекст запроса игрока: «{query}»
Начни с «Если совсем просто...»
Максимум 60 слов. Один конкретный пример из обычной жизни."""
    return await call_claude(prompt)

async def generate_help_response(cell_number: int, query: str, chosen_theme: str) -> str:
    cell = CELLS.get(cell_number, {"name": "?", "desc": ""})
    prompt = f"""Игрок не понял клетку {cell_number} «{cell["name"]}».
Он сказал, что тема «{chosen_theme}» ближе к его состоянию.
Запрос: «{query}»

Объясни клетку через эту тему применительно к их запросу.
Максимум 80 слов. Без абстракций — только конкретно про их ситуацию."""
    return await call_claude(prompt)

async def generate_final_summary(query: str, path: list, insights: list) -> str:
    path_str = " → ".join(str(c) for c in path)
    insights_str = "\n".join(f"- {i}" for i in insights) if insights else "Мыслей не записано"
    prompt = f"""Игрок завершил трансформационную игру Лила.

Начальный запрос: «{query}»
Путь по клеткам: {path_str}
Записанные мысли:
{insights_str}

Напиши итоговое послание:
1. Что прожил игрок на этом пути — 2 предложения
2. Что могло стать яснее — 1 предложение
3. Вопрос для следующего шага — 1 вопрос

Тон: тёплый, без пафоса. Максимум 100 слов."""
    return await call_claude(prompt)

# ══════════════════════════════════════════════
#  КУБИК
# ══════════════════════════════════════════════

def weighted_roll(readiness: float) -> int:
    """Шестёрка выпадает с вероятностью 17%–50% в зависимости от готовности"""
    p6 = 0.167 + readiness * 0.333
    if random.random() < p6:
        return 6
    return random.randint(1, 5)

def game_roll() -> int:
    return random.randint(1, 6)

ADMISSION_COMMENTS = {
    1: "Ваш запрос услышан. Но игра предлагает посмотреть совсем в другую сторону. Возможно, настоящий вопрос пока скрыт.",
    2: "Кажется, здесь есть ещё что-то важное. Попробуйте копнуть глубже.",
    3: "Уже появляется направление. Переформулируйте — вы близко.",
    4: "Ваш запрос становится яснее. Ещё чуть-чуть.",
    5: "Вы очень близко. Одно последнее уточнение.",
}

# ══════════════════════════════════════════════
#  КЛАВИАТУРЫ
# ══════════════════════════════════════════════

def kb_roll_admission():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🎲 Бросить кубик", callback_data="admission_roll")
    ]])

def kb_cell():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Продолжить путь", callback_data="continue")],
        [
            InlineKeyboardButton("💬 Объяснить проще", callback_data="simpler"),
            InlineKeyboardButton("✏️ Записать мысль", callback_data="insight"),
        ],
        [InlineKeyboardButton("❓ Не понимаю", callback_data="help")],
    ])

def kb_roll_game():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🎲 Бросить кубик", callback_data="game_roll")
    ]])

def kb_help_themes():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("😨 Страх", callback_data="help_страх"),
            InlineKeyboardButton("🔀 Выбор", callback_data="help_выбор"),
        ],
        [
            InlineKeyboardButton("💞 Отношения", callback_data="help_отношения"),
            InlineKeyboardButton("🤔 Неуверенность", callback_data="help_неуверенность"),
        ],
        [InlineKeyboardButton("✨ Что-то другое", callback_data="help_другое")],
    ])

# ══════════════════════════════════════════════
#  HANDLERS
# ══════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sessions[user_id] = {
        "state": "query_input",
        "query": "",
        "readiness": 0.5,
        "cell": 0,
        "path": [],
        "insights": [],
        "events": [],
        "roll_count": 0,
    }
    await update.message.reply_text(
        "✨ Добро пожаловать в игру Лила.\n\n"
        "Это путешествие по 72 состояниям человеческого опыта. "
        "Игра не даёт ответов — она помогает прожить вопрос.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "Перед началом путешествия сформулируйте запрос, "
        "с которым вы хотите войти в игру.\n\n"
        "Примеры:\n"
        "— Почему я боюсь менять работу?\n"
        "— Что мешает мне строить отношения?\n"
        "— Как мне выйти на новый уровень?\n\n"
        "Напишите свой запрос:"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    text = update.message.text.strip()

    if session["state"] == "query_input":
        await update.message.reply_text("⏳ Принимаю ваш запрос...")

        # Скрытый анализ
        readiness = await analyze_query(text)
        session["query"] = text
        session["readiness"] = readiness

        # Отражение
        reflection = await reflect_query(text)
        await update.message.reply_text(reflection)

        await asyncio.sleep(1)
        await update.message.reply_text(
            "Пространство готово встретить ваш запрос.\n\n"
            "Бросьте кубик — и узнайте, готово ли оно принять именно его.",
            reply_markup=kb_roll_admission()
        )
        session["state"] = "admission_roll"

    elif session["state"] == "insight_input":
        session["insights"].append(text)
        session["events"].append(f"💡 Мысль на клетке {session['cell']}: {text}")
        await update.message.reply_text(
            "✏️ Мысль записана. Она останется в вашей истории пути.\n\n"
            "Продолжайте:",
            reply_markup=kb_cell()
        )
        session["state"] = "cell_view"

    else:
        await update.message.reply_text(
            "Нажмите кнопку ниже, чтобы продолжить игру.",
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = get_session(user_id)
    data = query.data

    # ── БРОСОК ДОПУСКА ──
    if data == "admission_roll":
        roll = weighted_roll(session["readiness"])
        session["roll_count"] += 1

        if roll == 6:
            await query.message.reply_text(
                f"🎲 Выпало: 6\n\n"
                f"Запрос услышан.\nВаш путь начинается.\n\n"
                f"━━━━━━━━━━━━━━"
            )
            await asyncio.sleep(1)
            await enter_cell(query.message, session, 6)
        else:
            comment = ADMISSION_COMMENTS[roll]
            await query.message.reply_text(
                f"🎲 Выпало: {roll}\n\n{comment}\n\n"
                f"Попробуйте переформулировать запрос — и снова бросьте кубик.\n\n"
                f"Напишите новый вариант:"
            )
            session["state"] = "query_input"

    # ── ПРОДОЛЖИТЬ (БРОСОК В ИГРЕ) ──
    elif data == "continue":
        await query.message.reply_text(
            "🎲 Бросьте кубик, чтобы сделать следующий ход:",
            reply_markup=kb_roll_game()
        )
        session["state"] = "game_roll"

    # ── БРОСОК В ИГРЕ ──
    elif data == "game_roll":
        roll = game_roll()
        current = session["cell"]
        new_cell = current + roll

        if new_cell > 72:
            new_cell = 72  # не выходим за поле

        await query.message.reply_text(
            f"🎲 Выпало: {roll}\n"
            f"Клетка {current} → {new_cell}"
        )
        await asyncio.sleep(1)
        await enter_cell(query.message, session, new_cell)

    # ── ОБЪЯСНИТЬ ПРОЩЕ ──
    elif data == "simpler":
        await query.message.reply_text("⏳ Ищу более простые слова...")
        text = await explain_simpler(session["cell"], session["query"])
        await query.message.reply_text(
            f"💬 {text}\n\n━━━━━━━━━━━━━━",
            reply_markup=kb_cell()
        )

    # ── ЗАПИСАТЬ МЫСЛЬ ──
    elif data == "insight":
        await query.message.reply_text(
            "✏️ Напишите вашу мысль или инсайт — я сохраню его в истории пути:"
        )
        session["state"] = "insight_input"

    # ── НЕ ПОНИМАЮ ──
    elif data == "help":
        await query.message.reply_text(
            "Давайте попробуем иначе.\n\nЧто сейчас ближе к вашему состоянию?",
            reply_markup=kb_help_themes()
        )

    # ── ПОМОЩЬ ПО ТЕМЕ ──
    elif data.startswith("help_"):
        theme = data.replace("help_", "")
        await query.message.reply_text("⏳ Подбираю объяснение...")
        text = await generate_help_response(session["cell"], session["query"], theme)
        await query.message.reply_text(
            f"{text}\n\n━━━━━━━━━━━━━━",
            reply_markup=kb_cell()
        )
        session["state"] = "cell_view"


# ══════════════════════════════════════════════
#  ВХОД НА КЛЕТКУ
# ══════════════════════════════════════════════

async def enter_cell(message, session: dict, cell_number: int):
    cell = CELLS.get(cell_number, {"name": "Неизвестная клетка", "desc": ""})
    event_prefix = ""

    # Проверка змей
    if cell_number in SNAKES:
        snake_to = SNAKES[cell_number]
        event_prefix = (
            f"🐍 Здесь живёт змея.\n\n"
            f"Игра возвращает вас к чему-то важному.\n"
            f"Иногда то, что казалось пройденным, просит ещё одного взгляда.\n\n"
            f"Вы переходите с {cell_number} на {snake_to}.\n\n━━━━━━━━━━━━━━\n\n"
        )
        session["events"].append(f"🐍 Змея: {cell_number} → {snake_to}")
        cell_number = snake_to
        cell = CELLS.get(cell_number, {"name": "?", "desc": ""})

    # Проверка стрел
    elif cell_number in ARROWS:
        arrow_to = ARROWS[cell_number]
        event_prefix = (
            f"✨ Стрела!\n\n"
            f"Вы увидели что-то важное — и движетесь вперёд.\n\n"
            f"Вы переходите с {cell_number} на {arrow_to}.\n\n━━━━━━━━━━━━━━\n\n"
        )
        session["events"].append(f"✨ Стрела: {cell_number} → {arrow_to}")
        cell_number = arrow_to
        cell = CELLS.get(cell_number, {"name": "?", "desc": ""})

    session["cell"] = cell_number
    session["path"].append(cell_number)

    # Финал
    if cell_number == 68:
        await finish_game(message, session)
        return

    # Генерация текста клетки
    await message.reply_text("⏳ Проводник думает...")
    cell_text = await generate_cell_text(cell_number, session["query"])

    header = f"{'━'*14}\n🎯 Клетка {cell_number} — «{cell['name']}»\n{'━'*14}\n\n"

    await message.reply_text(
        event_prefix + header + cell_text,
        reply_markup=kb_cell()
    )
    session["state"] = "cell_view"


# ══════════════════════════════════════════════
#  ФИНАЛ
# ══════════════════════════════════════════════

async def finish_game(message, session: dict):
    await message.reply_text("⏳ Подготавливаю итог вашего пути...")

    summary = await generate_final_summary(
        session["query"],
        session["path"],
        session["insights"]
    )

    path_str = " → ".join(str(c) for c in session["path"])

    await message.reply_text(
        f"🏁 Вы завершили путь.\n\n"
        f"{'━'*14}\n"
        f"Ваш запрос в начале:\n«{session['query']}»\n\n"
        f"Ваш путь:\n{path_str}\n"
        f"{'━'*14}\n\n"
        f"{summary}\n\n"
        f"{'━'*14}\n\n"
        f"Что стало понятнее?\n"
        f"Что изменилось?\n"
        f"Какой шаг вы сделаете дальше?\n\n"
        f"{'━'*14}\n\n"
        f"_Ответ был не найден._\n"
        f"_Он был прожит._"
    )

    # Сбросить сессию
    session["state"] = "idle"
    await message.reply_text(
        "Чтобы начать новую игру, напишите /start"
    )


# ══════════════════════════════════════════════
#  ЗАПУСК
# ══════════════════════════════════════════════

def main():
    if not BOT_TOKEN:
        print("❌ Ошибка: переменная BOT_TOKEN не задана!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот Лила запущен!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

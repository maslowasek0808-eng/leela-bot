import os
import random
import json
import asyncio
import httpx
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

bot = telebot.TeleBot(BOT_TOKEN)

CELLS = {
    1:  {"name": "Рождение", "desc": "Начало пути. Момент появления в мире — чистый, без суждений. Всё возможно."},
    2:  {"name": "Иллюзия", "desc": "Майя. То, что кажется реальным, но скрывает глубинную природу вещей."},
    3:  {"name": "Гнев", "desc": "Огонь внутри. Энергия, которая может разрушать или очищать."},
    4:  {"name": "Жадность", "desc": "Цепляние за большее. Страх, что того, что есть, недостаточно."},
    5:  {"name": "Гордость", "desc": "Отождествление с достижениями. Преграда между уверенностью и высокомерием."},
    6:  {"name": "Земля", "desc": "Притхви. Стабильность, опора, заземление. То, на что можно встать."},
    7:  {"name": "Обман", "desc": "Ложь себе или другим. Место, где правда скрыта за удобным объяснением."},
    8:  {"name": "Воздух", "desc": "Движение, перемены, свежесть. Лёгкость и открытость к новому."},
    9:  {"name": "Огонь", "desc": "Трансформация. То, что сжигает старое, чтобы освободить место для нового."},
    10: {"name": "Вода", "desc": "Поток, адаптация, очищение. Способность принять форму любого сосуда."},
    11: {"name": "Доброта", "desc": "Тепло без условий. Действие из сердца, не из расчёта."},
    12: {"name": "Знание", "desc": "Информация, ставшая пониманием. Разница между знать и чувствовать."},
    13: {"name": "Тщеславие", "desc": "Игра для внешней аудитории. Жизнь напоказ, а не изнутри."},
    14: {"name": "Небеса", "desc": "Состояние лёгкости и блаженства. Временная остановка в покое."},
    15: {"name": "Убийство", "desc": "Разрушение чего-то живого — идеи, отношения, части себя."},
    16: {"name": "Жестокость", "desc": "Действие без сострадания. Нечувствительность стала нормой."},
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
    35: {"name": "Дурные намерения", "desc": "Действие из тени. Мотив скрыт даже от себя."},
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
    47: {"name": "Высшая сила", "desc": "Соприкосновение с тем, что больше личного я. Смирение как сила."},
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
    58: {"name": "Единство", "desc": "Ощущение связи со всем. Граница между я и мир становится прозрачной."},
    59: {"name": "Откровение", "desc": "Внезапное понимание. Пазл складывается. Что-то проясняется навсегда."},
    60: {"name": "Духовный план", "desc": "Измерение смысла. Вопрос: зачем всё это?"},
    61: {"name": "Блаженство", "desc": "Полнота без причины. Счастье, которое не зависит от обстоятельств."},
    62: {"name": "Высшее знание", "desc": "Понимание, которое невозможно объяснить словами — только прожить."},
    63: {"name": "Карма", "desc": "Причинно-следственная связь. То, что посеяно — прорастает."},
    64: {"name": "Трансцендентность", "desc": "Выход за пределы привычного я. Кратковременная свобода от роли."},
    65: {"name": "Преданность", "desc": "Верность пути даже когда непонятно зачем. Доверие процессу."},
    66: {"name": "Космическое сознание", "desc": "Всё есть одно. Разделение — иллюзия. Редкое состояние единства."},
    67: {"name": "Абсолют", "desc": "За пределами всех пар противоположностей. Тишина за шумом."},
    68: {"name": "Освобождение", "desc": "Мокша. Конец игры. Не победа над чем-то — растворение в понимании."},
    69: {"name": "Земля (возврат)", "desc": "После высоты — возвращение к основам. Интеграция опыта в обычную жизнь."},
    70: {"name": "Ум", "desc": "Инструмент познания. Слуга или господин — зависит от осознанности."},
    71: {"name": "Сознание", "desc": "То, что наблюдает за умом. Свидетель всего происходящего."},
    72: {"name": "Чистое бытие", "desc": "Существование до мысли. Просто быть — без добавлений."},
}

SNAKES = {17: 7, 54: 19, 62: 42}
ARROWS = {6: 28, 14: 47, 22: 60, 36: 55, 52: 69}

sessions = {}

def get_session(user_id):
    if user_id not in sessions:
        sessions[user_id] = {
            "state": "idle", "query": "", "readiness": 0.5,
            "cell": 0, "path": [], "insights": [], "events": [],
        }
    return sessions[user_id]

def call_groq_sync(prompt, system="", max_tokens=400):
    if not GROQ_API_KEY:
        return "Ключ GROQ_API_KEY не добавлен."
    sys_msg = system or "Ты мудрый проводник трансформационной игры Лила. Отвечай по-русски. Тон тихий, внимательный, без пафоса."
    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30
        )
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Ошибка: {e}"

def analyze_query(query):
    prompt = f"""Оцени запрос по 5 критериям от 0 до 1:
specificity, depth, emotionality, responsibility, awareness.
Запрос: «{query}»
Ответь ТОЛЬКО JSON: {{"specificity":0.5,"depth":0.5,"emotionality":0.5,"responsibility":0.5,"awareness":0.5}}"""
    try:
        result = call_groq_sync(prompt, "Отвечай только валидным JSON.", 80)
        scores = json.loads(result[result.find("{"):result.rfind("}")+1])
        w = {"specificity":0.15,"depth":0.25,"emotionality":0.20,"responsibility":0.25,"awareness":0.15}
        return min(1.0, max(0.0, sum(scores.get(k,0.5)*v for k,v in w.items())))
    except:
        return 0.5

def reflect_query(query):
    return call_groq_sync(
        f"Игрок вошёл в игру Лила с запросом: «{query}»\n"
        "Напиши 1-2 тёплых предложения — отрази суть, не оценивая. "
        "Начни с «Я слышу» или «Похоже». Без советов.", max_tokens=100)

def generate_cell_text(cell_number, query):
    cell = CELLS.get(cell_number, {"name":"?","desc":""})
    return call_groq_sync(
        f"Клетка {cell_number} — «{cell['name']}»\nСуть: {cell['desc']}\nЗапрос: «{query}»\n\n"
        "Напиши единым потоком без заголовков:\n"
        "1. Смысл клетки — 2 предложения\n"
        "2. Связь с запросом — 1 предложение\n"
        "3. Один открытый вопрос\nТон тихий. До 100 слов.", max_tokens=300)

def explain_simpler(cell_number, query):
    cell = CELLS.get(cell_number, {"name":"?","desc":""})
    return call_groq_sync(
        f"Объясни клетку «{cell['name']}» просто. Контекст: «{query}»\n"
        "Начни с «Если совсем просто...». Один пример из жизни. До 60 слов.", max_tokens=150)

def generate_help_response(cell_number, query, theme):
    cell = CELLS.get(cell_number, {"name":"?","desc":""})
    return call_groq_sync(
        f"Игрок не понял клетку «{cell['name']}». Тема «{theme}» ближе.\n"
        f"Запрос: «{query}»\nОбъясни через эту тему конкретно. До 80 слов.", max_tokens=200)

def generate_final_summary(query, path, insights):
    ins = "\n".join(f"- {i}" for i in insights) if insights else "Мыслей не записано"
    return call_groq_sync(
        f"Игрок завершил игру Лила.\nЗапрос: «{query}»\n"
        f"Путь: {' → '.join(str(c) for c in path)}\nМысли:\n{ins}\n\n"
        "Напиши послание: что прожил (2 пред.), что стало яснее (1 пред.), вопрос для следующего шага. До 100 слов.", max_tokens=300)

def weighted_roll(readiness):
    if random.random() < 0.167 + readiness * 0.333:
        return 6
    return random.randint(1, 5)

ADMISSION_COMMENTS = {
    1: "Ваш запрос услышан. Но игра предлагает посмотреть совсем в другую сторону. Возможно, настоящий вопрос пока скрыт.",
    2: "Кажется, здесь есть ещё что-то важное. Попробуйте копнуть глубже.",
    3: "Уже появляется направление. Переформулируйте — вы близко.",
    4: "Ваш запрос становится яснее. Ещё чуть-чуть.",
    5: "Вы очень близко. Одно последнее уточнение.",
}

def kb_admission():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎲 Бросить кубик", callback_data="admission_roll"))
    return kb

def kb_cell():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("▶️ Продолжить путь", callback_data="continue"))
    kb.row(
        types.InlineKeyboardButton("💬 Объяснить проще", callback_data="simpler"),
        types.InlineKeyboardButton("✏️ Записать мысль", callback_data="insight")
    )
    kb.add(types.InlineKeyboardButton("❓ Не понимаю", callback_data="help"))
    return kb

def kb_game_roll():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎲 Бросить кубик", callback_data="game_roll"))
    return kb

def kb_help():
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("😨 Страх", callback_data="help_страх"),
        types.InlineKeyboardButton("🔀 Выбор", callback_data="help_выбор")
    )
    kb.row(
        types.InlineKeyboardButton("💞 Отношения", callback_data="help_отношения"),
        types.InlineKeyboardButton("🤔 Неуверенность", callback_data="help_неуверенность")
    )
    kb.add(types.InlineKeyboardButton("✨ Что-то другое", callback_data="help_другое"))
    return kb

def enter_cell(chat_id, session, cell_number):
    cell = CELLS.get(cell_number, {"name":"?","desc":""})
    prefix = ""

    if cell_number in SNAKES:
        to = SNAKES[cell_number]
        prefix = f"🐍 Здесь живёт змея.\n\nИгра возвращает вас к чему-то важному.\n\nВы переходите с {cell_number} на {to}.\n\n━━━━━━━━━━━━━━\n\n"
        session["events"].append(f"🐍 Змея: {cell_number}→{to}")
        cell_number = to
        cell = CELLS.get(cell_number, {"name":"?","desc":""})
    elif cell_number in ARROWS:
        to = ARROWS[cell_number]
        prefix = f"✨ Стрела! Вы увидели что-то важное — и движетесь вперёд.\n\nВы переходите с {cell_number} на {to}.\n\n━━━━━━━━━━━━━━\n\n"
        session["events"].append(f"✨ Стрела: {cell_number}→{to}")
        cell_number = to
        cell = CELLS.get(cell_number, {"name":"?","desc":""})

    session["cell"] = cell_number
    session["path"].append(cell_number)

    if cell_number == 68:
        finish_game(chat_id, session)
        return

    bot.send_message(chat_id, "⏳ Проводник думает...")
    text = generate_cell_text(cell_number, session["query"])
    header = f"{'━'*14}\n🎯 Клетка {cell_number} — «{cell['name']}»\n{'━'*14}\n\n"
    bot.send_message(chat_id, prefix + header + text, reply_markup=kb_cell())
    session["state"] = "cell_view"

def finish_game(chat_id, session):
    bot.send_message(chat_id, "⏳ Подготавливаю итог...")
    summary = generate_final_summary(session["query"], session["path"], session["insights"])
    path_str = " → ".join(str(c) for c in session["path"])
    bot.send_message(chat_id,
        f"🏁 Вы завершили путь.\n\n{'━'*14}\n"
        f"Ваш запрос:\n«{session['query']}»\n\n"
        f"Ваш путь:\n{path_str}\n{'━'*14}\n\n"
        f"{summary}\n\n{'━'*14}\n\n"
        f"Что стало понятнее?\nЧто изменилось?\nКакой шаг вы сделаете дальше?\n\n{'━'*14}\n\n"
        f"Ответ был не найден.\nОн был прожит."
    )
    session["state"] = "idle"
    bot.send_message(chat_id, "Чтобы начать новую игру — напишите /start")

@bot.message_handler(commands=["start"])
def cmd_start(message):
    uid = message.chat.id
    sessions[uid] = {"state":"query_input","query":"","readiness":0.5,"cell":0,"path":[],"insights":[],"events":[]}
    bot.send_message(uid,
        "✨ Добро пожаловать в игру Лила.\n\n"
        "Это путешествие по 72 состояниям человеческого опыта. "
        "Игра не даёт ответов — она помогает прожить вопрос.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "Сформулируйте запрос, с которым хотите войти в игру.\n\n"
        "Примеры:\n"
        "— Почему я боюсь менять работу?\n"
        "— Что мешает мне строить отношения?\n"
        "— Как мне выйти на новый уровень?\n\n"
        "Напишите свой запрос:"
    )

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    uid = message.chat.id
    s = get_session(uid)
    text = message.text.strip()

    if s["state"] == "query_input":
        bot.send_message(uid, "⏳ Принимаю ваш запрос...")
        s["readiness"] = analyze_query(text)
        s["query"] = text
        reflection = reflect_query(text)
        bot.send_message(uid, reflection)
        bot.send_message(uid,
            "Пространство готово встретить ваш запрос.\n\nБросьте кубик:",
            reply_markup=kb_admission()
        )
        s["state"] = "admission_roll"

    elif s["state"] == "insight_input":
        s["insights"].append(text)
        bot.send_message(uid, "✏️ Мысль записана.\n\nПродолжайте:", reply_markup=kb_cell())
        s["state"] = "cell_view"

    else:
        bot.send_message(uid, "Нажмите кнопку ниже, чтобы продолжить.")

@bot.callback_query_handler(func=lambda c: True)
def handle_callback(call):
    uid = call.message.chat.id
    s = get_session(uid)
    data = call.data
    bot.answer_callback_query(call.id)

    if data == "admission_roll":
        roll = weighted_roll(s["readiness"])
        if roll == 6:
            bot.send_message(uid, "🎲 Выпало: 6\n\nЗапрос услышан.\nВаш путь начинается.\n\n━━━━━━━━━━━━━━")
            enter_cell(uid, s, 6)
        else:
            bot.send_message(uid, f"🎲 Выпало: {roll}\n\n{ADMISSION_COMMENTS[roll]}\n\nНапишите новый вариант запроса:")
            s["state"] = "query_input"

    elif data == "continue":
        bot.send_message(uid, "🎲 Бросьте кубик:", reply_markup=kb_game_roll())
        s["state"] = "game_roll"

    elif data == "game_roll":
        roll = random.randint(1, 6)
        new_cell = min(s["cell"] + roll, 72)
        bot.send_message(uid, f"🎲 Выпало: {roll}\nКлетка {s['cell']} → {new_cell}")
        enter_cell(uid, s, new_cell)

    elif data == "simpler":
        bot.send_message(uid, "⏳ Ищу простые слова...")
        t = explain_simpler(s["cell"], s["query"])
        bot.send_message(uid, f"💬 {t}\n\n━━━━━━━━━━━━━━", reply_markup=kb_cell())

    elif data == "insight":
        bot.send_message(uid, "✏️ Напишите вашу мысль:")
        s["state"] = "insight_input"

    elif data == "help":
        bot.send_message(uid, "Что сейчас ближе к вашему состоянию?", reply_markup=kb_help())

    elif data.startswith("help_"):
        theme = data.replace("help_", "")
        bot.send_message(uid, "⏳ Подбираю объяснение...")
        t = generate_help_response(s["cell"], s["query"], theme)
        bot.send_message(uid, f"{t}\n\n━━━━━━━━━━━━━━", reply_markup=kb_cell())
        s["state"] = "cell_view"

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

if __name__ == "__main__":
    print("Бот Лила запущен!")
    # Сначала запускаем HTTP-сервер в главном потоке на секунду
    port = int(os.environ.get("PORT", 8080))
    health_server = HTTPServer(("0.0.0.0", port), HealthHandler)
    # Запускаем polling в отдельном потоке
    t = threading.Thread(target=bot.infinity_polling, daemon=True)
    t.start()
    print(f"HTTP health server on port {port}")
    health_server.serve_forever()

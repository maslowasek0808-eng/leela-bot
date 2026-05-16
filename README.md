# 🎲 Бот Лила — инструкция по запуску

## Что нужно перед стартом
- Аккаунт на GitHub (бесплатно: github.com)
- Аккаунт на Railway (бесплатно: railway.app)
- Токен вашего Telegram-бота от @BotFather
- Ключ Anthropic API (claude.ai/settings → API Keys)

---

## Шаг 1 — Загрузить код на GitHub

1. Зайдите на github.com → нажмите "+" → "New repository"
2. Название: `leela-bot`
3. Нажмите "Create repository"
4. На следующей странице нажмите "uploading an existing file"
5. Перетащите ВСЕ три файла: `bot.py`, `requirements.txt`, `Procfile`
6. Нажмите "Commit changes"

---

## Шаг 2 — Запустить на Railway

1. Зайдите на railway.app → "New Project"
2. Выберите "Deploy from GitHub repo"
3. Выберите ваш репозиторий `leela-bot`
4. Railway автоматически найдёт Procfile и начнёт деплой

---

## Шаг 3 — Добавить секретные ключи

В Railway откройте ваш проект → вкладка "Variables" → добавьте:

| Имя переменной    | Значение                        |
|-------------------|---------------------------------|
| `BOT_TOKEN`       | Токен от @BotFather             |
| `ANTHROPIC_API_KEY` | Ключ от Anthropic             |

После добавления Railway автоматически перезапустит бота.

---

## Шаг 4 — Проверить

Откройте вашего бота в Telegram и напишите /start

---

## Если что-то пошло не так

В Railway откройте вкладку "Logs" — там видно все ошибки.
Самая частая причина: неправильно скопирован токен (лишний пробел).

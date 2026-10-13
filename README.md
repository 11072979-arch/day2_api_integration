# День 2 — інтеграція OpenWeatherMap → Telegram

Python-скрипт отримує поточну погоду з OpenWeatherMap, перетворює JSON на читабельний текст і надсилає його у Telegram через Bot API.

## 1. Вимоги

- Python 3.10 або новіший
- API key OpenWeatherMap
- Telegram-бот, створений через `@BotFather`
- Telegram chat ID, у який бот має право надсилати повідомлення

## 2. Встановлення

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:
```bat
.venv\Scripts\activate.bat
```

Linux/macOS:
```bash
source .venv/bin/activate
```

Потім:
```bash
python -m pip install -r requirements.txt
```

## 3. Налаштування секретів

Скопіюй `.env.example` у файл `.env` та заповни значення:

```dotenv
WEATHER_API_KEY=твій_ключ_openweathermap
TELEGRAM_BOT_TOKEN=токен_від_botfather
TELEGRAM_CHAT_ID=твій_chat_id
WEATHER_CITY=Kropyvnytskyi
```

Не додавай `.env` до Git. У репозиторій має потрапити лише `.env.example` без секретів.

## 4. Де отримати значення

- OpenWeatherMap: створи обліковий запис на https://openweathermap.org/api і згенеруй API key.
- Telegram: створи бота через https://t.me/BotFather.
- Chat ID: відкрий чат із ботом, натисни Start і надішли йому повідомлення. Щоб дізнатися ID, відкрий у браузері `https://api.telegram.org/bot<ТВІЙ_ТОКЕН>/getUpdates`. Не публікуй це посилання: воно містить токен. Якщо `result` порожній, напиши боту повідомлення та онови сторінку.

## 5. Запуск

```bash
python main.py
```

У консолі мають з'явитися кроки отримання даних і підтвердження надсилання. Перевір також, що повідомлення з'явилося в Telegram.

## 6. Перевірка API у Postman

GET:
`https://api.openweathermap.org/data/2.5/weather`

Query params:
- `q` = `Kropyvnytskyi`
- `appid` = твій OpenWeatherMap API key
- `units` = `metric`
- `lang` = `uk`

Очікуваний успіх — HTTP `200 OK` і JSON з полями `name`, `main.temp`, `main.humidity`, `weather[0].description`. Не зберігай запит з реальним ключем у публічній колекції та не включай ключ у скриншот.

## 7. Git

Перед комітом перевір:
```bash
git status
git check-ignore .env
```

Якщо `.env` раніше вже був доданий до Git, `.gitignore` сам по собі не прибере його з індексу:
```bash
git rm --cached .env
```

Потім:
```bash
git add main.py requirements.txt README.md .env.example .gitignore
git commit -m "Add weather to Telegram API integration"
git push
```

Перевір історію комітів і переконайся, що в ній немає секретів. Якщо ключ уже потрапив у GitHub, відклич/перегенеруй його в кабінеті сервісу — простого видалення з файлу недостатньо.

## Обробка помилок

Скрипт обробляє тайм-аути, проблеми з'єднання, HTTP-помилки, некоректний JSON і відсутні поля. Код завершення `0` означає успіх, `1` — помилку. Реальний успіх можна підтвердити лише після запуску з дійсними ключами.

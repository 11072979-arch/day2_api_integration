"""Fetch current weather and send a summary to Telegram.

Configure secrets in .env (never commit that file).
"""
import logging
import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
TELEGRAM_URL = "https://api.telegram.org"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Raised when an external API request or response is invalid."""


def required_env(name: str) -> str:
    """Return a required environment variable or raise a safe error."""
    value = os.getenv(name, "").strip()
    if not value:
        raise IntegrationError(
            f"Не задано змінну {name}. Заповни її у файлі .env."
        )
    return value


def get_weather(city: str, api_key: str) -> dict[str, Any]:
    """Get current weather data from OpenWeatherMap."""
    try:
        response = requests.get(
            WEATHER_URL,
            params={
                "q": city,
                "appid": api_key,
                "units": "metric",
                "lang": "uk",
            },
            timeout=15,
        )
        if response.status_code != 200:
            # Do not log request URL: it contains the API key in query params.
            try:
                details = response.json().get("message", "невідома помилка")
            except (ValueError, AttributeError):
                details = "відповідь сервера не містить JSON"
            raise IntegrationError(
                f"OpenWeatherMap повернув HTTP {response.status_code}: {details}"
            )
        try:
            data = response.json()
        except ValueError as exc:
            raise IntegrationError("OpenWeatherMap повернув некоректний JSON.") from exc

    except requests.Timeout as exc:
        raise IntegrationError("Час очікування OpenWeatherMap вичерпано.") from exc
    except requests.ConnectionError as exc:
        raise IntegrationError("Не вдалося з'єднатися з OpenWeatherMap.") from exc
    except requests.RequestException as exc:
        raise IntegrationError(f"Помилка HTTP-запиту погоди: {exc.__class__.__name__}.") from exc

    try:
        return {
            "city": data["name"],
            "country": data["sys"].get("country", ""),
            "temperature": float(data["main"]["temp"]),
            "feels_like": float(data["main"]["feels_like"]),
            "humidity": int(data["main"]["humidity"]),
            "description": str(data["weather"][0]["description"]).capitalize(),
            "wind_speed": float(data["wind"]["speed"]),
        }
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise IntegrationError(
            "У відповіді OpenWeatherMap відсутні очікувані поля."
        ) from exc


def format_weather(weather: dict[str, Any]) -> str:
    """Transform API data into a readable Telegram message."""
    place = ", ".join(part for part in (weather["city"], weather["country"]) if part)
    return (
        f"🌦 Погода: {place}\n"
        f"🌡 Температура: {weather['temperature']:.1f} °C\n"
        f"🤗 Відчувається як: {weather['feels_like']:.1f} °C\n"
        f"💧 Вологість: {weather['humidity']}%\n"
        f"☁️ Опис: {weather['description']}\n"
        f"💨 Вітер: {weather['wind_speed']:.1f} м/с"
    )


def send_telegram_message(token: str, chat_id: str, message: str) -> None:
    """Send a message to a Telegram chat using the Bot API."""
    url = f"{TELEGRAM_URL}/bot{token}/sendMessage"
    try:
        response = requests.post(
            url,
            json={"chat_id": chat_id, "text": message},
            timeout=15,
        )
        if response.status_code != 200:
            try:
                details = response.json().get("description", "невідома помилка")
            except (ValueError, AttributeError):
                details = "відповідь сервера не містить JSON"
            raise IntegrationError(
                f"Telegram повернув HTTP {response.status_code}: {details}"
            )
        try:
            result = response.json()
        except ValueError as exc:
            raise IntegrationError("Telegram повернув некоректний JSON.") from exc

        if not result.get("ok", False):
            raise IntegrationError(
                f"Telegram не надіслав повідомлення: {result.get('description', 'невідома помилка')}"
            )
    except requests.Timeout as exc:
        raise IntegrationError("Час очікування Telegram вичерпано.") from exc
    except requests.ConnectionError as exc:
        raise IntegrationError("Не вдалося з'єднатися з Telegram.") from exc
    except requests.RequestException as exc:
        raise IntegrationError(
            f"Помилка HTTP-запиту Telegram: {exc.__class__.__name__}."
        ) from exc


def main() -> int:
    load_dotenv()

    try:
        city = os.getenv("WEATHER_CITY", "Kropyvnytskyi").strip() or "Kropyvnytskyi"
        weather_key = required_env("WEATHER_API_KEY")
        telegram_token = required_env("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = required_env("TELEGRAM_CHAT_ID")

        logger.info("Отримую актуальну погоду для %s...", city)
        weather = get_weather(city, weather_key)
        message = format_weather(weather)
        logger.info("Дані отримано та оброблено.")
        logger.info("Надсилаю повідомлення в Telegram...")
        send_telegram_message(telegram_token, telegram_chat_id, message)
        logger.info("Успіх: повідомлення надіслано в Telegram.")
        print("\n--- Дані, передані в Telegram ---")
        print(message)
        return 0

    except IntegrationError as exc:
        logger.error("%s", exc)
        return 1
    except Exception:
        # Log the traceback locally, but never print secret values deliberately.
        logger.exception("Непередбачена помилка інтеграції.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

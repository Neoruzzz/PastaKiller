# PastaKiller

PastaKiller — инструмент для автоматического репортинга паст на Pastebin.

## Требования

- Python 3.x
- Google Chrome
- Chromedriver (совместимый с версией Chrome)
- Модули Python (Устанавливаются автоматически):
  - selenium
  - requests
  - pillow (PIL)
  - 2captcha-python

## Конфигурация

Перед запуском необходимо создать файл `config.json` или заполнить его при первом запуске.

```json
{
  "use_proxies": true или false,
  "api_key": "ВАШ_API_КЛЮЧ_RUCAPTCHA",
  "pastebin_id": "ID_ПАСТЫ (https://pastebin.com/ID_ПАСТЫ)",
  "telegram_token": "ВАШ_TELEGRAM_BOT_TOKEN",
  "telegram_chatid": "ВАШ_CHAT_ID"
}
```

### Файлы настроек:

- `names.txt` - список имен, используемых для отправки репортов.
- `reports.txt` - список шаблонов репортов.
- `proxy.txt` - список HTTP-прокси в формате `IP:PORT` или `IP:PORT:USERNAME:PASSWORD`.

## Запуск

```bash
python main.py
```

## Описание работы

1. Загружаются имена, тексты репортов и (если включено) прокси.
2. Каждый поток открывает браузер через Selenium.
3. Заполняются данные репорта.
4. Капча решается с помощью RuCaptcha.
5. Жалоба отправляется.
6. Уведомление отправляется в Telegram (если указаны токен и чат ID).

## Примечания

- Используйте только HTTP-прокси.
- RuCaptcha API Key можно получить на [rucaptcha.com](https://rucaptcha.com/).
- Chromedriver должен соответствовать версии установленного Chrome.
- Не рекомендуется запускать больше 7 потоков (Зависит от мощности железа).


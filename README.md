# WeimpaRadar
ТРЕБОВАНИЯ
- Python 3.10+
- Playwright + Chromium
- OpenAI API key в окружении

----------------------------------------------------------------

УСТАНОВКА (ОДИН РАЗ)

В корне проекта:

python -m pip install python-dotenv openai playwright
python -m playwright install chromium

----------------------------------------------------------------

КЛЮЧ OPENAI (КАЖДЫЙ НОВЫЙ ТЕРМИНАЛ)

Windows PowerShell:

$env:OPENAI_API_KEY="PASTE_KEY_HERE"

----------------------------------------------------------------

ОДИН ТЕСТОВЫЙ ЗАПУСК (ПРЯМО СЕЙЧАС)

Выполнить одну команду:

'{"cmd":"run","client_domain":"weimpa.com","market":"Global","language":"en","mode":"sales","competitors":["brightcall.ai"],"slide_limit":5}' | python py\cli.py

----------------------------------------------------------------

ЧТО СЧИТАЕТСЯ УСПЕХОМ

1) В терминале вернулся JSON с:
   "ok": true

2) Появилась папка:

runs/2025-12-18__weimpa.com__sales__en/

3) Внутри есть файлы:

sales_note.txt      (есть текст)
report.md           (есть текст)
data.json           (заполнен)
data.csv            (заполнен)
screenshots/        (есть изображения)

----------------------------------------------------------------

БЫСТРАЯ ПРОВЕРКА "ГОТОВО ЗА 2 МИНУТЫ"

Открыть по порядку:
1) report.md
2) sales_note.txt
3) data.json
4) screenshots/

Файлы не пустые — ядро работает.

----------------------------------------------------------------

ТЕСТ БЛОКИРОВКИ / КАПЧИ

'{"cmd":"run","client_domain":"https://yasmina.yango.com/","mode":"sales"}' | python py\cli.py

Ожидаемо:
- screenshots/blocked.png
- в data.json → "blocked": true

# Extra výplata: анализ тиражей

Разбор лотереи TIPOS EXTRA VÝPLATA (6 из 27 + 1 из 7) по всем 165 тиражам с 25.03.2024 по 02.11.2026 и купон на тираж 05.11.2026.

Отчёт: `report/extra-vyplata.html`. Промт: `PROMPT.md`.

## Запуск заново перед следующим тиражом

```bash
cd extra-vyplata
python3 -I scripts/fetch.py data/draws_raw.json          # скачать тиражи с tipos.sk
python3 -I scripts/parse.py data/draws_raw.json data/draws.json
python3 -I scripts/analyze.py data/draws.json data/results.json   # частоты, тесты, бэктест формул
python3 -I scripts/tickets.py data/draws.json data/results.json data/tickets.json   # подбор полей
python3 -I scripts/build.py data/draws.json data/results.json data/tickets.json scripts/template.html report/extra-vyplata.html PROMPT.md
```

Нужны Python 3 и numpy 2.x. `fetch.py` скачивает тиражи до ноября 2026: для более поздних дат поправьте диапазон месяцев.

## Главные выводы

- Предсказать тираж нельзя. «Горячие» числа обгоняли случайный выбор в 2024–2025, но с июня 2026 их преимущество около нуля.
- Каждое поле за 1,50 € в среднем возвращает 0,87 € (выплачивается 57,9 % ставок).
- Подобранные 8 полей дают 67 % шанса выиграть хоть что-то против 57 % у случайных полей той же цены. Шанс на главный приз от подбора не меняется.

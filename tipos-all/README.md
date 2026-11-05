# Все лотереи TIPOS (кроме Keno)

Тот же анализ, что в `extra-vyplata/`, для Loto, Loto 5 z 35, Eurojackpot, Euromilióny, Všetko alebo nič и игр Joker, плюс ожидаемый возврат на 1 € при текущих джекпотах.

Отчёт: `report/tipos-all.html`. Промт: `PROMPT.md`. Итоги: `data/multi.json`.

## Запуск

```bash
cd tipos-all
mkdir -p data/all
python3 -I scripts/fetch_all.py Loto 2018 data/all/loto.json
python3 -I scripts/fetch_all.py Loto5z35 2018 data/all/l535.json
python3 -I scripts/fetch_all.py Euromiliony 2020 data/all/em.json
python3 -I scripts/fetch_all.py Eurojackpot 2022 data/all/ej.json
python3 -I scripts/fetch_all.py VsetkoAleboNic 2026 data/all/van.json
python3 -I scripts/multi.py data/all ../extra-vyplata/data/results.json data/multi.json
python3 -I scripts/build2.py data/multi.json ../extra-vyplata/data/tickets.json scripts/style_common.css scripts/template2_body.html PROMPT.md report/tipos-all.html
```

Сырые архивы (`data/all`) в репозиторий не кладутся: это около 6,5 МБ, они скачиваются заново.

## Итог на 5.11.2026

- Joker (0,60 € к Loto или Loto 5 z 35): джекпот 862 841 €, к тиражу 6.11 около 885 тыс. €, шанс 1 к 1 000 000. Ставка в среднем возвращает около 0,95 € (159 %). Порог окупаемости джекпота около 511 тыс. €.
- Loto 5 z 35 (1 поле) + Joker = 1,20 €, в среднем около 1,29 € (107 %).
- Остальные игры возвращают 40–58 % ставки. Ни одна формула не обгоняет случайный выбор.

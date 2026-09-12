# OVB – Finančný trh / Финансовый рынок

Prepis ručne kreslenej schémy OVB do dvoch PDF (tlačeným písmom).
Перенос рукописной схемы OVB в два PDF (печатными буквами).

## Výstupy / Файлы

| Súbor | Formát | Popis |
|---|---|---|
| `out/OVB-prezentacia.pdf` | 10 slajdov, 16:9 (960 × 540 pt) | prezentácia – titulná, schéma trhu, banky, poisťovne, piliere, fondy + stavebné sporenie, kolobeh peňazí, REKLAMA, legenda skratiek, originálna schéma |
| `out/OVB-schema-A4.pdf` | 1 strana A4 | presná kópia listu – rovnaké rozloženie, rámčeky a šípky, ale tlačené písmo |

## Zdroje / Исходники

- `prezentacia.html` – slajdy (HTML + SVG)
- `schema-a4.html` – kópia listu (SVG, viewBox 1548 × 2190)
- `build.sh` – vygeneruje obe PDF cez Chromium headless

```bash
./build.sh          # alebo: CHROME=/cesta/k/chrome ./build.sh
```

## Poznámka k obsahu

Všetky čísla a skratky (56R–EÚ, 33–SK, 30P, 400FM, 1 500 000, 22/6, 3/1, 30/11,
15/5, 813, percentá) sú prevzaté z originálneho listu bez zmeny. Rozpis skratiek
na poslednom slajde je čítanie zápisu, nie doplnené údaje.

Все цифры и сокращения перенесены с оригинального листа без изменений;
расшифровка сокращений — прочтение записи, а не добавленные данные.

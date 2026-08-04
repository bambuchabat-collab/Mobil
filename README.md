# Autoškola testy 🚗

Mobilná webová aplikácia na precvičovanie testov z pravidiel cestnej premávky.
Vyberieš si **skupinu vodičského oprávnenia** a v každej skupine máš **10 testov**.

Aplikácia je čisté HTML/CSS/JS bez frameworkov a bez buildu – dá sa otvoriť priamo
zo súboru, nahrať na GitHub Pages alebo pridať na plochu iPhonu ako webová aplikácia.

## Čo vie

- **6 skupín**: B, A, C, D, T, B+E – každá má vlastný mix otázok (spoločný základ + otázky pre danú skupinu)
- **10 testov v každej skupine** + náhodný test
- **294 otázok** v 7 tematických okruhoch, každá s vysvetlením správnej odpovede
- **Vyhodnotenie** – body, percentá, rozpis podľa okruhov, prehľad odpovedí, filter „len chyby“
- **Ukladanie výsledkov** do zariadenia (localStorage) – najlepší výsledok a počet pokusov pre každý test
- **Nastavenia** – miešanie odpovedí, časový limit, okamžitá kontrola po každej odpovedi
- **Offline režim** (service worker) a inštalácia na plochu (PWA), svetlý aj tmavý režim

## Model testu

| Vlastnosť | Hodnota |
|---|---|
| Počet otázok | 27 |
| Maximum bodov | 50 |
| Na úspech treba | 45 bodov (90 %) |
| Časový limit | 20 minút |

Rozdelenie otázok a bodov podľa okruhov:

| Okruh | Otázok | Bodov za otázku |
|---|---|---|
| Pravidlá cestnej premávky | 5 | 3 |
| Dopravné značky a zariadenia | 5 | 2 |
| Prednosť v jazde a križovatky | 4 | 3 |
| Všeobecné predpisy a doklady | 4 | 1 |
| Teória vedenia vozidla | 3 | 1 |
| Konštrukcia a údržba vozidla | 3 | 1 |
| Bezpečná jazda a prvá pomoc | 3 | 1 |

Celý model je na jednom mieste v `assets/js/config.js` – ak sa zmenia požiadavky,
stačí upraviť tento súbor a testy sa prepočítajú automaticky (`tools/validate.js`
skontroluje, či počty otázok a bodov naďalej sedia).

## Spustenie

Otvor `index.html` v prehliadači, alebo spusti lokálny server (kvôli offline režimu):

```bash
npx http-server -p 8080 .
# potom http://localhost:8080
```

Na iPhone: otvor stránku v Safari → **Zdieľať** → **Pridať na plochu**.

## Kontrola obsahu

```bash
node tools/validate.js     # alebo: npm test
```

Skript načíta skripty v rovnakom poradí ako `index.html` a overí, že:

- každá otázka má platné ID, okruh, skupiny, tri odpovede, jednu správnu a vysvetlenie,
- žiadne ID sa neopakuje a žiadna otázka nemá dve rovnaké odpovede,
- v každej skupine je pre každý okruh dosť otázok,
- každý z testov má presne 27 otázok, 50 bodov a správny počet otázok v každom okruhu,
- žiadna otázka nie je v jednom teste dvakrát a zostavenie testu je deterministické.

## Štruktúra projektu

```
index.html                     obal aplikácie a poradie skriptov
assets/css/app.css             štýly (svetlý aj tmavý režim, safe-area pre iPhone)
assets/js/config.js            skupiny, okruhy, bodovanie, časový limit
assets/js/bank.js              banka otázok a deterministické zostavovanie testov
assets/js/storage.js           ukladanie výsledkov a nastavení
assets/js/app.js               obrazovky a logika aplikácie
assets/js/data/questions-*.js  otázky (7 okruhov + otázky podľa skupín)
tools/validate.js              kontrola banky otázok a zloženia testov
tools/gen-icons.py             vygenerovanie PNG ikon
sw.js                          offline režim
```

## Ako pridať otázku

Do príslušného súboru v `assets/js/data/` pridaj záznam:

```js
{
  id: 'PCP-041',        // jedinečné ID
  cat: 1,               // okruh 1 – 7
  groups: ['*'],        // '*' = všetky skupiny, inak napr. ['C', 'D']
  q: 'Text otázky?',
  a: ['Správna odpoveď', 'Nesprávna', 'Nesprávna'],
  c: 0,                 // index správnej odpovede
  e: 'Vysvetlenie, prečo je odpoveď správna.'
}
```

Nová otázka sa automaticky zapojí do rozdeľovania medzi testy. Po pridaní spusti
`node tools/validate.js`. Ak pribudne nový súbor s otázkami, pridaj ho aj do
`index.html` (za `bank.js`) a do zoznamu `ASSETS` v `sw.js`.

## Poznámka

Otázky sú učebnou pomôckou vychádzajúcou zo zákona č. 8/2009 Z. z. o cestnej premávke.
**Nejde o oficiálne testy Policajného zboru** – pred skúškou si vždy over aktuálne
znenie predpisov.

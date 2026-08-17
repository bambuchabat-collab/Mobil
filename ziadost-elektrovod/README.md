# Žiadosť — Elektrovod a.s., Montér oceľových konštrukcií — lezec

Balík dokumentov k inzerátu https://www.profesia.sk/praca/elektrovod/O5325752

## Súbory

| Súbor | Na čo je |
|---|---|
| `Zivotopis_Ostap_Ilischuk.pdf` | príloha do e-mailu / Profesia.sk |
| `Motivacny_list_Ostap_Ilischuk.pdf` | príloha do e-mailu / Profesia.sk |
| `sprievodny-text.md` | text správy — skopírovať do formulára |
| `zivotopis.html`, `motivacny-list.html` | zdroje na úpravy |
| `PROMPT.md` | zadanie, podľa ktorého boli dokumenty vytvorené |

## Pred odoslaním DOPLNIŤ

V životopise zostávajú **2 miesta označené červeným `[DOPLNIŤ]`**. Bez nich sa
dokument neposiela — červený text v PDF je zámerný, aby sa nedali prehliadnuť.

1. Vzdelanie: **názov školy**
2. Vzdelanie: **roky štúdia**

Ďalej si treba overiť dve veci, ktoré nie sú označené v texte:

- **Meno a priezvisko** — v dokumentoch je `Ostap Ilischuk`, odvodené z e-mailovej
  adresy. Overiť presný prepis podľa dokladu o tolerovanom pobyte
  (možný variant `Ilishchuk`).
- **Reštaurácia Millenium** — overiť oficiálny latinkový zápis názvu.

## Nezrovnalosť v dátumoch

Dátum narodenia 16. 10. 2005 a pozícia kuchára v rokoch 2020 – 2022 znamenajú
vek 14 – 17 rokov. Personalista si to prepočíta. Ak išlo o prácu popri štúdiu
alebo o odbornú prax, treba to v životopise pomenovať — stačí doplniť
`(popri štúdiu)` za názov pozície a otázka je vybavená. Ak sú dátumy nepresné,
opraviť ich.

## Ako po úprave znova vygenerovať PDF

```sh
CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
for f in zivotopis motivacny-list; do
  "$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$f.pdf" "$f.html"
done
```

Oba dokumenty musia zostať na jednej strane A4. Ak text pretečie na druhú
stranu, uber `font-size` alebo `line-height` v hlavičke `<style>`.

## Poznámka k obsahu

Inzerát žiada vodičský preukaz sk. B, elektrotechnickú odbornosť podľa vyhl.
508/2009 Z. z. je uvedená ako výhoda a lezecké osvedčenie sa predpokladá.
Kandidát nemá ani jedno. Motivačný list to priznáva **raz, jednou vetou**,
spolu s ochotou školenia absolvovať; životopis sa k tomu nevracia a stavia na
tom, čo kandidát reálne má — horolezectvo, šport, prax s retrakom, dostupnosť
ihneď a bezproblémový turnusový režim.

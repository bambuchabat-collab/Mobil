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

## Stav

Dokumenty sú kompletné a pripravené na odoslanie. Žiadne zástupné texty
v nich nezostali.

Názov školy a roky štúdia sa neuvádzajú — v sekcii `Vzdelanie` je uvedený
len stupeň vzdelania, čo pre požiadavku inzerátu („stredoškolské bez maturity")
postačuje.

## Voliteľné úpravy

Nasledujúce údaje sú v dokumentoch uvedené v podobe, ktorú možno ešte spresniť:

- **Meno a priezvisko** — použité `Ostap Ilischuk`, odvodené z e-mailovej adresy.
  Prípadne overiť podľa dokladu o tolerovanom pobyte (možný variant `Ilishchuk`).
- **Reštaurácia Millenium** — latinkový zápis názvu.
- **Kuchár 2020 – 2022** — pri dátume narodenia 16. 10. 2005 zodpovedá veku
  14 – 17 rokov. Ak išlo o prácu popri štúdiu, dá sa to ošetriť doplnením
  `(popri štúdiu)` za názov pozície v `zivotopis.html`.

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

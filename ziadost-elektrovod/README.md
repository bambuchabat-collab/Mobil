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

V životopise je **6 miest označených červeným `[DOPLNIŤ]`**. Bez nich sa
dokument neposiela — červený text v PDF je zámerný, aby sa nedali prehliadnuť.

1. Meno a priezvisko — overiť presný prepis podľa dokladu o tolerovanom pobyte
   (v dokumentoch je odvodené z e-mailovej adresy)
2. Skladník — operátor retraku: **zamestnávateľ** + **obdobie**
3. Kuchár: **zamestnávateľ** + **obdobie**
4. Vzdelanie: **názov školy** + **roky**

Ak ovládaš aj ruštinu alebo angličtinu, doplň ich do sekcie `Jazyky`.

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

/* Okruh 1 – Pravidlá cestnej premávky (zákon č. 8/2009 Z. z.) */
(function () {
  'use strict';
  BANK.add([
    {
      id: 'PCP-001', cat: 1, groups: ['*'],
      q: 'Aká je najvyššia dovolená rýchlosť vozidla v obci, ak nie je dopravnou značkou určené inak?',
      a: ['50 km/h', '60 km/h', '40 km/h'], c: 0,
      e: 'V obci smie vodič jazdiť rýchlosťou najviac 50 km/h. Dopravná značka môže rýchlosť znížiť aj zvýšiť.'
    },
    {
      id: 'PCP-002', cat: 1, groups: ['*'],
      q: 'Aká je najvyššia dovolená rýchlosť mimo obce na ceste, ktorá nie je diaľnicou ani rýchlostnou cestou?',
      a: ['90 km/h', '80 km/h', '110 km/h'], c: 0,
      e: 'Mimo obce je základná najvyššia dovolená rýchlosť 90 km/h.'
    },
    {
      id: 'PCP-003', cat: 1, groups: ['*'],
      q: 'Aká je najvyššia dovolená rýchlosť na diaľnici mimo obce?',
      a: ['130 km/h', '120 km/h', '150 km/h'], c: 0,
      e: 'Na diaľnici a rýchlostnej ceste mimo obce je najvyššia dovolená rýchlosť 130 km/h.'
    },
    {
      id: 'PCP-004', cat: 1, groups: ['*'],
      q: 'Aká je najvyššia dovolená rýchlosť na diaľnici, ktorá prechádza obcou?',
      a: ['90 km/h', '50 km/h', '130 km/h'], c: 0,
      e: 'Na diaľnici a rýchlostnej ceste v obci smie vodič jazdiť najviac 90 km/h.'
    },
    {
      id: 'PCP-005', cat: 1, groups: ['*'],
      q: 'Koľko alkoholu v krvi smie mať vodič pri vedení motorového vozidla?',
      a: ['Žiadny – vedenie vozidla po požití alkoholu je zakázané', 'Najviac 0,5 promile', 'Najviac 0,2 promile'],
      c: 0,
      e: 'Vodič nesmie viesť vozidlo po požití alkoholu alebo inej návykovej látky, ani v čase, keď je ešte pod ich vplyvom.'
    },
    {
      id: 'PCP-006', cat: 1, groups: ['*'],
      q: 'Smie vodič počas jazdy telefonovať?',
      a: ['Áno, ale len pomocou hands-free (bez držania telefónu v ruke)', 'Áno, kedykoľvek', 'Nie, telefonovanie počas jazdy je zakázané v každom prípade'],
      c: 0,
      e: 'Vodič nesmie počas jazdy držať telefónny prístroj v ruke ani iným spôsobom, ktorý mu bráni v bezpečnom vedení vozidla.'
    },
    {
      id: 'PCP-007', cat: 1, groups: ['*'],
      q: 'Kedy musí mať motorové vozidlo počas jazdy rozsvietené stretávacie svetlá?',
      a: ['Počas celého dňa, po celý rok', 'Len od súmraku do svitania', 'Len v období od 15. novembra do 31. marca'],
      c: 0,
      e: 'Vozidlo musí mať rozsvietené stretávacie svetlá alebo denné svietenie počas celého dňa a celý rok.'
    },
    {
      id: 'PCP-008', cat: 1, groups: ['*'],
      q: 'Kto je povinný byť počas jazdy pripútaný bezpečnostným pásom?',
      a: ['Vodič aj všetky prepravované osoby na sedadlách vybavených pásmi', 'Len vodič a spolujazdec vpredu', 'Len osoby na predných sedadlách mimo obce'],
      c: 0,
      e: 'Pripútať sa musí každá osoba na sedadle povinne vybavenom bezpečnostným pásom, vpredu aj vzadu.'
    },
    {
      id: 'PCP-009', cat: 1, groups: ['*'],
      q: 'Ako sa musí prepravovať dieťa s telesnou výškou menšou ako 150 cm?',
      a: ['V detskej zádržnej sústave (autosedačke) vhodnej pre jeho hmotnosť a výšku', 'Len na zadnom sedadle bez ďalších podmienok', 'Na kolenách dospelej osoby'],
      c: 0,
      e: 'Dieťa menšie ako 150 cm sa smie prepravovať len v autosedačke zodpovedajúcej jeho telesným rozmerom.'
    },
    {
      id: 'PCP-010', cat: 1, groups: ['*'],
      q: 'Kde vodič nesmie zastaviť a stáť vo vzťahu k priechodu pre chodcov?',
      a: ['Na priechode a vo vzdialenosti kratšej ako 5 m pred ním', 'Iba priamo na priechode', 'Vo vzdialenosti kratšej ako 15 m pred priechodom'],
      c: 0,
      e: 'Zastavenie a státie je zakázané na priechode pre chodcov aj na priechode pre cyklistov a bližšie ako 5 m pred nimi.'
    },
    {
      id: 'PCP-011', cat: 1, groups: ['*'],
      q: 'V akej vzdialenosti od hranice križovatky je zakázané zastavenie a státie?',
      a: ['Bližšie ako 5 m pred hranicou križovatky a 5 m za ňou', 'Bližšie ako 10 m pred aj za križovatkou', 'Bližšie ako 2 m pred križovatkou'],
      c: 0,
      e: 'Pri križovatke platí zákaz zastavenia a státia vo vzdialenosti kratšej ako 5 m pred hranicou križovatky a 5 m za ňou.'
    },
    {
      id: 'PCP-012', cat: 1, groups: ['*'],
      q: 'V akej vzdialenosti od železničného priecestia platí zákaz zastavenia a státia?',
      a: ['Bližšie ako 15 m pred priecestím a 15 m za ním', 'Bližšie ako 5 m pred aj za priecestím', 'Bližšie ako 30 m pred priecestím'],
      c: 0,
      e: 'Na železničnom priecestí a vo vzdialenosti kratšej ako 15 m pred ním a za ním sa nesmie zastaviť ani stáť.'
    },
    {
      id: 'PCP-013', cat: 1, groups: ['*'],
      q: 'Smie vodič predchádzať iné vozidlo na priechode pre chodcov?',
      a: ['Nie, na priechode ani bezprostredne pred ním', 'Áno, ak na priechode nie je chodec', 'Áno, ak jazdí rýchlosťou najviac 30 km/h'],
      c: 0,
      e: 'Predchádzanie je zakázané na priechode pre chodcov a bezprostredne pred ním, pretože vodič nevidí za predchádzané vozidlo.'
    },
    {
      id: 'PCP-014', cat: 1, groups: ['*'],
      q: 'Po ktorej strane vodič spravidla predchádza iné vozidlo?',
      a: ['Vľavo; vpravo sa predchádza vozidlo, ktoré odbočuje vľavo', 'Vždy vpravo', 'Podľa vlastného uváženia, zákon to neurčuje'],
      c: 0,
      e: 'Predchádza sa vľavo. Vpravo sa predchádza vozidlo, ktoré mení smer jazdy vľavo a už nie je pochybnosť o ďalšom smere jeho jazdy.'
    },
    {
      id: 'PCP-015', cat: 1, groups: ['*'],
      q: 'Akou rýchlosťou smie vodič prechádzať cez železničné priecestie, ak svieti prerušované biele svetlo priecestného zabezpečovacieho zariadenia?',
      a: ['Najviac 50 km/h', 'Najviac 30 km/h', 'Najviac 90 km/h'],
      c: 0,
      e: 'Pri prerušovanom bielom svetle smie vodič prechádzať priecestím rýchlosťou najviac 50 km/h, inak najviac 30 km/h.'
    },
    {
      id: 'PCP-016', cat: 1, groups: ['*'],
      q: 'Kedy smie vodič použiť zvukové výstražné znamenie (klaksón)?',
      a: ['Len ak je to potrebné na odvrátenie hroziaceho nebezpečenstva', 'Kedykoľvek na upozornenie iných vodičov', 'Vždy pred vchádzaním do križovatky'],
      c: 0,
      e: 'Zvukové znamenie sa smie použiť len na odvrátenie hroziaceho nebezpečenstva, mimo obce aj na upozornenie pri predchádzaní.'
    },
    {
      id: 'PCP-017', cat: 1, groups: ['*'],
      q: 'Ako má vodič postupovať pri cúvaní na väčšiu vzdialenosť alebo na neprehľadnom mieste?',
      a: ['Zaistiť bezpečné cúvanie pomocou spôsobilej a náležite poučenej osoby', 'Cúvať rýchlo, aby čo najskôr uvoľnil cestu', 'Použiť len spätné zrkadlá, iná pomoc nie je potrebná'],
      c: 0,
      e: 'Ak to vyžaduje bezpečnosť, vodič je povinný zaistiť cúvanie pomocou spôsobilej a náležite poučenej osoby.'
    },
    {
      id: 'PCP-018', cat: 1, groups: ['*'],
      q: 'Kde je zakázané otáčanie a cúvanie?',
      a: ['Na priechode pre chodcov, na moste, v tuneli a na železničnom priecestí', 'Len na diaľnici', 'Len v obci po zotmení'],
      c: 0,
      e: 'Otáčať a cúvať sa nesmie na neprehľadnom mieste, na priechode pre chodcov, na moste, v tuneli, na priecestí a na miestach s obmedzeným výhľadom.'
    },
    {
      id: 'PCP-019', cat: 1, groups: ['*'],
      q: 'Ako sa má zachovať vodič, keď autobus pravidelnej verejnej dopravy v obci vychádza zo zastávky a dáva znamenie o zmene smeru jazdy?',
      a: ['Umožniť mu vyjsť zo zastávky – prípadne aj znížiť rýchlosť alebo zastaviť', 'Zrýchliť a predbehnúť ho', 'Trvať na svojom práve prednosti a pokračovať bez zmeny'],
      c: 0,
      e: 'V obci je vodič povinný umožniť vodičovi autobusu vyjsť zo zastávky, ak autobus dáva znamenie o zmene smeru jazdy.'
    },
    {
      id: 'PCP-020', cat: 1, groups: ['*'],
      q: 'Ako sa musí vodič zachovať, keď za ním prichádza vozidlo s právom prednostnej jazdy (modré svetlo a siréna)?',
      a: ['Uvoľniť mu vozovku, prípadne aj zastaviť', 'Zrýchliť a jazdiť pred ním', 'Zastaviť v strede vozovky a čakať'],
      c: 0,
      e: 'Vodič je povinný umožniť bezpečný a plynulý prejazd vozidla s právom prednostnej jazdy, ak treba aj zastaviť na krajnici.'
    },
    {
      id: 'PCP-021', cat: 1, groups: ['*'],
      q: 'Čo je vodič povinný urobiť pri vytváraní kolóny na diaľnici s dvomi jazdnými pruhmi v jednom smere?',
      a: ['Vytvoriť záchranársku uličku medzi pruhmi pre vozidlá záchrannej služby', 'Zastaviť na odstavnom pruhu', 'Zapnúť diaľkové svetlá'],
      c: 0,
      e: 'Pri spomalení alebo zastavení kolóny sú vodiči povinní vytvoriť voľný priestor – záchranársku uličku – pre vozidlá s právom prednostnej jazdy.'
    },
    {
      id: 'PCP-022', cat: 1, groups: ['*'],
      q: 'Čo je na diaľnici zakázané?',
      a: ['Zastavenie, státie, otáčanie a cúvanie', 'Predchádzanie vľavo', 'Jazda rýchlosťou nižšou ako 100 km/h'],
      c: 0,
      e: 'Na diaľnici sa nesmie zastaviť ani stáť (okrem odpočívadiel a núdze), otáčať sa, cúvať ani jazdiť v protismere.'
    },
    {
      id: 'PCP-023', cat: 1, groups: ['*'],
      q: 'Kde na ceste má vodič jazdiť?',
      a: ['Pri pravom okraji vozovky, ak tomu nebránia okolnosti', 'V strede vozovky', 'V ľavom jazdnom pruhu, aby lepšie videl'],
      c: 0,
      e: 'Vodič jazdí vpravo a čo najbližšie k pravému okraju vozovky, s ohľadom na bezpečnosť a plynulosť premávky.'
    },
    {
      id: 'PCP-024', cat: 1, groups: ['*'],
      q: 'Akú rýchlosť musí vodič dodržať v obytnej zóne alebo pešej zóne?',
      a: ['Najviac 20 km/h', 'Najviac 30 km/h', 'Najviac 50 km/h'],
      c: 0,
      e: 'V obytnej, pešej a školskej zóne smie vodič jazdiť rýchlosťou najviac 20 km/h a nesmie ohroziť chodcov.'
    },
    {
      id: 'PCP-025', cat: 1, groups: ['*'],
      q: 'Ako sa má vodič správať pri približovaní sa k priechodu pre chodcov?',
      a: ['Jazdiť tak, aby mohol zastaviť pred priechodom, a umožniť chodcovi prejsť', 'Zvýšiť rýchlosť, aby priechod rýchlo prešiel', 'Použiť zvukové znamenie a pokračovať v jazde'],
      c: 0,
      e: 'Vodič nesmie ohroziť ani obmedziť chodca prechádzajúceho cez priechod; k priechodu sa musí blížiť primeranou rýchlosťou.'
    },
    {
      id: 'PCP-026', cat: 1, groups: ['*'],
      q: 'Aký bočný odstup musí vodič dodržať pri predchádzaní cyklistu?',
      a: ['Bezpečný bočný odstup najmenej 1 meter', 'Postačuje 30 cm', 'Zákon žiadny odstup neurčuje'],
      c: 0,
      e: 'Pri predchádzaní cyklistu je vodič povinný dodržať bezpečný bočný odstup najmenej 1 meter.'
    },
    {
      id: 'PCP-027', cat: 1, groups: ['*'],
      q: 'Aká vzdialenosť sa musí dodržiavať za vozidlom idúcim vpredu?',
      a: ['Taká, aby vodič mohol bezpečne zastaviť, ak vozidlo pred ním prudko zabrzdí', 'Presne dva metre', 'Vzdialenosť nie je podstatná, ak sa jazdí do 50 km/h'],
      c: 0,
      e: 'Vodič musí za vozidlom idúcim pred ním dodržiavať takú vzdialenosť, aby mohol včas znížiť rýchlosť alebo zastaviť.'
    },
    {
      id: 'PCP-028', cat: 1, groups: ['*'],
      q: 'Kedy je vodič povinný dať znamenie o zmene smeru jazdy?',
      a: ['Vždy, keď mení smer jazdy alebo prechádza do iného jazdného pruhu – včas pred manévrom', 'Len ak je za ním iné vozidlo', 'Len v obci'],
      c: 0,
      e: 'Znamenie sa dáva včas pred zmenou smeru jazdy a ukončí sa hneď po jej vykonaní.'
    },
    {
      id: 'PCP-029', cat: 1, groups: ['*'],
      q: 'Kedy vodič použije výstražné (súčasné blikanie všetkých smeroviek) znamenie?',
      a: ['Ak hrozí nebezpečenstvo, napríklad pri náhlom vzniku kolóny alebo pri poruche vozidla', 'Pri parkovaní na chodníku', 'Pri každom odbočovaní vľavo'],
      c: 0,
      e: 'Výstražné znamenie upozorňuje ostatných vodičov na hroziace nebezpečenstvo, napríklad na koniec kolóny alebo nepojazdné vozidlo.'
    },
    {
      id: 'PCP-030', cat: 1, groups: ['*'],
      q: 'Kde smie vodič motorového vozidla zastaviť a stáť na chodníku?',
      a: ['Len na mieste, ktoré je na to označené dopravnou značkou', 'Kdekoľvek, ak ostane 1,5 m pre chodcov', 'Kdekoľvek, ak stojí najviac 10 minút'],
      c: 0,
      e: 'Státie na chodníku je dovolené len na mieste označenom príslušnou dopravnou značkou.'
    },
    {
      id: 'PCP-031', cat: 1, groups: ['*'],
      q: 'Čo znamená pojem „zastavenie vozidla“?',
      a: ['Uvedenie vozidla do pokoja na čas nevyhnutne potrebný na nastúpenie alebo vystúpenie osôb, prípadne naloženie nákladu',
          'Uvedenie vozidla do pokoja na ľubovoľne dlhý čas', 'Zaparkovanie vozidla cez noc'],
      c: 0,
      e: 'Zastavenie je krátkodobé uvedenie vozidla do pokoja; dlhšie uvedenie do pokoja je státie.'
    },
    {
      id: 'PCP-032', cat: 1, groups: ['*'],
      q: 'Kedy je vodič povinný použiť zimné pneumatiky?',
      a: ['Ak sa na vozovke nachádza súvislá snehová vrstva, ľad alebo námraza', 'Vždy od 1. októbra do 31. marca bez ohľadu na počasie', 'Nikdy, je to len odporúčanie'],
      c: 0,
      e: 'Zimné pneumatiky sú povinné, keď je na vozovke súvislá snehová vrstva, ľad alebo námraza.'
    },
    {
      id: 'PCP-033', cat: 1, groups: ['*'],
      q: 'Ako sa má vodič zachovať, keď vytvorí prekážku cestnej premávky (napríklad pri poruche vozidla)?',
      a: ['Bezodkladne ju odstrániť, a ak to nie je možné, označiť ju a ohlásiť polícii', 'Počkať, kým ju odstráni iný vodič', 'Nemusí robiť nič, ak vozidlo nie je pojazdné'],
      c: 0,
      e: 'Kto spôsobil prekážku premávky, je povinný ju odstrániť; ak to nedokáže, musí ju označiť a oznámiť to polícii.'
    },
    {
      id: 'PCP-034', cat: 1, groups: ['*'],
      q: 'Smie vodič vojsť na križovatku, ak mu situácia nedovoľuje pokračovať v jazde za križovatku?',
      a: ['Nie, nesmie vojsť, ak by musel zastaviť na križovatke', 'Áno, ak má zelenú', 'Áno, vždy keď má prednosť v jazde'],
      c: 0,
      e: 'Do križovatky sa nesmie vchádzať, ak dopravná situácia nedovoľuje križovatku bez zastavenia prejsť.'
    },
    {
      id: 'PCP-035', cat: 1, groups: ['*'],
      q: 'Ako musí vodič postupovať pri jazde okolo električky, ktorá stojí v zastávke bez nástupného ostrovčeka?',
      a: ['Zastaviť a umožniť cestujúcim bezpečne nastúpiť a vystúpiť', 'Prejsť okolo nej najviac 30 km/h bez zastavenia', 'Použiť zvukové znamenie a pokračovať v jazde'],
      c: 0,
      e: 'Ak zastávka nemá nástupný ostrovček, vodič musí zastaviť a nechať cestujúcich bezpečne nastúpiť alebo vystúpiť.'
    },
    {
      id: 'PCP-036', cat: 1, groups: ['*'],
      q: 'Akou najvyššou rýchlosťou sa smie jazdiť pri vlečení motorového vozidla?',
      a: ['Najviac 60 km/h', 'Najviac 90 km/h', 'Rýchlosť nie je obmedzená'],
      c: 0,
      e: 'Pri vlečení motorového vozidla je najvyššia dovolená rýchlosť 60 km/h.'
    },
    {
      id: 'PCP-037', cat: 1, groups: ['*'],
      q: 'Smie vodič počas jazdy fajčiť alebo jesť tak, že drží predmet v ruke?',
      a: ['Nie, ak mu to bráni v bezpečnom vedení vozidla a v držaní volantu', 'Áno, vždy', 'Áno, ak jazdí do 50 km/h'],
      c: 0,
      e: 'Vodič musí venovať plnú pozornosť vedeniu vozidla a nesmie robiť činnosti, ktoré ho od nej odpútavajú.'
    },
    {
      id: 'PCP-038', cat: 1, groups: ['*'],
      q: 'Kedy smie vodič použiť diaľkové svetlá?',
      a: ['Len ak neoslní vodičov ostatných vozidiel ani iné osoby', 'Vždy mimo obce bez obmedzenia', 'V obci pri jazde za iným vozidlom'],
      c: 0,
      e: 'Diaľkové svetlá sa nesmú použiť, ak by mohli oslniť vodičov protiidúcich vozidiel, vodiča idúceho vpredu alebo iné osoby.'
    },
    {
      id: 'PCP-039', cat: 1, groups: ['*'],
      q: 'Ako sa vodič musí zachovať, keď sa priecestné zabezpečovacie zariadenie rozsvieti prerušovaným červeným svetlom?',
      a: ['Zastaviť pred priecestím a nevchádzať naň', 'Rýchlo prejsť priecestie', 'Pokračovať v jazde rýchlosťou 30 km/h'],
      c: 0,
      e: 'Pri dvoch striedavo prerušovaných červených svetlách musí vodič zastaviť pred priecestím a čakať.'
    },
    {
      id: 'PCP-040', cat: 1, groups: ['*'],
      q: 'Čo musí vodič urobiť, ak mu na priecestí vozidlo zostane stáť a nedá sa naštartovať?',
      a: ['Odstrániť vozidlo z priecestia, a ak to nejde, urobiť všetko pre varovanie rušňovodiča', 'Zostať sedieť vo vozidle a čakať', 'Zapnúť diaľkové svetlá a čakať na políciu'],
      c: 0,
      e: 'Vodič musí vozidlo z priecestia odstrániť; ak to nie je možné, musí bezodkladne varovať vodičov koľajových vozidiel.'
    }
  ]);
})();

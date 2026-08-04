/* Okruh 7 – Zásady bezpečnej jazdy a poskytovanie prvej pomoci */
(function () {
  'use strict';
  BANK.add([
    {
      id: 'BEZ-001', cat: 7, groups: ['*'],
      q: 'Aké je telefónne číslo záchrannej zdravotnej služby na Slovensku?',
      a: ['155 (alebo 112)', '158', '150'], c: 0,
      e: 'Na 155 sa dovoláte priamo záchrannej zdravotnej službe, 112 je jednotné európske tiesňové číslo.'
    },
    {
      id: 'BEZ-002', cat: 7, groups: ['*'],
      q: 'Čo treba urobiť ako prvé na mieste dopravnej nehody?',
      a: ['Zabezpečiť miesto nehody, aby nevznikla ďalšia nehoda, a až potom pomáhať zraneným',
          'Ihneď presunúť všetkých zranených mimo vozidiel', 'Odfotografovať poškodenie vozidiel'],
      c: 0,
      e: 'Vlastná bezpečnosť je prvá – výstražné svetlá, reflexný odev, trojuholník; potom nasleduje pomoc zraneným.'
    },
    {
      id: 'BEZ-003', cat: 7, groups: ['*'],
      q: 'Ako postupujeme pri kardiopulmonálnej resuscitácii dospelého?',
      a: ['30 stlačení hrudníka a 2 vdychy, s frekvenciou stlačení 100 – 120 za minútu',
          '10 stlačení a 5 vdychov', 'Len umelé dýchanie bez stláčania hrudníka'],
      c: 0,
      e: 'Ak zachranca nevie alebo nechce dýchať z úst do úst, vykonáva aspoň nepretržité stláčanie hrudníka.'
    },
    {
      id: 'BEZ-004', cat: 7, groups: ['*'],
      q: 'Do akej hĺbky sa stláča hrudník dospelého pri resuscitácii?',
      a: ['Približne 5 – 6 cm', 'Približne 1 – 2 cm', 'Približne 10 cm'], c: 0,
      e: 'Stláča sa v strede hrudníka, dostatočne hlboko a rýchlo, s úplným uvoľnením medzi stlačeniami.'
    },
    {
      id: 'BEZ-005', cat: 7, groups: ['*'],
      q: 'Ako uložíme zraneného, ktorý je v bezvedomí, ale normálne dýcha?',
      a: ['Do stabilizovanej polohy na boku a priebežne kontrolujeme dýchanie', 'Na chrbát s podloženou hlavou', 'Posadíme ho a dáme mu vodu'],
      c: 0,
      e: 'Stabilizovaná poloha udržiava priechodné dýchacie cesty a zabraňuje vdýchnutiu zvratkov.'
    },
    {
      id: 'BEZ-006', cat: 7, groups: ['*'],
      q: 'Kedy smieme zraneného premiestniť z vozidla pred príchodom záchranárov?',
      a: ['Len ak mu hrozí bezprostredné nebezpečenstvo, napríklad požiar alebo je potrebná resuscitácia',
          'Vždy a ihneď', 'Nikdy, ani pri požiari'],
      c: 0,
      e: 'Neodborná manipulácia môže zhoršiť poranenie chrbtice; presúvame len pri priamom ohrození života.'
    },
    {
      id: 'BEZ-007', cat: 7, groups: ['*'],
      q: 'Ako zastavíme silné vonkajšie krvácanie?',
      a: ['Priamym tlakom na ranu a priložením tlakového obväzu', 'Priložením studeného obkladu', 'Vydezinfikovaním rany a jej ponechaním voľne'],
      c: 0,
      e: 'Pri masívnom krvácaní z končatiny, ktoré sa nedá zastaviť, je poslednou možnosťou škrtidlo.'
    },
    {
      id: 'BEZ-008', cat: 7, groups: ['*'],
      q: 'Aké informácie treba uviesť pri volaní na tiesňovú linku?',
      a: ['Kde sa nehoda stala, čo sa stalo, koľko je zranených a kto volá', 'Len meno volajúceho', 'Len evidenčné číslo vozidla'],
      c: 0,
      e: 'Presné miesto a počet zranených umožnia dispečerovi vyslať správnu pomoc; hovor ukončuje dispečer.'
    },
    {
      id: 'BEZ-009', cat: 7, groups: ['*'],
      q: 'Smieme zranenému motocyklistovi zložiť prilbu?',
      a: ['Len ak je to nevyhnutné, napríklad ak nedýcha a treba resuscitovať – ideálne dvaja zachrancovia',
          'Vždy a ihneď po nehode', 'Nikdy, za žiadnych okolností'],
      c: 0,
      e: 'Prilba sa sníma šetrne s fixáciou hlavy a krku, aby sa nezhoršilo možné poranenie chrbtice.'
    },
    {
      id: 'BEZ-010', cat: 7, groups: ['*'],
      q: 'Ako sa prejavuje šok u zraneného?',
      a: ['Bledá studená spotená koža, zrýchlený slabý pulz, nepokoj alebo apatia', 'Červená horúca koža a spomalený pulz', 'Zvýšená chuť do jedla'],
      c: 0,
      e: 'Zraneného v šoku uložíme, prikryjeme, upokojíme a nedávame mu piť ani jesť.'
    },
    {
      id: 'BEZ-011', cat: 7, groups: ['*'],
      q: 'Čo NEsmieme robiť zranenému v šoku?',
      a: ['Dávať mu piť, jesť alebo podávať lieky', 'Prikryť ho a upokojovať', 'Kontrolovať jeho dýchanie'],
      c: 0,
      e: 'Podanie tekutín môže skomplikovať následné ošetrenie a hrozí vdýchnutie pri zvracaní.'
    },
    {
      id: 'BEZ-012', cat: 7, groups: ['*'],
      q: 'Ako ošetríme popáleninu?',
      a: ['Chladíme čistou studenou vodou a prikryjeme sterilným krytím', 'Natrieme masťou alebo olejom', 'Prepichneme pľuzgiere'],
      c: 0,
      e: 'Chladenie zmierňuje bolesť a hĺbku poškodenia; masti a pľuzgiere sa neošetrujú svojpomocne.'
    },
    {
      id: 'BEZ-013', cat: 7, groups: ['*'],
      q: 'Ako zistíme, či postihnutý dýcha?',
      a: ['Zakloníme mu hlavu, uvoľníme dýchacie cesty a najviac 10 sekúnd sledujeme dýchanie',
          'Podržíme mu zrkadielko pred ústami aspoň minútu', 'Skontrolujeme pulz na zápästí'],
      c: 0,
      e: 'Lapavé dychy nie sú normálne dýchanie – vtedy sa začína resuscitácia.'
    },
    {
      id: 'BEZ-014', cat: 7, groups: ['*'],
      q: 'Ako postupujeme pri podozrení na poranenie chrbtice?',
      a: ['S postihnutým zbytočne nehýbeme a fixujeme hlavu v osi tela', 'Posadíme ho', 'Otočíme ho na brucho'],
      c: 0,
      e: 'Nesprávna manipulácia môže spôsobiť trvalé ochrnutie; čakáme na odbornú pomoc.'
    },
    {
      id: 'BEZ-015', cat: 7, groups: ['*'],
      q: 'Ako pôsobí alkohol na schopnosť viesť vozidlo?',
      a: ['Predlžuje reakčný čas, zhoršuje odhad vzdialenosti a zvyšuje sebavedomie vodiča',
          'Zlepšuje sústredenie', 'Nemá vplyv, ak vodič vypil len jedno pivo'],
      c: 0,
      e: 'Aj malé množstvo alkoholu zhoršuje pozornosť a odhad situácie – preto platí nulová tolerancia.'
    },
    {
      id: 'BEZ-016', cat: 7, groups: ['*'],
      q: 'Ako sa dá znížiť riziko mikrospánku pri dlhej jazde?',
      a: ['Pravidelnými prestávkami približne každé dve hodiny a dostatočným spánkom pred jazdou',
          'Zvýšením rýchlosti, aby jazda trvala kratšie', 'Nastavením kúrenia na vyššiu teplotu'],
      c: 0,
      e: 'Únava sa nedá „premôcť“ vôľou; jediné účinné riešenie je odpočinok.'
    },
    {
      id: 'BEZ-017', cat: 7, groups: ['*'],
      q: 'Prečo je nebezpečné jazdiť tesne za iným vozidlom?',
      a: ['Vodič nemá dostatok priestoru na reakciu a hrozí náraz zozadu', 'Zvyšuje sa spotreba paliva', 'Zhoršuje sa výhľad do zrkadiel'],
      c: 0,
      e: 'Nedodržanie bezpečnej vzdialenosti je jednou z najčastejších príčin nehôd.'
    },
    {
      id: 'BEZ-018', cat: 7, groups: ['*'],
      q: 'Ako sa má vodič správať k chodcom pri prechádzaní cez cestu za zníženej viditeľnosti?',
      a: ['Počítať s tým, že chodca nemusí včas vidieť, a znížiť rýchlosť najmä pri priechodoch',
          'Predpokladať, že chodec vozidlo vždy uvidí a počká', 'Používať diaľkové svetlá pri priechodoch'],
      c: 0,
      e: 'Chodec bez reflexných prvkov je za tmy viditeľný len na krátku vzdialenosť.'
    },
    {
      id: 'BEZ-019', cat: 7, groups: ['*'],
      q: 'Kedy musí mať chodec idúci po ceste mimo obce za zníženej viditeľnosti reflexné prvky?',
      a: ['Vždy, keď ide po krajnici alebo okraji vozovky za zníženej viditeľnosti mimo obce',
          'Nikdy, je to len odporúčanie', 'Len ak ide v skupine'],
      c: 0,
      e: 'Reflexné prvky predĺžia vzdialenosť, na ktorú vodič chodca uvidí, aj niekoľkonásobne.'
    },
    {
      id: 'BEZ-020', cat: 7, groups: ['*'],
      q: 'Čo je najčastejšou príčinou vážnych dopravných nehôd?',
      a: ['Neprimeraná rýchlosť a nevenovanie sa vedeniu vozidla', 'Zlý technický stav vozidiel', 'Nepriaznivé počasie'],
      c: 0,
      e: 'Rýchlosť rozhoduje o tom, či sa nehode dá zabrániť, aj o závažnosti následkov.'
    },
    {
      id: 'BEZ-021', cat: 7, groups: ['*'],
      q: 'Ako pomôže bezpečnostný pás pri náraze?',
      a: ['Zadrží telo, rozloží sily nárazu a zabráni vymršteniu z vozidla', 'Chráni len pred pokutou', 'Pomáha len pri rýchlosti nad 90 km/h'],
      c: 0,
      e: 'Aj náraz pri 50 km/h zodpovedá pádu z výšky niekoľkých poschodí – bez pásu je zranenie takmer isté.'
    },
    {
      id: 'BEZ-022', cat: 7, groups: ['*'],
      q: 'Ako sa má vodič zachovať, ak na diaľnici zbadá stojace vozidlo s výstražnými svetlami?',
      a: ['Znížiť rýchlosť, zvýšiť pozornosť a ak je to možné, prejsť do vzdialenejšieho jazdného pruhu',
          'Zachovať rýchlosť a prejsť tesne okolo neho', 'Zastaviť za ním a ponúknuť pomoc v jazdnom pruhu'],
      c: 0,
      e: 'Pri stojacom vozidle sa môžu na vozovke pohybovať ľudia – hrozí ich zrazenie.'
    },
    {
      id: 'BEZ-023', cat: 7, groups: ['*'],
      q: 'Prečo je používanie mobilného telefónu počas jazdy nebezpečné aj s hands-free?',
      a: ['Odvádza pozornosť vodiča od sledovania dopravnej situácie', 'Zhoršuje príjem signálu', 'Zvyšuje spotrebu paliva'],
      c: 0,
      e: 'Rozdelená pozornosť predlžuje reakčný čas podobne ako alkohol.'
    },
    {
      id: 'BEZ-024', cat: 7, groups: ['*'],
      q: 'Ako sa má správať vodič k cyklistom a chodcom v obytnej zóne?',
      a: ['Jazdiť najviac 20 km/h, dbať na zvýšenú opatrnosť a nesmie ich ohroziť', 'Používať zvukové znamenie, aby uvoľnili cestu', 'Jazdiť rovnako ako v ostatných uliciach'],
      c: 0,
      e: 'V obytnej zóne majú chodci prednosť a deti sa tam smú hrať na ceste.'
    },
    {
      id: 'BEZ-025', cat: 7, groups: ['*'],
      q: 'Ako postupujeme, ak zranený krváca z nosa?',
      a: ['Posadíme ho, hlavu mierne predklonený a stlačíme mäkkú časť nosa', 'Zakloníme mu hlavu dozadu', 'Uložíme ho na chrbát'],
      c: 0,
      e: 'Pri záklone hlavy krv steká do dýchacích ciest a žalúdka.'
    },
    {
      id: 'BEZ-026', cat: 7, groups: ['*'],
      q: 'Čo robíme, ak je postihnutý po nehode pri vedomí a sťažuje si na bolesť?',
      a: ['Upokojíme ho, zabránime prechladnutiu a sledujeme jeho stav do príchodu záchranárov',
          'Necháme ho prejsť sa, aby sa rozhýbal', 'Podáme mu lieky proti bolesti'],
      c: 0,
      e: 'Laik nepodáva lieky; dôležitý je psychický kontakt, teplo a sledovanie stavu.'
    }
  ]);
})();

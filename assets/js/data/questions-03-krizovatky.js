/* Okruh 3 – Prednosť v jazde, križovatky a jazda v jazdných pruhoch */
(function () {
  'use strict';
  BANK.add([
    {
      id: 'KRI-001', cat: 3, groups: ['*'],
      q: 'Kto má prednosť na križovatke, ktorá nie je označená dopravnými značkami ani riadená semaformi?',
      a: ['Vodič prichádzajúci sprava', 'Vodič prichádzajúci zľava', 'Vodič, ktorý ide rovno'],
      c: 0,
      e: 'Na neoznačenej križovatke platí pravidlo pravej ruky – prednosť má vozidlo prichádzajúce sprava.'
    },
    {
      id: 'KRI-002', cat: 3, groups: ['*'],
      q: 'Kto má prednosť, ak vodič odbočuje vľavo a oproti prichádza vozidlo idúce rovno?',
      a: ['Protiidúce vozidlo idúce rovno', 'Odbočujúce vozidlo', 'Ten, kto prišiel do križovatky skôr'],
      c: 0,
      e: 'Vodič odbočujúci vľavo musí dať prednosť protiidúcim vozidlám idúcim rovno alebo odbočujúcim vpravo.'
    },
    {
      id: 'KRI-003', cat: 3, groups: ['*'],
      q: 'Musí vodič odbočujúci vpravo alebo vľavo dať prednosť chodcom prechádzajúcim cez cestu, do ktorej odbočuje?',
      a: ['Áno, chodcom na priechode musí dať prednosť', 'Nie, chodci musia počkať', 'Len ak je priechod riadený semaforom'],
      c: 0,
      e: 'Pri odbočovaní musí vodič dať prednosť chodcom prechádzajúcim po priechode cez vozovku, do ktorej vchádza.'
    },
    {
      id: 'KRI-004', cat: 3, groups: ['*'],
      q: 'Kto má prednosť, ak sa hlavná cesta v križovatke lomí (mení smer)?',
      a: ['Vodič idúci po hlavnej ceste, ktorý sleduje jej priebeh podľa dodatkovej tabuľky',
          'Vždy vodič idúci rovno', 'Vždy vodič prichádzajúci sprava'],
      c: 0,
      e: 'Priebeh hlavnej cesty ukazuje dodatková tabuľka; vodič na hlavnej ceste má prednosť aj vtedy, ak musí odbočiť.'
    },
    {
      id: 'KRI-005', cat: 3, groups: ['*'],
      q: 'Kto má prednosť, ak vodič vychádza z poľnej cesty, lesnej cesty alebo z miesta mimo cesty?',
      a: ['Musí dať prednosť všetkým vozidlám na ceste, na ktorú vchádza', 'Má prednosť, ak prichádza sprava', 'Prednosť sa určuje podľa rýchlosti vozidiel'],
      c: 0,
      e: 'Pri vychádzaní z miesta mimo cesty (dvor, parkovisko, poľná cesta) musí vodič dať prednosť všetkým účastníkom premávky.'
    },
    {
      id: 'KRI-006', cat: 3, groups: ['*'],
      q: 'Ako sa určuje prednosť pri vjazde na kruhový objazd označený značkou „Kruhový objazd“ spolu so značkou „Daj prednosť v jazde!“?',
      a: ['Prednosť majú vozidlá, ktoré už jazdia po kruhovom objazde', 'Prednosť má vozidlo vchádzajúce do kruhu', 'Platí pravidlo pravej ruky'],
      c: 0,
      e: 'Ak je pod značkou kruhového objazdu značka „Daj prednosť v jazde!“, vodič vchádzajúci do kruhu dáva prednosť.'
    },
    {
      id: 'KRI-007', cat: 3, groups: ['*'],
      q: 'Kto má prednosť v križovatke pred vozidlom idúcim po vedľajšej ceste?',
      a: ['Vozidlo idúce po hlavnej ceste', 'Vozidlo, ktoré je rýchlejšie', 'Vozidlo prichádzajúce zľava'],
      c: 0,
      e: 'Vodič prichádzajúci po vedľajšej ceste musí dať prednosť všetkým vozidlám na hlavnej ceste.'
    },
    {
      id: 'KRI-008', cat: 3, groups: ['*'],
      q: 'Kto má prednosť, ak vodič odbočuje vľavo a súčasne z ľavej strany prichádza električka?',
      a: ['Električka – vodič jej musí dať prednosť', 'Vodič odbočujúceho vozidla', 'Ten, kto dá znamenie skôr'],
      c: 0,
      e: 'Vodič odbočujúci vľavo musí dať prednosť električke idúcej v oboch smeroch, ak križuje jej dráhu.'
    },
    {
      id: 'KRI-009', cat: 3, groups: ['*'],
      q: 'Kedy má električka prednosť pred ostatnými vozidlami?',
      a: ['Keď odbočuje cez jazdný pruh, po ktorom ide iné vozidlo, a dáva znamenie o zmene smeru',
          'Vždy a za všetkých okolností', 'Nikdy, električka nemá prednosť'],
      c: 0,
      e: 'Ak električka križuje smer jazdy vozidla a dáva znamenie o zmene smeru jazdy, ostatní vodiči jej musia dať prednosť.'
    },
    {
      id: 'KRI-010', cat: 3, groups: ['*'],
      q: 'Ako sa má vodič zachovať, ak policajt riadi premávku a jeho pokyn je v rozpore so svetelným signálom?',
      a: ['Riadi sa pokynmi policajta', 'Riadi sa svetelným signálom', 'Zastaví a čaká, kým sa situácia vyjasní'],
      c: 0,
      e: 'Pokyny policajta sú nadradené svetelným signálom aj dopravným značkám.'
    },
    {
      id: 'KRI-011', cat: 3, groups: ['*'],
      q: 'Čo znamená pokyn policajta „upažené obe ruky alebo jedna ruka“?',
      a: ['Pre vodičov, ku ktorým je policajt otočený čelom alebo chrbtom, znamená „Stoj!“',
          'Znamená voľno pre všetkých', 'Znamená zákaz odbočovania vpravo'],
      c: 0,
      e: 'Pri upažených rukách je voľno pre smery, ku ktorým je policajt otočený bokom.'
    },
    {
      id: 'KRI-012', cat: 3, groups: ['*'],
      q: 'Čo znamená pokyn policajta „vztýčená ruka predpažená hore“?',
      a: ['Stoj – pre všetky smery, s výnimkou vodičov, ktorí už nemôžu bezpečne zastaviť',
          'Voľno pre všetky smery', 'Zvýšená opatrnosť'],
      c: 0,
      e: 'Vztýčená ruka znamená „Pozor!“ – pripravte sa zastaviť; vodiči, ktorí sú už príliš blízko, križovatku dokončia.'
    },
    {
      id: 'KRI-013', cat: 3, groups: ['*'],
      q: 'Ako má vodič odbočiť vpravo?',
      a: ['Zaradiť sa čo najbližšie k pravému okraju vozovky a odbočiť pri pravom okraji',
          'Zaradiť sa do stredu vozovky', 'Odbočiť z ľavého jazdného pruhu'],
      c: 0,
      e: 'Pred odbočením vpravo sa vodič zaradí čo najbližšie k pravému okraju vozovky.'
    },
    {
      id: 'KRI-014', cat: 3, groups: ['*'],
      q: 'Ako sa vodič zaradí pred odbočením vľavo na obojsmernej ceste?',
      a: ['Čo najbližšie k stredu vozovky (k deliacej čiare)', 'K pravému okraju vozovky', 'Do protismerného jazdného pruhu'],
      c: 0,
      e: 'Pred odbočením vľavo sa vodič zaradí čo najviac vľavo v časti vozovky určenej pre jeho smer jazdy.'
    },
    {
      id: 'KRI-015', cat: 3, groups: ['*'],
      q: 'Kto dáva prednosť pri súbežnej jazde, keď sa počet jazdných pruhov znižuje (zipsovanie)?',
      a: ['Vodiči sa musia striedavo radiť po jednom vozidle do priebežného pruhu',
          'Vodič v priebežnom pruhu musí vždy zastaviť', 'Vodič v končiacom pruhu má prednosť'],
      c: 0,
      e: 'Pri zaraďovaní z končiaceho pruhu sa vodiči striedajú po jednom vozidle – ide o tzv. zipsovanie.'
    },
    {
      id: 'KRI-016', cat: 3, groups: ['*'],
      q: 'Musí vodič dať prednosť vozidlu, ktoré prichádza sprava po ceste označenej ako vedľajšia?',
      a: ['Nie, ak sám ide po hlavnej ceste', 'Áno, pravidlo pravej ruky platí vždy', 'Áno, ale len v obci'],
      c: 0,
      e: 'Pravidlo pravej ruky platí len tam, kde prednosť nie je upravená značkami alebo svetelnou signalizáciou.'
    },
    {
      id: 'KRI-017', cat: 3, groups: ['*'],
      q: 'Ako sa vodič musí zachovať, keď na križovatke pri značke „Daj prednosť v jazde!“ nemá dostatočný rozhľad?',
      a: ['Prispôsobiť rýchlosť, prípadne zastaviť, a pomaly sa vysunúť na miesto s rozhľadom',
          'Rýchlo prejsť križovatkou', 'Použiť zvukové znamenie a pokračovať'],
      c: 0,
      e: 'Vodič musí jazdiť tak, aby dokázal dať prednosť; ak nevidí, musí zastaviť a opatrne sa vysunúť.'
    },
    {
      id: 'KRI-018', cat: 3, groups: ['*'],
      q: 'Kto má prednosť pri vchádzaní na cestu z parkoviska alebo od čerpacej stanice?',
      a: ['Vodiči jazdiaci po ceste – vychádzajúce vozidlo dáva prednosť', 'Vychádzajúce vozidlo, ak je väčšie', 'Vozidlo prichádzajúce sprava po ceste'],
      c: 0,
      e: 'Vychádzanie z miesta mimo cesty nie je križovatka – vodič musí dať prednosť všetkým vozidlám aj chodcom.'
    },
    {
      id: 'KRI-019', cat: 3, groups: ['*'],
      q: 'Kedy je vodič povinný dať prednosť vozidlám aj chodcom pri cúvaní?',
      a: ['Vždy – pri cúvaní nesmie ohroziť ani obmedziť ostatných účastníkov premávky',
          'Len ak cúva na parkovisku', 'Len v obci'],
      c: 0,
      e: 'Pri cúvaní a otáčaní nesmie vodič ohroziť ani obmedziť ostatných účastníkov cestnej premávky.'
    },
    {
      id: 'KRI-020', cat: 3, groups: ['*'],
      q: 'Ako sa má vodič zachovať, keď v križovatke zbadá vozidlo s právom prednostnej jazdy so zapnutým modrým svetlom a sirénou?',
      a: ['Umožniť mu prednostný prejazd, aj keby sám mal prednosť v jazde', 'Trvať na svojej prednosti', 'Zrýchliť a opustiť križovatku pred ním'],
      c: 0,
      e: 'Vozidlá s právom prednostnej jazdy majú prednosť pred všetkými; ostatní vodiči im musia uvoľniť cestu.'
    },
    {
      id: 'KRI-021', cat: 3, groups: ['*'],
      q: 'Kedy smie vodič predchádzať v križovatke?',
      a: ['Ak ide po hlavnej ceste a predchádza vozidlo odbočujúce vľavo, prípadne pri jazde v pruhoch',
          'Nikdy a za žiadnych okolností', 'Vždy, ak má voľný ľavý pruh'],
      c: 0,
      e: 'Predchádzať v križovatke je zakázané; výnimkou je jazda po hlavnej ceste, jazda v pruhoch a predchádzanie vpravo pri odbočovaní vľavo.'
    },
    {
      id: 'KRI-022', cat: 3, groups: ['*'],
      q: 'Kedy vodič nesmie vojsť na križovatku, aj keď má prednosť v jazde alebo zelenú?',
      a: ['Ak by musel zastaviť na križovatke a blokovať priečnu premávku', 'Ak sa blíži k obci', 'Ak je za ním rad vozidiel'],
      c: 0,
      e: 'Do križovatky sa vchádza len vtedy, keď dopravná situácia dovoľuje bez zastavenia križovatku opustiť.'
    },
    {
      id: 'KRI-023', cat: 3, groups: ['*'],
      q: 'Ako sa má vodič zachovať pri jazde cez križovatku so značkou „Hlavná cesta“, ak z vedľajšej cesty vchádza vozidlo do jeho jazdnej dráhy?',
      a: ['Prispôsobiť jazdu, aby nedošlo k nehode – prednosť neoprávňuje ohroziť ostatných',
          'Pokračovať rovnakou rýchlosťou, prednosť má on', 'Použiť diaľkové svetlá'],
      c: 0,
      e: 'Prednosť v jazde nie je právom ohroziť iných; vodič musí predchádzať dopravnej nehode.'
    },
    {
      id: 'KRI-024', cat: 3, groups: ['*'],
      q: 'Kto je povinný dať prednosť pri zúženej ceste, kde je značka „Daj prednosť protiidúcim vozidlám“?',
      a: ['Vodič idúci v smere, pre ktorý je značka určená', 'Vodič, ktorý prišiel k zúženiu neskôr', 'Vodič väčšieho vozidla'],
      c: 0,
      e: 'Značka určuje, ktorý smer musí počkať; opačný smer má prednosť.'
    },
    {
      id: 'KRI-025', cat: 3, groups: ['*'],
      q: 'Ako sa určuje prednosť v jazde, ak svetelná signalizácia nefunguje (je vypnutá)?',
      a: ['Podľa dopravných značiek, a ak nie sú, podľa pravidla pravej ruky', 'Prednosť má vždy vozidlo idúce rovno', 'Prednosť má vodič, ktorý prišiel skôr'],
      c: 0,
      e: 'Pri nefunkčnej signalizácii sa prednosť riadi zvislými dopravnými značkami, inak platí pravidlo pravej ruky.'
    },
    {
      id: 'KRI-026', cat: 3, groups: ['*'],
      q: 'Ako má vodič prechádzať cez koľaje električky pri odbočovaní, ak je električková dráha v strede vozovky?',
      a: ['Prejsť cez koľaje až vtedy, keď neohrozí električku, a nezastaviť na koľajach',
          'Zastaviť na koľajach a počkať na medzeru', 'Prejsť rýchlo bez ohliadnutia'],
      c: 0,
      e: 'Vodič nesmie zastaviť na električkovej dráhe a musí umožniť električke plynulú jazdu.'
    },
    {
      id: 'KRI-027', cat: 3, groups: ['*'],
      q: 'Kto má prednosť, ak dve vozidlá prichádzajú k neoznačenej križovatke z ciest rovnakého významu oproti sebe a obe odbočujú vľavo?',
      a: ['Vozidlá sa vzájomne obídu vľavo a prejdú za sebou – prednosť sa v tomto prípade neurčuje pravidlom pravej ruky',
          'Vždy vozidlo prichádzajúce sprava', 'Vozidlo, ktoré prišlo skôr'],
      c: 0,
      e: 'Protiidúce vozidlá odbočujúce vľavo sa vyhýbajú vľavo a prejdú okolo seba, ak dopravná situácia nevyžaduje inak.'
    },
    {
      id: 'KRI-028', cat: 3, groups: ['*'],
      q: 'Musí vodič dať prednosť cyklistovi prechádzajúcemu cez priechod pre cyklistov?',
      a: ['Áno, cyklistu na priechode pre cyklistov nesmie ohroziť', 'Nie, cyklista musí vždy počkať', 'Len mimo obce'],
      c: 0,
      e: 'Vodič nesmie ohroziť cyklistu prechádzajúceho cez priechod pre cyklistov.'
    },
    {
      id: 'KRI-029', cat: 3, groups: ['*'],
      q: 'Ako sa má vodič zachovať pri jazde v jazdných pruhoch, ak sa chce presunúť do vedľajšieho pruhu?',
      a: ['Dať znamenie a nesmie ohroziť ani obmedziť vodiča idúceho vo vedľajšom pruhu',
          'Presunúť sa okamžite, ostatní ho musia pustiť', 'Presúvať sa len mimo obce'],
      c: 0,
      e: 'Pri prechádzaní z pruhu do pruhu má prednosť vodič idúci v pruhu, do ktorého sa vodič chce zaradiť.'
    },
    {
      id: 'KRI-030', cat: 3, groups: ['*'],
      q: 'Ako sa vodič zachová pred železničným priecestím, keď pred ním stojí vozidlo?',
      a: ['Zastaví v bezpečnej vzdialenosti za ním a na priecestie vojde, až keď ho môže bez zastavenia opustiť',
          'Predbehne ho a prejde priecestie', 'Zastaví na priecestí a počká'],
      c: 0,
      e: 'Na priecestie sa vchádza, len ak je za ním voľné miesto na jeho opustenie bez zastavenia.'
    },
    {
      id: 'KRI-031', cat: 3, groups: ['*'],
      q: 'Kto má prednosť pri vjazde do kruhového objazdu, ktorý nie je označený značkou „Daj prednosť v jazde!“?',
      a: ['Platí všeobecná úprava prednosti – rozhodujú značky, inak pravidlo pravej ruky',
          'Vždy vozidlá v kruhovom objazde', 'Vždy vozidlá vchádzajúce do kruhového objazdu'],
      c: 0,
      e: 'Prednosť v kruhovom objazde vyplýva z dopravných značiek; bez nich sa uplatní pravidlo pravej ruky.'
    },
    {
      id: 'KRI-032', cat: 3, groups: ['*'],
      q: 'Ako sa má vodič zachovať, keď chce prejsť cez priechod pre chodcov, na ktorý práve vstupuje chodec?',
      a: ['Zastaviť a umožniť chodcovi prejsť', 'Prejsť rýchlo pred chodcom', 'Zatrúbiť a pokračovať'],
      c: 0,
      e: 'Vodič je povinný umožniť chodcovi, ktorý je na priechode alebo naň vstupuje, bezpečne prejsť.'
    }
  ]);
})();

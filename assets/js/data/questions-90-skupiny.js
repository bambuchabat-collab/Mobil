/* Doplnkové otázky viazané na konkrétnu skupinu vodičského oprávnenia.
   Pridávajú sa k spoločnému základu podľa poľa `groups`. */
(function () {
  'use strict';
  BANK.add([
    /* ---------------- Skupina A – motocykle ---------------- */
    {
      id: 'SKA-001', cat: 4, groups: ['A'],
      q: 'Kto musí mať na motocykli počas jazdy riadne upevnenú ochrannú prilbu?',
      a: ['Vodič aj spolujazdec', 'Len vodič', 'Prilba je povinná len mimo obce'],
      c: 0,
      e: 'Ochrannú prilbu musí mať vodič aj prepravovaná osoba, prilba musí byť riadne upevnená.'
    },
    {
      id: 'SKA-002', cat: 4, groups: ['A'],
      q: 'Od akého veku možno získať vodičské oprávnenie skupiny A1?',
      a: ['16 rokov', '15 rokov', '18 rokov'], c: 0,
      e: 'Skupina A1 (ľahké motocykle do 125 cm³ a 11 kW) sa udeľuje najskôr vo veku 16 rokov.'
    },
    {
      id: 'SKA-003', cat: 4, groups: ['A'],
      q: 'Aké obmedzenie výkonu platí pre motocykle skupiny A2?',
      a: ['Najviac 35 kW', 'Najviac 11 kW', 'Výkon nie je obmedzený'], c: 0,
      e: 'Skupina A2 zahŕňa motocykle s výkonom do 35 kW a určeným pomerom výkonu k hmotnosti.'
    },
    {
      id: 'SKA-004', cat: 4, groups: ['A'],
      q: 'Smie vodič motocykla prepravovať dieťa mladšie ako 12 rokov?',
      a: ['Nie, na motocykli sa takéto dieťa prepravovať nesmie', 'Áno, ak má prilbu', 'Áno, ak sedí pred vodičom'],
      c: 0,
      e: 'Dieťa mladšie ako 12 rokov sa na motocykli prepravovať nesmie.'
    },
    {
      id: 'SKA-005', cat: 1, groups: ['A'],
      q: 'Smie motocyklista prechádzať medzi radmi stojacich vozidiel (tzv. filtrovanie)?',
      a: ['Nie, aj motocyklista musí jazdiť v jazdnom pruhu a rešpektovať pravidlá', 'Áno, kedykoľvek', 'Áno, ak jazdí do 30 km/h'],
      c: 0,
      e: 'Predchádzanie kolóny pomedzi vozidlá je v premávke zakázané a mimoriadne rizikové.'
    },
    {
      id: 'SKA-006', cat: 5, groups: ['A'],
      q: 'Ktorá brzda má na motocykli väčší brzdný účinok?',
      a: ['Predná – ale používať treba obe súčasne a plynulo', 'Zadná – prednú netreba používať', 'Obe majú rovnaký účinok'],
      c: 0,
      e: 'Pri brzdení sa hmotnosť prenáša dopredu; prudké použitie samotnej prednej brzdy však môže spôsobiť pád.'
    },
    {
      id: 'SKA-007', cat: 5, groups: ['A'],
      q: 'Ako má motocyklista prechádzať zákrutou?',
      a: ['Spomaliť pred zákrutou, v zákrute jazdiť plynulo s pohľadom smerom von zo zákruty',
          'Brzdiť čo najviac v zákrute', 'Zaradiť neutrál a nechať motocykel voľne prejsť'],
      c: 0,
      e: 'Brzdenie v naklonenom motocykli výrazne zvyšuje riziko šmyku a pádu.'
    },
    {
      id: 'SKA-008', cat: 5, groups: ['A'],
      q: 'Prečo sú pre motocyklistu nebezpečné kanalizačné poklopy, vodorovné značenie a koľajnice?',
      a: ['Za mokra sú mimoriadne klzké a hrozí na nich strata priľnavosti', 'Poškodzujú pneumatiky', 'Rušia elektroniku motocykla'],
      c: 0,
      e: 'Na klzkom povrchu treba jazdiť priamo, bez brzdenia a bez zmien plynu.'
    },
    {
      id: 'SKA-009', cat: 6, groups: ['A'],
      q: 'Čo treba na motocykli kontrolovať pred každou jazdou?',
      a: ['Tlak a stav pneumatík, brzdy, osvetlenie a napnutie reťaze', 'Len množstvo paliva', 'Len funkčnosť klaksónu'],
      c: 0,
      e: 'Motocykel odpúšťa menej než auto – aj drobná porucha môže viesť k pádu.'
    },
    {
      id: 'SKA-010', cat: 7, groups: ['A'],
      q: 'Prečo je motocyklista v premávke ohrozenejší ako vodič auta?',
      a: ['Je horšie viditeľný, nemá karosériu a pri páde nie je chránený', 'Má vždy horšie brzdy', 'Nesmie používať diaľnicu'],
      c: 0,
      e: 'Motocyklista by mal počítať s tým, že ho iní vodiči prehliadnu, a nosiť ochranné oblečenie a reflexné prvky.'
    },
    {
      id: 'SKA-011', cat: 7, groups: ['A'],
      q: 'Aké ochranné pomôcky odporúčame motocyklistovi okrem prilby?',
      a: ['Rukavice, pevnú obuv, chrániče a odev z odolného materiálu', 'Stačí prilba', 'Reflexnú vestu namiesto prilby'],
      c: 0,
      e: 'Ochranné oblečenie výrazne znižuje rozsah poranení pri páde.'
    },
    {
      id: 'SKA-012', cat: 1, groups: ['A'],
      q: 'Ako musí byť motocykel osvetlený počas jazdy?',
      a: ['Musí mať rozsvietené stretávacie svetlo počas celého dňa', 'Svetlá sú potrebné len v noci', 'Postačuje obrysové svetlo'],
      c: 0,
      e: 'Trvalé svietenie zvyšuje viditeľnosť motocykla, ktorý je v premávke ľahko prehliadnuteľný.'
    },

    /* ---------------- Skupina B – osobné vozidlá ---------------- */
    {
      id: 'SKB-001', cat: 4, groups: ['B'],
      q: 'Aké vozidlá oprávňuje viesť skupina B?',
      a: ['Motorové vozidlá do 3 500 kg s najviac 8 miestami na sedenie okrem miesta vodiča',
          'Všetky vozidlá do 7 500 kg', 'Len vozidlá s automatickou prevodovkou'],
      c: 0,
      e: 'K vozidlu skupiny B možno pripojiť príves do 750 kg, prípadne ťažší pri splnení podmienok.'
    },
    {
      id: 'SKB-002', cat: 4, groups: ['B'],
      q: 'Aký príves smie vodič skupiny B pripojiť bez ďalšieho oprávnenia?',
      a: ['Príves s najväčšou prípustnou celkovou hmotnosťou do 750 kg', 'Ľubovoľný príves', 'Príves do 2 000 kg'],
      c: 0,
      e: 'Ťažší príves si vyžaduje rozšírenie oprávnenia (kód 96 alebo skupina B+E) podľa hmotnosti jazdnej súpravy.'
    },
    {
      id: 'SKB-003', cat: 4, groups: ['B'],
      q: 'Čo znamená obmedzujúci kód 78 vo vodičskom preukaze?',
      a: ['Držiteľ smie viesť len vozidlá s automatickou prevodovkou', 'Držiteľ smie jazdiť len cez deň', 'Držiteľ smie jazdiť len v obci'],
      c: 0,
      e: 'Kód 78 sa uvádza, ak bola skúška vykonaná na vozidle s automatickou prevodovkou.'
    },
    {
      id: 'SKB-004', cat: 1, groups: ['B'],
      q: 'Ako má vodič a posádka vystupovať z vozidla zastaveného pri okraji vozovky?',
      a: ['Až po presvedčení sa, že tým neohrozia iných účastníkov premávky, najmä cyklistov',
          'Kedykoľvek, ostatní musia dávať pozor', 'Vždy len na strane vozovky'],
      c: 0,
      e: 'Otvorené dvere sú častou príčinou zrážok s cyklistami; pomáha technika otvárania dverí vzdialenejšou rukou.'
    },
    {
      id: 'SKB-005', cat: 6, groups: ['B'],
      q: 'Ako sa má prepravovať batožina v osobnom vozidle?',
      a: ['Zaistená v batožinovom priestore, ťažké predmety čo najnižšie a dopredu', 'Voľne na zadnej odkladacej doske', 'Na sedadle spolujazdca bez zaistenia'],
      c: 0,
      e: 'Nezaistený predmet sa pri náraze mení na nebezpečný projektil.'
    },
    {
      id: 'SKB-006', cat: 5, groups: ['B'],
      q: 'Ako ovplyvní plne obsadené vozidlo s batožinou jazdné vlastnosti?',
      a: ['Predĺži brzdnú dráhu a zhorší ovládateľnosť, treba upraviť aj sklon svetlometov',
          'Vozidlo brzdí lepšie', 'Nemá to vplyv'],
      c: 0,
      e: 'Pri plnom zaťažení treba znížiť rýchlosť, zvýšiť odstup a skontrolovať tlak v pneumatikách.'
    },
    {
      id: 'SKB-007', cat: 6, groups: ['B'],
      q: 'Prečo treba pri jazde s prívesom upraviť spätné zrkadlá alebo použiť prídavné zrkadlá?',
      a: ['Aby vodič videl za koniec jazdnej súpravy', 'Kvôli zníženiu spotreby', 'Nie je to potrebné'],
      c: 0,
      e: 'Bez dostatočného výhľadu dozadu nie je možné bezpečne predchádzať ani meniť jazdný pruh.'
    },
    {
      id: 'SKB-008', cat: 3, groups: ['B'],
      q: 'Ako má vodič postupovať pri parkovaní cúvaním na miesto pozdĺž vozovky?',
      a: ['Priebežne sledovať okolie, prípadne využiť pomoc inej osoby, a nesmie ohroziť ostatných',
          'Cúvať rýchlo, aby neblokoval premávku', 'Spoliehať sa len na parkovacie senzory'],
      c: 0,
      e: 'Senzory a kamery nevidia všetko – najmä nízke prekážky a deti.'
    },
    {
      id: 'SKB-009', cat: 1, groups: ['B'],
      q: 'Smie vodič nechať v stojacom vozidle bežať motor bez potreby?',
      a: ['Nie, zbytočné státie s bežiacim motorom je zakázané', 'Áno, kvôli kúreniu', 'Áno, ak sedí vo vozidle'],
      c: 0,
      e: 'Vodič nesmie zbytočne nechať bežať motor stojaceho vozidla – ide o zbytočné znečisťovanie ovzdušia a hluk.'
    },
    {
      id: 'SKB-010', cat: 4, groups: ['B'],
      q: 'Kedy je vodič povinný zabezpečiť vozidlo proti samovoľnému pohybu?',
      a: ['Vždy, keď opustí vozidlo – zatiahnuť parkovaciu brzdu, prípadne zaradiť rýchlostný stupeň',
          'Len pri parkovaní v svahu', 'Len ak vo vozidle ostanú deti'],
      c: 0,
      e: 'Vodič musí urobiť opatrenia, aby vozidlo nemohlo ohroziť premávku ani sa samovoľne rozísť.'
    },
    {
      id: 'SKB-011', cat: 7, groups: ['B'],
      q: 'Prečo je nebezpečné nechať dieťa alebo zviera v zaparkovanom vozidle za horúceho počasia?',
      a: ['Teplota vo vozidle rýchlo stúpa a hrozí prehriatie organizmu', 'Vozidlo sa môže samovoľne rozísť', 'Zvyšuje sa spotreba paliva'],
      c: 0,
      e: 'Vnútri vozidla môže teplota za pár minút vystúpiť na životu nebezpečnú úroveň.'
    },
    {
      id: 'SKB-012', cat: 4, groups: ['B'],
      q: 'Musí mať vodič skupiny B pri jazde s prívesom doklady aj od prívesu?',
      a: ['Áno, osvedčenie o evidencii prívesu aj doklad o jeho poistení', 'Nie, stačia doklady od ťažného vozidla', 'Áno, ale len mimo obce'],
      c: 0,
      e: 'Príves je samostatné vozidlo s vlastnou evidenciou a poistením.'
    },

    /* ---------------- Skupina C – nákladné vozidlá ---------------- */
    {
      id: 'SKC-001', cat: 1, groups: ['C', 'D'],
      q: 'Aká je najvyššia dovolená rýchlosť vozidla nad 3 500 kg mimo obce a na diaľnici?',
      a: ['80 km/h mimo obce a 90 km/h na diaľnici', '90 km/h mimo obce a 130 km/h na diaľnici', '70 km/h mimo obce a 80 km/h na diaľnici'],
      c: 0,
      e: 'Pre ťažké vozidlá platia nižšie rýchlostné limity než pre osobné automobily.'
    },
    {
      id: 'SKC-002', cat: 4, groups: ['C'],
      q: 'Aký je základný vek na udelenie vodičského oprávnenia skupiny C?',
      a: ['21 rokov (v spojení s kvalifikačnou kartou vodiča aj skôr)', '18 rokov bez výnimky', '24 rokov'],
      c: 0,
      e: 'Nižší vek je možný pri absolvovaní základnej kvalifikácie a získaní kvalifikačnej karty vodiča.'
    },
    {
      id: 'SKC-003', cat: 4, groups: ['C', 'D'],
      q: 'Ako dlho smie vodič v nákladnej doprave viesť vozidlo bez prestávky?',
      a: ['Najviac 4,5 hodiny, potom nasleduje prestávka najmenej 45 minút', 'Najviac 8 hodín', 'Bez obmedzenia, ak sa cíti oddýchnutý'],
      c: 0,
      e: 'Prestávku možno rozdeliť na 15 a 30 minút; dodržiavanie sleduje tachograf.'
    },
    {
      id: 'SKC-004', cat: 4, groups: ['C', 'D'],
      q: 'Na čo slúži tachograf?',
      a: ['Zaznamenáva rýchlosť, prejazdenú vzdialenosť a časy jazdy a odpočinku vodiča', 'Meria spotrebu paliva', 'Reguluje výkon motora'],
      c: 0,
      e: 'Manipulácia s tachografom je závažným porušením predpisov v nákladnej a autobusovej doprave.'
    },
    {
      id: 'SKC-005', cat: 6, groups: ['C'],
      q: 'Ako musí byť zaistený náklad na nákladnom vozidle?',
      a: ['Upínacími pásmi, sieťami alebo inými prostriedkami tak, aby sa pri brzdení a v zákrutách neposunul',
          'Stačí, ak je náklad ťažký', 'Postačuje plachta'],
      c: 0,
      e: 'Nezaistený náklad pri prudkom brzdení pokračuje v pohybe a môže preraziť kabínu alebo spadnúť na cestu.'
    },
    {
      id: 'SKC-006', cat: 5, groups: ['C', 'D'],
      q: 'Prečo musí vodič dlhého vozidla pri odbočovaní vpravo dávať zvýšený pozor na cyklistov a chodcov?',
      a: ['Zadná časť vozidla opisuje menší oblúk (vlečná krivka) a vzniká veľký mŕtvy uhol',
          'Pretože vozidlo v zákrute zrýchľuje', 'Pretože sa zhoršuje brzdný účinok'],
      c: 0,
      e: 'Nehody pri odbočovaní vpravo patria k najzávažnejším v mestskej premávke.'
    },
    {
      id: 'SKC-007', cat: 5, groups: ['C'],
      q: 'Ako sa má vodič nákladného vozidla správať pri dlhom klesaní?',
      a: ['Zaradiť nižší prevodový stupeň a využiť odľahčovaciu brzdu (retardér), aby sa neprehriali brzdy',
          'Ísť na neutrál a brzdiť prevádzkovou brzdou', 'Zvýšiť rýchlosť pre lepšie chladenie bŕzd'],
      c: 0,
      e: 'Trvalé brzdenie prevádzkovou brzdou vedie k jej prehriatiu a úplnej strate účinku.'
    },
    {
      id: 'SKC-008', cat: 6, groups: ['C', 'D'],
      q: 'Čo musí vodič skontrolovať pri vozidle so vzduchovými brzdami pred jazdou?',
      a: ['Tlak vzduchu v sústave a odvodnenie vzduchojemov, tesnosť sústavy', 'Len hladinu oleja', 'Nič, systém je bezúdržbový'],
      c: 0,
      e: 'Pri nízkom tlaku vzduchu sa brzdy nedajú uvoľniť alebo strácajú účinok.'
    },
    {
      id: 'SKC-009', cat: 2, groups: ['C'],
      q: 'Čo znamená značka so symbolom nákladného vozidla a údajom o hmotnosti v červenom kruhu?',
      a: ['Zákaz vjazdu vozidiel, ktorých hmotnosť presahuje uvedenú hranicu', 'Odporúčanú trasu pre kamióny', 'Parkovisko pre nákladné vozidlá'],
      c: 0,
      e: 'Vodič ťažkého vozidla musí sledovať aj obmedzenia výšky, šírky a dĺžky.'
    },
    {
      id: 'SKC-010', cat: 6, groups: ['C'],
      q: 'Prečo musí vodič nákladného vozidla poznať jeho výšku?',
      a: ['Kvôli podjazdom, mostom a tunelom s obmedzenou výškou', 'Kvôli výpočtu spotreby', 'Kvôli parkovacej známke'],
      c: 0,
      e: 'Náraz do podjazdu patrí k typickým nehodám nákladných vozidiel a spôsobuje veľké škody.'
    },
    {
      id: 'SKC-011', cat: 4, groups: ['C', 'D'],
      q: 'Čo je kvalifikačná karta vodiča (KKV)?',
      a: ['Doklad o odbornej spôsobilosti vodiča v nákladnej alebo autobusovej doprave', 'Doklad o poistení vozidla', 'Náhrada vodičského preukazu'],
      c: 0,
      e: 'Vodič z povolania musí absolvovať základnú kvalifikáciu a pravidelný výcvik.'
    },
    {
      id: 'SKC-012', cat: 7, groups: ['C'],
      q: 'Ako sa má vodič zachovať pri preprave nebezpečného nákladu (ADR)?',
      a: ['Dodržiavať predpísané označenie vozidla, výbavu a pokyny pre prípad nehody', 'Prepravovať ho ako bežný náklad', 'Prepravovať ho len v noci'],
      c: 0,
      e: 'Vodič musí mať osobitné školenie ADR a pri nehode postupovať podľa písomných pokynov.'
    },

    /* ---------------- Skupina D – autobusy ---------------- */
    {
      id: 'SKD-001', cat: 4, groups: ['D'],
      q: 'Aký je základný vek na udelenie vodičského oprávnenia skupiny D?',
      a: ['24 rokov (skôr len pri splnení podmienok odbornej kvalifikácie)', '18 rokov', '30 rokov'],
      c: 0,
      e: 'Nižší vek je možný pri získaní základnej kvalifikácie, spravidla s obmedzením typu prepravy.'
    },
    {
      id: 'SKD-002', cat: 1, groups: ['D'],
      q: 'Kedy smie vodič autobusu otvoriť dvere pre cestujúcich?',
      a: ['Až po úplnom zastavení vozidla na zastávke', 'Krátko pred zastavením, aby sa urýchlil nástup', 'Kedykoľvek počas pomalej jazdy'],
      c: 0,
      e: 'Otvorenie dverí za jazdy ohrozuje cestujúcich aj ostatných účastníkov premávky.'
    },
    {
      id: 'SKD-003', cat: 1, groups: ['D'],
      q: 'Ako má vodič autobusu vychádzať zo zastávky v obci?',
      a: ['Dať znamenie o zmene smeru jazdy a vychádzať, až keď neohrozí ostatných vodičov',
          'Vyjsť okamžite, ostatní musia zastaviť', 'Vychádzať bez znamenia'],
      c: 0,
      e: 'Ostatní vodiči sú povinní umožniť autobusu vyjsť, vodič autobusu ich však nesmie ohroziť.'
    },
    {
      id: 'SKD-004', cat: 4, groups: ['D'],
      q: 'Čo musí vodič autobusu zabezpečiť pri preprave osôb?',
      a: ['Aby počet prepravovaných osôb nepresiahol povolený počet a aby boli dodržané podmienky bezpečnej prepravy',
          'Len výber cestovného', 'Aby všetci cestujúci sedeli aj v mestskej doprave'],
      c: 0,
      e: 'Prekročenie počtu osôb a nedodržanie podmienok prepravy ohrozuje bezpečnosť všetkých cestujúcich.'
    },
    {
      id: 'SKD-005', cat: 4, groups: ['D'],
      q: 'Kedy sa musia cestujúci v autobuse pripútať bezpečnostným pásom?',
      a: ['Ak je sedadlo vybavené bezpečnostným pásom, cestujúci sa musí pripútať', 'Nikdy', 'Len počas jazdy po diaľnici'],
      c: 0,
      e: 'Vodič alebo prevádzkovateľ musí cestujúcich o povinnosti pripútať sa informovať.'
    },
    {
      id: 'SKD-006', cat: 6, groups: ['D'],
      q: 'Aké bezpečnostné vybavenie musí byť v autobuse dostupné?',
      a: ['Hasiaci prístroj, lekárnička a označené núdzové východy s kladivkom', 'Len lekárnička', 'Len hasiaci prístroj'],
      c: 0,
      e: 'Vodič musí vedieť, kde sa výbava nachádza, a v prípade nehody riadiť evakuáciu.'
    },
    {
      id: 'SKD-007', cat: 7, groups: ['D'],
      q: 'Ako má vodič autobusu postupovať pri nehode alebo požiari vozidla?',
      a: ['Zastaviť na bezpečnom mieste, evakuovať cestujúcich a privolať pomoc', 'Pokračovať do najbližšej zastávky', 'Nechať cestujúcich vo vozidle a hasiť požiar'],
      c: 0,
      e: 'Prvoradá je evakuácia cestujúcich do bezpečnej vzdialenosti od vozidla.'
    },
    {
      id: 'SKD-008', cat: 5, groups: ['D'],
      q: 'Prečo musí vodič autobusu jazdiť mimoriadne plynulo?',
      a: ['Stojaci cestujúci môžu pri prudkom brzdení alebo zrýchlení spadnúť a zraniť sa',
          'Kvôli nižšej spotrebe paliva', 'Kvôli hlučnosti motora'],
      c: 0,
      e: 'Väčšina zranení v autobusoch vznikne pri prudkom brzdení, nie pri zrážke.'
    },
    {
      id: 'SKD-009', cat: 4, groups: ['D'],
      q: 'Ako musí byť označené vozidlo prepravujúce skupinu detí?',
      a: ['Predpísaným označením upozorňujúcim ostatných vodičov na prepravu detí', 'Nemusí byť označené', 'Len výstražnými svetlami'],
      c: 0,
      e: 'Označenie upozorňuje ostatných vodičov na zvýšenú opatrnosť pri nastupovaní a vystupovaní detí.'
    },
    {
      id: 'SKD-010', cat: 3, groups: ['D'],
      q: 'Ako sa má vodič autobusu zachovať pri prejazde úzkou ulicou s parkujúcimi vozidlami?',
      a: ['Znížiť rýchlosť a v prípade potreby dať prednosť protiidúcim vozidlám', 'Trvať na prednosti pre veľkosť vozidla', 'Použiť zvukové znamenie a pokračovať'],
      c: 0,
      e: 'Rozmery autobusu vyžadujú väčší priestor; bezpečnosť má prednosť pred plynulosťou.'
    },
    {
      id: 'SKD-011', cat: 6, groups: ['D'],
      q: 'Čo musí vodič autobusu skontrolovať pred začatím jazdy?',
      a: ['Technický stav vozidla, funkčnosť dverí, svetiel, bŕzd a bezpečnostného vybavenia',
          'Len množstvo paliva', 'Len čistotu interiéru'],
      c: 0,
      e: 'Vodič zodpovedá za bezpečnosť desiatok cestujúcich, preto je kontrola pred jazdou nevyhnutná.'
    },
    {
      id: 'SKD-012', cat: 7, groups: ['D'],
      q: 'Ako má vodič autobusu reagovať na agresívne správanie cestujúceho počas jazdy?',
      a: ['Bezpečne zastaviť na vhodnom mieste a riešiť situáciu, prípadne privolať políciu',
          'Riešiť konflikt počas jazdy', 'Ignorovať situáciu a zrýchliť'],
      c: 0,
      e: 'Riešenie konfliktu za jazdy odvádza pozornosť od vedenia vozidla a ohrozuje všetkých cestujúcich.'
    },

    /* ---------------- Skupina T – traktory ---------------- */
    {
      id: 'SKT-001', cat: 1, groups: ['T'],
      q: 'Smie traktor alebo pracovný stroj vojsť na diaľnicu?',
      a: ['Nie, diaľnica je určená len pre vozidlá schopné dosiahnuť predpísanú rýchlosť', 'Áno, v pravom pruhu', 'Áno, mimo dopravnej špičky'],
      c: 0,
      e: 'Pomalé vozidlá na diaľnici by predstavovali mimoriadne riziko, preto tam nesmú vojsť.'
    },
    {
      id: 'SKT-002', cat: 1, groups: ['T'],
      q: 'Čo musí urobiť vodič traktora, ak pri výjazde z poľa znečistí cestu?',
      a: ['Bezodkladne znečistenie odstrániť alebo zabezpečiť jeho odstránenie', 'Nemusí robiť nič, blato zmyje dážď', 'Stačí označiť úsek výstražným trojuholníkom'],
      c: 0,
      e: 'Znečistená vozovka je klzká a predstavuje prekážku cestnej premávky, ktorú musí pôvodca odstrániť.'
    },
    {
      id: 'SKT-003', cat: 4, groups: ['T'],
      q: 'Smie sa na traktore alebo v jeho prívese prepravovať osoba?',
      a: ['Len na miestach na to určených; preprava osôb na náklade alebo v ložnom priestore je zakázaná',
          'Áno, ak sa jazdí pomaly', 'Áno, na poľnej ceste vždy'],
      c: 0,
      e: 'Prepravovaná osoba mimo určeného miesta nie je chránená a môže ľahko vypadnúť.'
    },
    {
      id: 'SKT-004', cat: 6, groups: ['T'],
      q: 'Ako musí byť označené pomaly idúce vozidlo alebo nadmerné náradie pri jazde po ceste?',
      a: ['Predpísaným označením a osvetlením tak, aby bolo pre ostatných vodičov dobre viditeľné',
          'Nemusí byť označené, ak jazdí cez deň', 'Stačí zapnuté diaľkové svetlo'],
      c: 0,
      e: 'Pripojené náradie často zakrýva svetlá a obrys vozidla, preto sa musí označiť a osvetliť.'
    },
    {
      id: 'SKT-005', cat: 1, groups: ['T'],
      q: 'Ako sa má správať vodič pomaly idúceho traktora, ak sa za ním vytvorí kolóna vozidiel?',
      a: ['Umožniť rýchlejším vozidlám predchádzať, prípadne na vhodnom mieste odbočiť alebo zastaviť',
          'Pokračovať v jazde stredom vozovky', 'Zrýchliť nad konštrukčnú rýchlosť'],
      c: 0,
      e: 'Vodič pomalého vozidla má jazdiť pri pravom okraji a nebrániť plynulosti premávky.'
    },
    {
      id: 'SKT-006', cat: 5, groups: ['T'],
      q: 'Prečo hrozí traktoru s vysoko umiestneným nákladom prevrátenie?',
      a: ['Vysoké ťažisko zhoršuje stabilitu, najmä v zákrutách a na svahu', 'Pretože traktor má malé kolesá', 'Pretože traktor nemá brzdy na prívese'],
      c: 0,
      e: 'Na svahu a v zákrutách treba jazdiť pomaly a vyhnúť sa prudkým manévrom.'
    },
    {
      id: 'SKT-007', cat: 6, groups: ['T'],
      q: 'Čo treba skontrolovať pred jazdou traktora s prívesom po ceste?',
      a: ['Spojenie prívesu, brzdy, osvetlenie a zaistenie nákladu', 'Len množstvo paliva', 'Len tlak v pneumatikách traktora'],
      c: 0,
      e: 'Nezaistený náklad, napríklad balíky slamy, môže spadnúť na vozovku a spôsobiť nehodu.'
    },
    {
      id: 'SKT-008', cat: 5, groups: ['T'],
      q: 'Ako ovplyvňuje jazdná súprava traktora s prívesom brzdnú dráhu?',
      a: ['Výrazne ju predlžuje, preto treba jazdiť pomaly a s väčším odstupom', 'Skracuje ju', 'Nemá na ňu vplyv'],
      c: 0,
      e: 'Hmotnosť súpravy a často slabšie brzdy prívesu predlžujú dráhu potrebnú na zastavenie.'
    },
    {
      id: 'SKT-009', cat: 2, groups: ['T'],
      q: 'Ako sa musí vodič traktora správať k dopravným značkám obmedzujúcim šírku alebo hmotnosť?',
      a: ['Musí ich rešpektovať aj so širokým náradím a nesmie prekročiť uvedené hodnoty',
          'Značky sa na poľnohospodárske vozidlá nevzťahujú', 'Platia len pre nákladné vozidlá'],
      c: 0,
      e: 'Obmedzenia platia pre všetky vozidlá vrátane poľnohospodárskej techniky.'
    },
    {
      id: 'SKT-010', cat: 7, groups: ['T'],
      q: 'Prečo je práca s traktorom v svahu nebezpečná?',
      a: ['Hrozí prevrátenie stroja, preto treba jazdiť pomaly a vyhnúť sa prudkému otáčaniu',
          'Motor v svahu stráca výkon', 'Zvyšuje sa spotreba paliva'],
      c: 0,
      e: 'Prevrátenie traktora patrí medzi najčastejšie príčiny smrteľných úrazov v poľnohospodárstve.'
    },
    {
      id: 'SKT-011', cat: 3, groups: ['T'],
      q: 'Kto má prednosť, keď traktor vychádza z poľnej cesty na cestu?',
      a: ['Vozidlá idúce po ceste – traktor im musí dať prednosť', 'Traktor, lebo je väčší', 'Vozidlo prichádzajúce sprava'],
      c: 0,
      e: 'Poľná cesta sa nepovažuje za rovnocennú cestu, preto vychádzajúce vozidlo dáva prednosť.'
    },
    {
      id: 'SKT-012', cat: 4, groups: ['T'],
      q: 'Musí mať traktor jazdiaci po ceste platnú technickú kontrolu a poistenie?',
      a: ['Áno, ako každé vozidlo v cestnej premávke', 'Nie, ak jazdí len po poliach a krátkych úsekoch ciest', 'Postačuje poistenie'],
      c: 0,
      e: 'Vozidlo používané v cestnej premávke musí spĺňať všetky podmienky prevádzky.'
    },

    /* ---------------- Skupina B+E – jazdné súpravy ---------------- */
    {
      id: 'SBE-001', cat: 4, groups: ['BE'],
      q: 'Na čo oprávňuje vodičské oprávnenie skupiny B+E?',
      a: ['Viesť jazdnú súpravu vozidla skupiny B s prívesom nad 750 kg v rozsahu určenom zákonom',
          'Viesť nákladné vozidlo nad 3 500 kg', 'Viesť autobus s prívesom'],
      c: 0,
      e: 'Skupina B+E rozširuje oprávnenie B o ťažšie prívesy a návesy.'
    },
    {
      id: 'SBE-002', cat: 6, groups: ['BE'],
      q: 'Ako sa má rozložiť náklad v prívese?',
      a: ['Ťažšia časť nad nápravou a čo najnižšie, s primeraným zvislým zaťažením spojovacieho zariadenia',
          'Všetok náklad dozadu', 'Všetok náklad na jednu stranu'],
      c: 0,
      e: 'Nesprávne rozloženie nákladu spôsobuje kmitanie prívesu a stratu stability súpravy.'
    },
    {
      id: 'SBE-003', cat: 5, groups: ['BE'],
      q: 'Čo je najčastejšou príčinou nebezpečného kmitania prívesu pri vyššej rýchlosti?',
      a: ['Nesprávne rozloženie nákladu a príliš vysoká rýchlosť', 'Príliš nízky tlak v pneumatikách ťažného vozidla', 'Použitie poistného lanka'],
      c: 0,
      e: 'Pri kmitaní treba plynule ubrať plyn, nebrzdiť prudko a nestrhávať volant.'
    },
    {
      id: 'SBE-004', cat: 5, groups: ['BE'],
      q: 'Ako sa mení brzdná dráha jazdnej súpravy oproti samostatnému vozidlu?',
      a: ['Predlžuje sa, preto treba väčší odstup a nižšiu rýchlosť', 'Skracuje sa vďaka bŕzd prívesu', 'Nemení sa'],
      c: 0,
      e: 'Väčšia hmotnosť súpravy znamená dlhšiu dráhu potrebnú na zastavenie.'
    },
    {
      id: 'SBE-005', cat: 6, groups: ['BE'],
      q: 'Na čo slúži odtrhové (poistné) lanko prívesu?',
      a: ['Pri odpojení prívesu aktivuje jeho brzdu alebo zabráni jeho voľnému pohybu', 'Slúži na uväzovanie nákladu', 'Nahrádza spojovacie zariadenie'],
      c: 0,
      e: 'Bez funkčného poistného lanka alebo reťaze sa príves nesmie použiť.'
    },
    {
      id: 'SBE-006', cat: 5, groups: ['BE'],
      q: 'Ako sa cúva s prívesom?',
      a: ['Pomaly, malými korekciami volantu – príves sa otáča na opačnú stranu než volant',
          'Rýchlo a s veľkými pohybmi volantu', 'Cúvanie s prívesom je zakázané'],
      c: 0,
      e: 'Pri cúvaní so súpravou je vhodné využiť pomoc druhej osoby a priebežne kontrolovať okolie.'
    },
    {
      id: 'SBE-007', cat: 1, groups: ['BE'],
      q: 'Ako má vodič jazdnej súpravy predchádzať iné vozidlo?',
      a: ['Len ak má dostatok priestoru a výhľadu – predchádzanie so súpravou trvá výrazne dlhšie',
          'Rovnako ako s osobným vozidlom', 'Predchádzať možno aj v zákrute'],
      c: 0,
      e: 'Dlhšia súprava a nižšie zrýchlenie predlžujú čas potrebný na predchádzanie.'
    },
    {
      id: 'SBE-008', cat: 6, groups: ['BE'],
      q: 'Čo treba pred jazdou skontrolovať na jazdnej súprave?',
      a: ['Zaistenie spojovacieho zariadenia, poistné lanko, osvetlenie prívesu, tlak v pneumatikách a zaistenie nákladu',
          'Len osvetlenie ťažného vozidla', 'Nič, ak sa súprava používala včera'],
      c: 0,
      e: 'Nesprávne zaistené spojovacie zariadenie môže viesť k odpojeniu prívesu za jazdy.'
    },
    {
      id: 'SBE-009', cat: 3, groups: ['BE'],
      q: 'Na čo musí dbať vodič súpravy pri odbočovaní a prejazde križovatkou?',
      a: ['Na väčší polomer otáčania a na to, že príves prechádza bližšie k okraju vozovky',
          'Na nič zvláštne, súprava sa správa ako auto', 'Na rýchlejšie zrýchlenie súpravy'],
      c: 0,
      e: 'Pri odbočovaní treba nabrať väčší oblúk, aby príves nezachytil obrubník alebo chodca.'
    },
    {
      id: 'SBE-010', cat: 4, groups: ['BE'],
      q: 'Smie vodič prekročiť najväčšiu prípustnú hmotnosť jazdnej súpravy uvedenú v dokladoch?',
      a: ['Nie, hmotnosti súpravy aj prívesu sú záväzné', 'Áno, o 10 %', 'Áno, na krátku vzdialenosť'],
      c: 0,
      e: 'Prekročenie hmotností mení jazdné vlastnosti a je porušením podmienok prevádzky vozidla.'
    },
    {
      id: 'SBE-011', cat: 6, groups: ['BE'],
      q: 'Prečo musí mať príves funkčné osvetlenie a smerové svetlá?',
      a: ['Príves zakrýva svetlá ťažného vozidla, takže bez neho ostatní nevidia zámery vodiča',
          'Kvôli technickej kontrole ťažného vozidla', 'Nie je to nutné pri jazde cez deň'],
      c: 0,
      e: 'Nefunkčné osvetlenie prívesu je dôvodom na vyradenie súpravy z premávky.'
    },
    {
      id: 'SBE-012', cat: 2, groups: ['BE'],
      q: 'Ako sa vodič súpravy musí správať k značkám obmedzujúcim dĺžku alebo hmotnosť vozidiel?',
      a: ['Musí ich rešpektovať a v prípade potreby zvoliť inú trasu', 'Platia len pre nákladné vozidlá', 'Môže ich prekročiť pri jazde do 30 km/h'],
      c: 0,
      e: 'Obmedzenia sa vzťahujú na celú jazdnú súpravu vrátane prívesu.'
    }
  ]);
})();

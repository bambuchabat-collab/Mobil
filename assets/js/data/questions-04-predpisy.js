/* Okruh 4 – Všeobecné predpisy, doklady a povinnosti vodiča */
(function () {
  'use strict';
  BANK.add([
    {
      id: 'PRE-001', cat: 4, groups: ['*'],
      q: 'Ktoré doklady musí mať vodič motorového vozidla pri sebe počas jazdy?',
      a: ['Vodičský preukaz, osvedčenie o evidencii vozidla a doklad o povinnom zmluvnom poistení',
          'Len vodičský preukaz', 'Len občiansky preukaz'],
      c: 0,
      e: 'Vodič sa preukazuje vodičským preukazom, osvedčením o evidencii časť I a dokladom o poistení zodpovednosti za škodu.'
    },
    {
      id: 'PRE-002', cat: 4, groups: ['*'],
      q: 'Kedy je vodič povinný ohlásiť dopravnú nehodu polícii?',
      a: ['Ak došlo k zraneniu alebo usmrteniu osoby, k poškodeniu cesty či majetku tretej osoby, alebo ak sa účastníci nedohodli na zavinení',
          'Vždy, aj pri drobnom škrabanci', 'Nikdy, stačí vyplniť správu o nehode'],
      c: 0,
      e: 'Dopravnú nehodu treba ohlásiť polícii najmä pri zranení, značnej škode, poškodení cesty alebo pri nezhode účastníkov.'
    },
    {
      id: 'PRE-003', cat: 4, groups: ['*'],
      q: 'Čo musí vodič urobiť bezprostredne po dopravnej nehode, na ktorej sa zúčastnil?',
      a: ['Zastaviť vozidlo, zdržať sa požitia alkoholu, poskytnúť prvú pomoc a označiť miesto nehody',
          'Odviezť vozidlo domov a nehodu ohlásiť neskôr', 'Počkať vo vozidle, kým príde polícia, a nič nerobiť'],
      c: 0,
      e: 'Účastník nehody musí zastaviť, poskytnúť pomoc zraneným, označiť miesto nehody a zotrvať na mieste do príchodu polície.'
    },
    {
      id: 'PRE-004', cat: 4, groups: ['*'],
      q: 'Smie vodič po dopravnej nehode požiť alkohol pred príchodom polície?',
      a: ['Nie, je to zakázané, kým sa nevykoná vyšetrenie na zistenie alkoholu', 'Áno, na upokojenie', 'Áno, ak nehodu nezavinil'],
      c: 0,
      e: 'Požitie alkoholu po nehode by znemožnilo zistiť, či bol vodič pod vplyvom počas jazdy, preto je zakázané.'
    },
    {
      id: 'PRE-005', cat: 4, groups: ['*'],
      q: 'Ako sa posudzuje odmietnutie dychovej skúšky na alkohol?',
      a: ['Rovnako, ako keby bol vodič pod vplyvom alkoholu – ide o závažné porušenie zákona',
          'Ako priestupok bez následkov', 'Vodič má právo skúšku odmietnuť bez následkov'],
      c: 0,
      e: 'Vodič je povinný podrobiť sa vyšetreniu na zistenie alkoholu; odmietnutie je závažným porušením pravidiel.'
    },
    {
      id: 'PRE-006', cat: 4, groups: ['*'],
      q: 'Kto smie viesť motorové vozidlo?',
      a: ['Osoba, ktorá je držiteľom platného vodičského oprávnenia príslušnej skupiny a je spôsobilá viesť vozidlo',
          'Ktokoľvek, kto absolvoval autoškolu', 'Ktokoľvek starší ako 18 rokov'],
      c: 0,
      e: 'Vodič musí mať vodičské oprávnenie danej skupiny a byť telesne aj duševne spôsobilý viesť vozidlo.'
    },
    {
      id: 'PRE-007', cat: 4, groups: ['*'],
      q: 'Čo je povinné zmluvné poistenie (PZP)?',
      a: ['Poistenie zodpovednosti za škodu spôsobenú prevádzkou vozidla, ktoré musí mať každé vozidlo',
          'Dobrovoľné havarijné poistenie', 'Poistenie posádky vozidla'],
      c: 0,
      e: 'PZP kryje škody, ktoré prevádzkou vozidla spôsobíte iným; bez neho sa vozidlo nesmie používať.'
    },
    {
      id: 'PRE-008', cat: 4, groups: ['*'],
      q: 'Kedy je vodič mimo obce povinný použiť reflexný bezpečnostný odev?',
      a: ['Keď sa po núdzovom zastavení pohybuje po vozovke alebo krajnici mimo vozidla',
          'Vždy počas jazdy', 'Len v noci v obci'],
      c: 0,
      e: 'Pri poruche alebo nehode mimo obce sa vodič musí mimo vozidla pohybovať v reflexnom odeve.'
    },
    {
      id: 'PRE-009', cat: 4, groups: ['*'],
      q: 'Smú sa prepravovať osoby v ložnom priestore nákladného vozidla alebo prívesu?',
      a: ['Nie, s výnimkami ustanovenými zákonom', 'Áno, ak sedia', 'Áno, ak sa jazdí do 30 km/h'],
      c: 0,
      e: 'Preprava osôb v ložnom priestore je zakázaná, pretože tam nie sú zabezpečené bezpečnostné prvky.'
    },
    {
      id: 'PRE-010', cat: 4, groups: ['*'],
      q: 'Aké požiadavky platia pre náklad prepravovaný na vozidle?',
      a: ['Musí byť rozložený a zaistený tak, aby neohrozil bezpečnosť a neznečisťoval cestu',
          'Stačí, ak nepresahuje obrysy vozidla', 'Náklad netreba zaisťovať pri jazde v obci'],
      c: 0,
      e: 'Náklad nesmie ohroziť bezpečnosť premávky, znečistiť cestu, zakrývať svetlá ani obmedziť výhľad vodiča.'
    },
    {
      id: 'PRE-011', cat: 4, groups: ['*'],
      q: 'Aký je najnižší vek na udelenie vodičského oprávnenia skupiny B na Slovensku?',
      a: ['17 rokov, pričom do dovŕšenia 18 rokov možno viesť vozidlo len so sprevádzajúcou osobou',
          '21 rokov', '16 rokov bez ďalších podmienok'],
      c: 0,
      e: 'Skupinu B možno získať od 17 rokov; do 18. roku musí byť vo vozidle zapísaná sprevádzajúca osoba.'
    },
    {
      id: 'PRE-012', cat: 4, groups: ['*'],
      q: 'Čo znamená, že vodičský preukaz bol zadržaný políciou?',
      a: ['Vodič nesmie ďalej viesť motorové vozidlo, kým mu preukaz nevrátia', 'Môže jazdiť s potvrdením neobmedzene', 'Môže jazdiť len v obci'],
      c: 0,
      e: 'Po zadržaní vodičského preukazu stráca vodič oprávnenie viesť vozidlo do rozhodnutia príslušného orgánu.'
    },
    {
      id: 'PRE-013', cat: 4, groups: ['*'],
      q: 'Kto zodpovedá za technický stav vozidla pri jazde?',
      a: ['Vodič spolu s prevádzkovateľom vozidla', 'Len servis, ktorý vozidlo naposledy opravoval', 'Len prevádzkovateľ vozidla'],
      c: 0,
      e: 'Vodič sa musí pred jazdou presvedčiť, či vozidlo spĺňa podmienky prevádzky; zodpovedá aj prevádzkovateľ.'
    },
    {
      id: 'PRE-014', cat: 4, groups: ['*'],
      q: 'Smie vodič viesť vozidlo, ak jeho technická alebo emisná kontrola nie je platná?',
      a: ['Nie, vozidlo nespĺňa podmienky na prevádzku v cestnej premávke', 'Áno, ak vozidlo funguje bez porúch', 'Áno, najviac 30 dní po skončení platnosti'],
      c: 0,
      e: 'Vozidlo bez platnej technickej a emisnej kontroly je technicky nespôsobilé na premávku.'
    },
    {
      id: 'PRE-015', cat: 4, groups: ['*'],
      q: 'Čo je škodová udalosť (na rozdiel od dopravnej nehody)?',
      a: ['Udalosť bez zranenia osôb, pri ktorej sa účastníci dohodli na zavinení a škoda je nižšia ako zákonná hranica',
          'Každá zrážka dvoch vozidiel', 'Udalosť, pri ktorej došlo k zraneniu'],
      c: 0,
      e: 'Pri škodovej udalosti stačí vyplniť správu o nehode; polícia sa nevolá, ak nie sú splnené podmienky nehody.'
    },
    {
      id: 'PRE-016', cat: 4, groups: ['*'],
      q: 'Je vodič povinný poskytnúť prvú pomoc zranenej osobe pri dopravnej nehode?',
      a: ['Áno, v rozsahu svojich schopností a možností, a privolať záchrannú službu', 'Nie, to je úloha len záchranárov', 'Áno, len ak nehodu zavinil'],
      c: 0,
      e: 'Neposkytnutie pomoci je trestný čin; vodič má povinnosť pomôcť a privolať odbornú pomoc.'
    },
    {
      id: 'PRE-017', cat: 4, groups: ['*'],
      q: 'Aké je telefónne číslo integrovaného záchranného systému platné v celej EÚ?',
      a: ['112', '158', '150'], c: 0,
      e: 'Číslo 112 spája volajúceho so všetkými zložkami záchranného systému; 155 je záchranná zdravotná služba, 158 polícia.'
    },
    {
      id: 'PRE-018', cat: 4, groups: ['*'],
      q: 'Smie vodič viesť vozidlo, ak užil liek, ktorý znižuje schopnosť viesť vozidlo?',
      a: ['Nie, ak liek znižuje jeho schopnosť bezpečne viesť vozidlo', 'Áno, lieky sa nepovažujú za návykové látky', 'Áno, ak liek predpísal lekár'],
      c: 0,
      e: 'Vodič nesmie viesť vozidlo, ak je jeho schopnosť znížená úrazom, chorobou, liekmi alebo únavou.'
    },
    {
      id: 'PRE-019', cat: 4, groups: ['*'],
      q: 'Čo musí urobiť vodič, ktorý pri jazde spôsobí škodu na majetku a nemôže nájsť poškodeného?',
      a: ['Ohlásiť udalosť polícii', 'Nechať na vozidle odkaz a odísť', 'Nemusí robiť nič'],
      c: 0,
      e: 'Ak sa poškodený nedá zistiť, musí vodič udalosť bezodkladne ohlásiť polícii.'
    },
    {
      id: 'PRE-020', cat: 4, groups: ['*'],
      q: 'Kto sa považuje za účastníka cestnej premávky?',
      a: ['Každá osoba, ktorá sa priamo zúčastňuje na cestnej premávke – vodič, chodec, cyklista aj pasažier',
          'Len vodiči motorových vozidiel', 'Len vodiči a cyklisti'],
      c: 0,
      e: 'Účastníkom premávky je každý, kto sa priamo zúčastňuje premávky na pozemných komunikáciách.'
    },
    {
      id: 'PRE-021', cat: 4, groups: ['*'],
      q: 'Je vodič povinný uposlúchnuť pokyn policajta na zastavenie vozidla?',
      a: ['Áno, musí zastaviť na bezpečnom mieste podľa pokynu', 'Nie, ak sa neprevinil', 'Áno, ale len na diaľnici'],
      c: 0,
      e: 'Vodič musí uposlúchnuť pokyny policajta a predložiť požadované doklady.'
    },
    {
      id: 'PRE-022', cat: 4, groups: ['*'],
      q: 'Čo platí pre používanie diaľnice vozidlom do 3,5 t na Slovensku?',
      a: ['Vozidlo musí mať uhradenú platnú diaľničnú známku', 'Diaľnice sú bezplatné pre všetky vozidlá', 'Známka je potrebná len v lete'],
      c: 0,
      e: 'Za používanie vymedzených úsekov diaľnic a rýchlostných ciest sa platí elektronická diaľničná známka.'
    },
    {
      id: 'PRE-023', cat: 4, groups: ['*'],
      q: 'Kedy môže polícia zabrániť vodičovi v jazde (napr. zadržaním dokladov alebo tabuliek)?',
      a: ['Ak je vodič pod vplyvom alkoholu alebo vozidlo je technicky nespôsobilé na premávku',
          'Nikdy, polícia môže len udeliť pokutu', 'Len ak vodič nemá pri sebe občiansky preukaz'],
      c: 0,
      e: 'Polícia môže zabrániť v jazde vodičovi, ktorý ohrozuje bezpečnosť premávky, napríklad po požití alkoholu.'
    },
    {
      id: 'PRE-024', cat: 4, groups: ['*'],
      q: 'Ako sa má vodič zachovať, ak je svedkom dopravnej nehody, na ktorej sa nezúčastnil?',
      a: ['Zastaviť a poskytnúť pomoc, ak je to potrebné, a prípadne privolať záchranné zložky',
          'Pokračovať v jazde, nie je jeho vec', 'Zastaviť a fotografovať nehodu'],
      c: 0,
      e: 'Povinnosť poskytnúť pomoc pri nehode má každý vodič, aj keď sa na nej nezúčastnil.'
    },
    {
      id: 'PRE-025', cat: 4, groups: ['*'],
      q: 'Musí vodič oznámiť zmenu vlastníka vozidla v evidencii vozidiel?',
      a: ['Áno, prevod držby vozidla treba nahlásiť príslušnému dopravnému inšpektorátu v zákonnej lehote',
          'Nie, stačí ústna dohoda s kupujúcim', 'Áno, ale len pri vozidlách starších ako 10 rokov'],
      c: 0,
      e: 'Zmenu držiteľa vozidla treba nahlásiť; inak ostávajú povinnosti a zodpovednosť na pôvodnom držiteľovi.'
    },
    {
      id: 'PRE-026', cat: 4, groups: ['*'],
      q: 'Je vodič zodpovedný za to, že prepravované deti sú riadne zabezpečené v autosedačke?',
      a: ['Áno, za bezpečnú prepravu detí zodpovedá vodič', 'Nie, zodpovedá rodič dieťaťa', 'Áno, ale len mimo obce'],
      c: 0,
      e: 'Vodič zodpovedá za to, že prepravované osoby sú pripútané a deti prepravované v zádržnom systéme.'
    },
    {
      id: 'PRE-027', cat: 4, groups: ['*'],
      q: 'Smie vodič použiť antiradar (zariadenie na rušenie merania rýchlosti)?',
      a: ['Nie, používanie takýchto zariadení je zakázané', 'Áno, mimo obce', 'Áno, ak neprekračuje rýchlosť'],
      c: 0,
      e: 'Zariadenia na zisťovanie alebo rušenie meracích prístrojov polície sa nesmú používať ani mať vo vozidle pripravené na použitie.'
    },
    {
      id: 'PRE-028', cat: 4, groups: ['*'],
      q: 'Aké označenie musí mať vozidlo autoškoly pri výcvikovej jazde?',
      a: ['Musí byť zreteľne označené (napríklad tabuľkou s nápisom „Autoškola“)', 'Nemusí byť označené', 'Stačí označenie vo výhľade vodiča'],
      c: 0,
      e: 'Výcvikové vozidlo musí byť zreteľne označené, aby ostatní vodiči vedeli, že ide o žiaka autoškoly.'
    },
    {
      id: 'PRE-029', cat: 4, groups: ['*'],
      q: 'Čo znamená pojem „obmedzenie“ iného účastníka cestnej premávky?',
      a: ['Také konanie vodiča, pre ktoré musí iný účastník náhle zmeniť smer alebo rýchlosť jazdy',
          'Spôsobenie dopravnej nehody', 'Len prekročenie rýchlosti'],
      c: 0,
      e: 'Obmedzenie nastane, keď iný účastník musí kvôli nám zmeniť rýchlosť alebo smer; ohrozenie je závažnejšie – hrozí nehoda.'
    },
    {
      id: 'PRE-030', cat: 4, groups: ['*'],
      q: 'Kto je „sprevádzajúca osoba“ pri jazde vodiča vo veku 17 rokov?',
      a: ['Osoba zapísaná v evidencii, ktorá spĺňa zákonné podmienky a sedí vedľa vodiča', 'Ktokoľvek starší ako 18 rokov', 'Inštruktor autoškoly'],
      c: 0,
      e: 'Sprevádzajúca osoba musí byť zapísaná v evidencii a spĺňať podmienky veku a praxe; sedí na mieste spolujazdca.'
    },
    {
      id: 'PRE-031', cat: 4, groups: ['*'],
      q: 'Ako sa má správať vodič, ktorý zbadá za sebou vozidlo polície s výzvou „STOP“ na svetelnej tabuli?',
      a: ['Zastaviť vozidlo na bezpečnom mieste podľa pokynu polície', 'Zvýšiť rýchlosť a odbočiť', 'Ignorovať výzvu, ak si nie je vedomý priestupku'],
      c: 0,
      e: 'Výzva na zastavenie z policajného vozidla je pokynom na riadenie premávky, ktorý musí vodič uposlúchnuť.'
    },
    {
      id: 'PRE-032', cat: 4, groups: ['*'],
      q: 'Smie vodič viesť vozidlo, ak je unavený alebo ospalý?',
      a: ['Nie, únava znižuje schopnosť viesť vozidlo – treba zastaviť a odpočinúť si', 'Áno, ak si dá kávu', 'Áno, ak ide na krátku vzdialenosť'],
      c: 0,
      e: 'Mikrospánok patrí medzi najčastejšie príčiny vážnych nehôd; pri únave treba prerušiť jazdu.'
    }
  ]);
})();

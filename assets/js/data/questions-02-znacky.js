/* Okruh 2 – Dopravné značky, dopravné zariadenia a svetelné signály */
(function () {
  'use strict';
  BANK.add([
    {
      id: 'DZ-001', cat: 2, groups: ['*'],
      q: 'Čo prikazuje značka „Stoj, daj prednosť v jazde!“ (osemuholník s nápisom STOP)?',
      a: ['Zastaviť vozidlo na mieste, odkiaľ je rozhľad, a dať prednosť vozidlám na hlavnej ceste',
          'Spomaliť a prejsť križovatkou bez zastavenia', 'Zastaviť len vtedy, ak prichádza iné vozidlo'],
      c: 0,
      e: 'Pri značke STOP musí vodič vždy zastaviť, aj keď je križovatka voľná, a až potom dať prednosť.'
    },
    {
      id: 'DZ-002', cat: 2, groups: ['*'],
      q: 'Ako vyzerá značka „Daj prednosť v jazde!“?',
      a: ['Trojuholník s červeným okrajom obrátený hrotom nadol', 'Modrý kruh so šípkou', 'Žltý kosoštvorec'],
      c: 0,
      e: 'Značka „Daj prednosť v jazde!“ je trojuholník postavený na vrchol; vodič nemusí zastaviť, ale musí dať prednosť.'
    },
    {
      id: 'DZ-003', cat: 2, groups: ['*'],
      q: 'Čo znamená žltý kosoštvorec s bielym okrajom?',
      a: ['Hlavná cesta – vodič má prednosť pred vozidlami z vedľajších ciest', 'Koniec obce', 'Zákaz predchádzania'],
      c: 0,
      e: 'Žltý kosoštvorec označuje hlavnú cestu; jej koniec označuje rovnaká značka prečiarknutá čiernym pásom.'
    },
    {
      id: 'DZ-004', cat: 2, groups: ['*'],
      q: 'Čo znamená kruhová značka s bielym vodorovným pruhom na červenom podklade?',
      a: ['Zákaz vjazdu všetkých vozidiel', 'Zákaz predchádzania', 'Jednosmerná premávka'],
      c: 0,
      e: 'Ide o značku „Zákaz vjazdu“, spravidla označuje výjazd z jednosmernej cesty.'
    },
    {
      id: 'DZ-005', cat: 2, groups: ['*'],
      q: 'Čo znamená kruhová značka s červeným okrajom a číslom, napríklad 70?',
      a: ['Najvyššia dovolená rýchlosť 70 km/h', 'Odporúčaná rýchlosť 70 km/h', 'Najnižšia dovolená rýchlosť 70 km/h'],
      c: 0,
      e: 'Zákazová značka určuje najvyššiu dovolenú rýchlosť; platí do najbližšej križovatky alebo do značky ukončujúcej zákaz.'
    },
    {
      id: 'DZ-006', cat: 2, groups: ['*'],
      q: 'Čo znamená modrá kruhová značka s bielym číslom?',
      a: ['Najnižšia dovolená rýchlosť', 'Najvyššia dovolená rýchlosť', 'Odporúčaná rýchlosť pre nákladné vozidlá'],
      c: 0,
      e: 'Modrá kruhová značka s číslom prikazuje jazdiť najmenej takou rýchlosťou, ak to dovoľuje dopravná situácia.'
    },
    {
      id: 'DZ-007', cat: 2, groups: ['*'],
      q: 'Ktorá značka označuje zákaz predchádzania?',
      a: ['Kruh s červeným okrajom s dvomi autami – červené vľavo', 'Modrý kruh s dvomi autami', 'Trojuholník s dvomi autami'],
      c: 0,
      e: 'Zákaz predchádzania platí od značky po najbližšiu križovatku alebo po značku ukončujúcu zákaz.'
    },
    {
      id: 'DZ-008', cat: 2, groups: ['*'],
      q: 'Čo označuje trojuholníková značka s červeným okrajom?',
      a: ['Výstrahu pred nebezpečenstvom, ktoré je zobrazené v značke', 'Príkaz, ktorý musí vodič splniť', 'Informáciu o službách pri ceste'],
      c: 0,
      e: 'Výstražné značky upozorňujú na miesto, kde vodičovi hrozí nebezpečenstvo; vodič musí prispôsobiť jazdu.'
    },
    {
      id: 'DZ-009', cat: 2, groups: ['*'],
      q: 'Čo znamenajú modré kruhové značky so šípkami?',
      a: ['Prikázaný smer jazdy – vodič musí ísť naznačeným smerom', 'Odporúčaný smer jazdy', 'Zákaz jazdy naznačeným smerom'],
      c: 0,
      e: 'Modré príkazové značky prikazujú smer jazdy, spôsob jazdy alebo druh premávky.'
    },
    {
      id: 'DZ-010', cat: 2, groups: ['*'],
      q: 'Čo označuje modrá kruhová značka s tromi šípkami do kruhu?',
      a: ['Kruhový objazd', 'Otáčanie vozidla', 'Zákaz vjazdu do križovatky'],
      c: 0,
      e: 'Značka „Kruhový objazd“ prikazuje jazdu v smere šípok; ak je pod ňou značka „Daj prednosť v jazde!“, vodič dáva prednosť vozidlám v kruhovom objazde.'
    },
    {
      id: 'DZ-011', cat: 2, groups: ['*'],
      q: 'Aký význam má vodorovná plná pozdĺžna čiara na vozovke?',
      a: ['Vodič ju nesmie prechádzať ani po nej jazdiť, ak to nevyžaduje bezpečnosť premávky',
          'Označuje odporúčaný stred vozovky', 'Umožňuje predchádzanie'],
      c: 0,
      e: 'Súvislú čiaru je zakázané prechádzať a jazdiť po nej okrem prípadov, keď to vyžaduje bezpečnosť (napr. obchádzanie prekážky).'
    },
    {
      id: 'DZ-012', cat: 2, groups: ['*'],
      q: 'Čo znamená prerušovaná pozdĺžna čiara na vozovke?',
      a: ['Vodič ju smie prechádzať pri dodržaní pravidiel (napr. pri predchádzaní)',
          'Zakazuje predchádzanie', 'Označuje okraj vozovky'],
      c: 0,
      e: 'Prerušovaná čiara oddeľuje jazdné pruhy a možno ju prechádzať, ak to premávka dovoľuje.'
    },
    {
      id: 'DZ-013', cat: 2, groups: ['*'],
      q: 'Ako sa má vodič zachovať pri žltej kľukatej čiare pri okraji vozovky?',
      a: ['Je to zastávka vozidiel pravidelnej dopravy – nesmie tam zastaviť ani stáť',
          'Je to parkovacie miesto pre osobné vozidlá', 'Je to miesto na otáčanie'],
      c: 0,
      e: 'Žltá kľukatá čiara vyznačuje zastávku; zastavenie a státie iných vozidiel je tam zakázané.'
    },
    {
      id: 'DZ-014', cat: 2, groups: ['*'],
      q: 'Aké je poradie dôležitosti pri riadení cestnej premávky?',
      a: ['Pokyny policajta, potom svetelné signály, potom dopravné značky a nakoniec všeobecné pravidlá',
          'Dopravné značky majú vždy prednosť pred pokynmi policajta',
          'Vodorovné značky majú prednosť pred pokynmi policajta'],
      c: 0,
      e: 'Pokyny policajta sú nadradené svetelným signálom aj značkám; značky sú nadradené všeobecným pravidlám.'
    },
    {
      id: 'DZ-015', cat: 2, groups: ['*'],
      q: 'Čo znamená prerušované žlté svetlo na svetelnej signalizácii?',
      a: ['Vodič musí dbať na zvýšenú opatrnosť a riadiť sa dopravnými značkami a pravidlami',
          'Vodič musí zastaviť', 'Vodič má prednosť v jazde'],
      c: 0,
      e: 'Prerušované žlté svetlo znamená, že križovatka nie je riadená – platia značky a všeobecné pravidlá.'
    },
    {
      id: 'DZ-016', cat: 2, groups: ['*'],
      q: 'Kedy smie vodič vojsť do križovatky pri žltom svetle signálu „Stoj!“?',
      a: ['Len ak je už tak blízko, že by nemohol bezpečne zastaviť', 'Vždy, žltá znamená pripraviť sa na jazdu', 'Nikdy, aj keby musel prudko zabrzdiť'],
      c: 0,
      e: 'Pri žltom svetle sa vodič musí zastaviť pred križovatkou; ak je príliš blízko a nemohol by bezpečne zastaviť, smie prejsť.'
    },
    {
      id: 'DZ-017', cat: 2, groups: ['*'],
      q: 'Čo označuje Andrejov kríž (biely kríž s červeným okrajom) pri ceste?',
      a: ['Železničné priecestie', 'Zákaz vjazdu', 'Koniec obce'],
      c: 0,
      e: 'Andrejov kríž označuje železničné priecestie – jednoduchý pri jednej koľaji, dvojitý pri dvoch a viacerých koľajach.'
    },
    {
      id: 'DZ-018', cat: 2, groups: ['*'],
      q: 'Čo znamenajú návestné tabule so šikmými pruhmi pred železničným priecestím?',
      a: ['Upozorňujú na vzdialenosť k priecestiu – tri pruhy 240 m, dva 160 m, jeden 80 m',
          'Označujú koniec obce', 'Označujú zákaz predchádzania'],
      c: 0,
      e: 'Návestné tabule postupne upozorňujú na blížiace sa priecestie; posledná je zhruba 80 m pred ním.'
    },
    {
      id: 'DZ-019', cat: 2, groups: ['*'],
      q: 'Od ktorého miesta platí najvyššia dovolená rýchlosť 50 km/h v obci?',
      a: ['Od značky označujúcej začiatok obce (biela tabuľa s názvom obce)', 'Od prvej budovy pri ceste', 'Od prvého priechodu pre chodcov'],
      c: 0,
      e: 'Obec sa začína značkou „Obec“ a končí značkou „Koniec obce“; medzi nimi platia pravidlá pre jazdu v obci.'
    },
    {
      id: 'DZ-020', cat: 2, groups: ['*'],
      q: 'Ako dlho spravidla platí zákazová značka umiestnená pri ceste?',
      a: ['Po najbližšiu križovatku alebo po značku, ktorá zákaz ukončuje', 'Presne 500 metrov', 'Do konca obce vždy'],
      c: 0,
      e: 'Platnosť zákazovej značky sa končí najbližšou križovatkou alebo značkou ukončujúcou zákaz, prípadne podľa dodatkovej tabuľky.'
    },
    {
      id: 'DZ-021', cat: 2, groups: ['*'],
      q: 'Aký význam má dodatková tabuľka pod dopravnou značkou?',
      a: ['Spresňuje, obmedzuje alebo dopĺňa význam značky', 'Nemá právny význam', 'Ruší platnosť značky'],
      c: 0,
      e: 'Dodatková tabuľka napríklad určuje dĺžku úseku, čas platnosti alebo skupinu vozidiel, ktorých sa značka týka.'
    },
    {
      id: 'DZ-022', cat: 2, groups: ['*'],
      q: 'Čo znamená značka s obrázkom dvoch detí v červenom trojuholníku?',
      a: ['Upozorňuje na miesto, kde sa deti často pohybujú pri ceste alebo cez ňu prechádzajú',
          'Označuje detské ihrisko so zákazom vjazdu', 'Prikazuje jazdiť 20 km/h'],
      c: 0,
      e: 'Výstražná značka „Pozor, deti“ upozorňuje na okolie škôl a ihrísk; vodič musí byť mimoriadne opatrný.'
    },
    {
      id: 'DZ-023', cat: 2, groups: ['*'],
      q: 'Čo znamená výstražná značka „Šmykľavá vozovka“?',
      a: ['Vozovka môže byť klzká – treba znížiť rýchlosť a jazdiť plynulo', 'Vozovka je vo výstavbe', 'Je zakázané brzdiť'],
      c: 0,
      e: 'Na šmykľavej vozovke sa predlžuje brzdná dráha; vodič má jazdiť pomaly, bez prudkých manévrov.'
    },
    {
      id: 'DZ-024', cat: 2, groups: ['*'],
      q: 'Čo znamená značka „Práca na ceste“?',
      a: ['Upozorňuje na úsek, kde sa vykonávajú práce – treba spomaliť a dbať na pokyny',
          'Zakazuje vjazd všetkých vozidiel', 'Označuje odstavné parkovisko'],
      c: 0,
      e: 'V úseku prác sa mení organizácia premávky; vodič musí rešpektovať dočasné značky a zariadenia.'
    },
    {
      id: 'DZ-025', cat: 2, groups: ['*'],
      q: 'Na čo upozorňuje výstražná značka s percentuálnym údajom, napríklad 10 %?',
      a: ['Na nebezpečné klesanie alebo stúpanie cesty', 'Na povolený sklon nákladu', 'Na podiel poškodenej vozovky'],
      c: 0,
      e: 'Značka upozorňuje na prudké klesanie alebo stúpanie; pri klesaní treba brzdiť motorom.'
    },
    {
      id: 'DZ-026', cat: 2, groups: ['*'],
      q: 'Čo označuje modrá štvorcová značka s bielym písmenom P?',
      a: ['Parkovisko', 'Policajnú stanicu', 'Zákaz státia'],
      c: 0,
      e: 'Informatívne značky s modrým podkladom označujú služby a zariadenia, napríklad parkovisko.'
    },
    {
      id: 'DZ-027', cat: 2, groups: ['*'],
      q: 'Čo znamená značka „Zákaz zastavenia“?',
      a: ['Vodič nesmie na vyznačenom mieste zastaviť ani stáť', 'Vodič smie zastaviť, ale nesmie stáť', 'Vodič smie zastaviť najviac na 3 minúty'],
      c: 0,
      e: 'Zákaz zastavenia je prísnejší ako zákaz státia – nesmie sa tam ani krátkodobo zastaviť.'
    },
    {
      id: 'DZ-028', cat: 2, groups: ['*'],
      q: 'Čo znamená značka „Zákaz státia“?',
      a: ['Vodič smie krátko zastaviť na nastúpenie alebo vystúpenie osôb, ale nesmie tam stáť',
          'Vodič nesmie zastaviť za žiadnych okolností', 'Značka platí len v noci'],
      c: 0,
      e: 'Zákaz státia dovoľuje zastavenie na čas nevyhnutný na nastúpenie a vystúpenie osôb alebo naloženie nákladu.'
    },
    {
      id: 'DZ-029', cat: 2, groups: ['*'],
      q: 'Čo znamenajú dopravné kužele, smerovacie dosky a zábrany na ceste?',
      a: ['Sú to dopravné zariadenia, ktoré usmerňujú premávku a vodič ich musí rešpektovať',
          'Sú to len orientačné pomôcky bez záväznosti', 'Označujú koniec platnosti značiek'],
      c: 0,
      e: 'Dopravné zariadenia vyznačujú prekážky a zmeny organizácie premávky; ich pokyny sú záväzné.'
    },
    {
      id: 'DZ-030', cat: 2, groups: ['*'],
      q: 'Čo znamená informatívna značka s bielym autom na modrom podklade a nápisom „Diaľnica“?',
      a: ['Začiatok diaľnice a platnosť osobitných pravidiel pre diaľnicu', 'Odporúčanú trasu pre nákladné vozidlá', 'Koniec obce'],
      c: 0,
      e: 'Od tejto značky platia pravidlá pre diaľnicu – vyššia rýchlosť, zákaz zastavenia, otáčania a cúvania.'
    },
    {
      id: 'DZ-031', cat: 2, groups: ['*'],
      q: 'Čo znamená značka „Prednosť pred protiidúcimi vozidlami“ (modrý štvorec s bielou a červenou šípkou)?',
      a: ['V zúženom úseku má vodič prednosť pred vozidlami idúcimi oproti', 'Vodič musí dať prednosť protiidúcim', 'Označuje jednosmernú cestu'],
      c: 0,
      e: 'Opačný význam má červená značka „Daj prednosť protiidúcim vozidlám“ – tam vodič musí počkať.'
    },
    {
      id: 'DZ-032', cat: 2, groups: ['*'],
      q: 'Čo znamená značka „Slepá ulica“?',
      a: ['Cesta ďalej nepokračuje a nedá sa ňou prejsť', 'Cesta je jednosmerná', 'Cesta je určená len pre chodcov'],
      c: 0,
      e: 'Slepá ulica končí a vodič sa bude musieť vrátiť rovnakou cestou.'
    },
    {
      id: 'DZ-033', cat: 2, groups: ['*'],
      q: 'Aký význam má výstražná značka „Zúžená vozovka“?',
      a: ['Upozorňuje na zúženie cesty – vodič musí prispôsobiť rýchlosť a prípadne dať prednosť',
          'Označuje koniec vozovky', 'Prikazuje jazdu v ľavom pruhu'],
      c: 0,
      e: 'V zúženom úseku sa vodiči musia striedať alebo rešpektovať značky určujúce prednosť.'
    },
    {
      id: 'DZ-034', cat: 2, groups: ['*'],
      q: 'Čo znamená vodorovná značka „priechod pre chodcov“ (biele pozdĺžne pruhy naprieč vozovkou)?',
      a: ['Miesto určené na prechádzanie chodcov cez vozovku, kde im vodič musí umožniť prejsť',
          'Miesto na zastavenie vozidiel', 'Miesto na otáčanie vozidiel'],
      c: 0,
      e: 'Na priechode má chodec prednosť; vodič ho nesmie ohroziť ani obmedziť.'
    },
    {
      id: 'DZ-035', cat: 2, groups: ['*'],
      q: 'Čo znamená značka „Zákaz vjazdu vozidiel, ktorých okamžitá hmotnosť presahuje vyznačenú hranicu“?',
      a: ['Vozidlá ťažšie, ako uvádza značka, tam nesmú vojsť', 'Značka je len odporúčaním',
          'Platí len pre vozidlá s prívesom'],
      c: 0,
      e: 'Rozhoduje okamžitá hmotnosť vozidla vrátane nákladu a posádky.'
    },
    {
      id: 'DZ-036', cat: 2, groups: ['*'],
      q: 'Čo označuje značka „Obytná zóna“?',
      a: ['Zónu, kde chodci smú používať cestu po celej šírke a platí rýchlosť najviac 20 km/h',
          'Zónu s parkovaním zadarmo', 'Zónu, kde neplatia dopravné značky'],
      c: 0,
      e: 'V obytnej zóne majú chodci a hry detí prednosť, vodič ich nesmie ohroziť a smie jazdiť najviac 20 km/h.'
    },
    {
      id: 'DZ-037', cat: 2, groups: ['*'],
      q: 'Čo vyjadruje zelené svetlo so šípkou (smerový signál) na semafore?',
      a: ['Voľno len pre smer vyznačený šípkou', 'Voľno pre všetky smery', 'Príkaz zastaviť'],
      c: 0,
      e: 'Pri smerovom signále smie vodič pokračovať len v smere šípky, ostatné smery majú vlastný signál.'
    },
    {
      id: 'DZ-038', cat: 2, groups: ['*'],
      q: 'Čo znamená dvojitá plná pozdĺžna čiara?',
      a: ['Vodič ju nesmie prechádzať ani sa dostať vozidlom do protismeru', 'Možno ju prechádzať pri predchádzaní', 'Označuje odbočovací pruh'],
      c: 0,
      e: 'Dvojitá súvislá čiara prísne oddeľuje protismerné jazdné pruhy.'
    },
    {
      id: 'DZ-039', cat: 2, groups: ['*'],
      q: 'Čo znamená značka „Zákaz odbočenia vpravo“?',
      a: ['V najbližšej križovatke nesmie vodič odbočiť vpravo', 'Vodič nesmie zaraďovať sa do pravého pruhu', 'Vodič nesmie zastaviť vpravo'],
      c: 0,
      e: 'Zákaz odbočenia platí pre najbližšiu križovatku za značkou.'
    },
    {
      id: 'DZ-040', cat: 2, groups: ['*'],
      q: 'Ktorá dopravná značka má prednosť, ak sa vodorovná a zvislá značka odporujú?',
      a: ['Zvislá dopravná značka', 'Vodorovná dopravná značka', 'Vodič si môže vybrať'],
      c: 0,
      e: 'Ak sa údaje zvislej a vodorovnej značky líšia, riadi sa vodič zvislou dopravnou značkou.'
    }
  ]);
})();

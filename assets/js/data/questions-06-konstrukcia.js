/* Okruh 6 – Konštrukcia vozidla, povinná výbava a údržba */
(function () {
  'use strict';
  BANK.add([
    {
      id: 'VOZ-001', cat: 6, groups: ['*'],
      q: 'Čo patrí do povinnej výbavy osobného motorového vozidla?',
      a: ['Lekárnička, prenosný výstražný trojuholník a reflexný bezpečnostný odev',
          'Len lekárnička', 'Hasiaci prístroj a rezervné žiarovky vo všetkých prípadoch'],
      c: 0,
      e: 'Základ povinnej výbavy tvorí lekárnička, výstražný trojuholník, reflexný odev a náhradné koleso alebo prostriedok na opravu defektu.'
    },
    {
      id: 'VOZ-002', cat: 6, groups: ['*'],
      q: 'Aká je najmenšia dovolená hĺbka dezénu pneumatiky osobného automobilu?',
      a: ['1,6 mm', '0,8 mm', '3,5 mm'], c: 0,
      e: 'Pod 1,6 mm je pneumatika nespôsobilá; pri zimných pneumatikách sa vyžaduje väčšia hĺbka dezénu.'
    },
    {
      id: 'VOZ-003', cat: 6, groups: ['*'],
      q: 'Kam umiestni vodič prenosný výstražný trojuholník pri poruche mimo obce?',
      a: ['Najmenej 50 m za vozidlo, na diaľnici najmenej 100 m', 'Priamo za vozidlo do 5 m', 'Pred vozidlo do 20 m'],
      c: 0,
      e: 'Trojuholník musí byť viditeľný dostatočne skoro, aby prichádzajúci vodiči stihli spomaliť.'
    },
    {
      id: 'VOZ-004', cat: 6, groups: ['*'],
      q: 'Čo musí vodič urobiť ako prvé, keď mu vozidlo zostane stáť na ceste pre poruchu?',
      a: ['Zapnúť výstražné svetelné zariadenie a označiť vozidlo trojuholníkom', 'Otvoriť kapotu a hľadať poruchu', 'Volať odťahovú službu ešte pred označením vozidla'],
      c: 0,
      e: 'Prvoradé je varovať ostatných vodičov, aby nevznikla ďalšia nehoda.'
    },
    {
      id: 'VOZ-005', cat: 6, groups: ['*'],
      q: 'Aký vplyv má nízky tlak v pneumatikách?',
      a: ['Zhoršuje ovládateľnosť, zvyšuje spotrebu a opotrebenie pneumatiky', 'Zlepšuje priľnavosť za každých okolností', 'Nemá vplyv na jazdu'],
      c: 0,
      e: 'Podhustená pneumatika sa prehrieva, rýchlejšie sa opotrebuje po okrajoch a môže zlyhať.'
    },
    {
      id: 'VOZ-006', cat: 6, groups: ['*'],
      q: 'Smie vodič jazdiť s nefunkčným stretávacím svetlom?',
      a: ['Nie, vozidlo je technicky nespôsobilé na premávku', 'Áno, ak svieti druhé svetlo', 'Áno, len cez deň'],
      c: 0,
      e: 'Osvetlenie vozidla musí byť funkčné; s nesvietiacim svetlometom vozidlo nespĺňa podmienky prevádzky.'
    },
    {
      id: 'VOZ-007', cat: 6, groups: ['*'],
      q: 'Na čo slúži airbag?',
      a: ['Doplňuje ochranu bezpečnostného pásu pri náraze – nenahrádza ho', 'Nahrádza bezpečnostný pás', 'Chráni vozidlo pred poškodením'],
      c: 0,
      e: 'Airbag je účinný len v kombinácii s pripútaným bezpečnostným pásom.'
    },
    {
      id: 'VOZ-008', cat: 6, groups: ['*'],
      q: 'Kde sa nesmie umiestniť detská sedačka otočená proti smeru jazdy?',
      a: ['Na predné sedadlo s aktívnym airbagom spolujazdca', 'Na zadné sedadlo za vodičom', 'Na zadné sedadlo v strede'],
      c: 0,
      e: 'Airbag by pri aktivácii mohol dieťa vážne zraniť; airbag treba deaktivovať alebo sedačku umiestniť dozadu.'
    },
    {
      id: 'VOZ-009', cat: 6, groups: ['*'],
      q: 'Čo signalizuje rozsvietená červená kontrolka tlaku oleja počas jazdy?',
      a: ['Vážnu poruchu mazania – treba bezodkladne zastaviť a vypnúť motor', 'Že treba doliať palivo', 'Že sú zapnuté hmlové svetlá'],
      c: 0,
      e: 'Pri strate tlaku oleja hrozí zadretie motora; jazdiť ďalej je neprípustné.'
    },
    {
      id: 'VOZ-010', cat: 6, groups: ['*'],
      q: 'Čo znamená rozsvietená kontrolka nabíjania (batérie) počas jazdy?',
      a: ['Porucha dobíjania – alternátor nedobíja batériu', 'Vybité palivo', 'Otvorené dvere'],
      c: 0,
      e: 'Vozidlo pôjde len dovtedy, kým vydrží batéria; poruchu treba čo najskôr odstrániť.'
    },
    {
      id: 'VOZ-011', cat: 6, groups: ['*'],
      q: 'Ako sa prejaví nedostatok brzdovej kvapaliny alebo vzduch v brzdovom systéme?',
      a: ['Brzdový pedál je mäkký, „prepadáva“ a účinok bŕzd je slabší', 'Brzdový pedál je tvrdší ako zvyčajne', 'Nijako sa neprejaví'],
      c: 0,
      e: 'Mäkký pedál je vážna porucha; s takýmto vozidlom sa nesmie jazdiť.'
    },
    {
      id: 'VOZ-012', cat: 6, groups: ['*'],
      q: 'Prečo treba pravidelne kontrolovať stav bŕzd a pneumatík?',
      a: ['Sú rozhodujúce pre bezpečné zastavenie a ovládateľnosť vozidla', 'Kvôli nižšej spotrebe paliva', 'Kvôli hlučnosti vozidla'],
      c: 0,
      e: 'Brzdy a pneumatiky prenášajú všetky sily medzi vozidlom a vozovkou.'
    },
    {
      id: 'VOZ-013', cat: 6, groups: ['*'],
      q: 'Aký je správny postup pri výmene kolesa na ceste?',
      a: ['Zabezpečiť vozidlo, označiť ho trojuholníkom, obliecť si reflexný odev a vymeniť koleso na bezpečnom mieste',
          'Vymeniť koleso na jazdnom pruhu čo najrýchlejšie', 'Vymeniť koleso bez zabezpečenia vozidla'],
      c: 0,
      e: 'Bezpečnosť má prednosť: vozidlo mimo jazdného pruhu, zatiahnutá parkovacia brzda, výstražné svetlá a reflexný odev.'
    },
    {
      id: 'VOZ-014', cat: 6, groups: ['*'],
      q: 'Kedy sa musí použiť náhradné koleso alebo súprava na opravu defektu?',
      a: ['Pri poškodení pneumatiky, ktoré neumožňuje bezpečnú jazdu', 'Len v zime', 'Len na diaľnici'],
      c: 0,
      e: 'S poškodenou pneumatikou sa nesmie pokračovať v jazde – hrozí strata ovládateľnosti.'
    },
    {
      id: 'VOZ-015', cat: 6, groups: ['*'],
      q: 'Ako často sa podrobuje bežné osobné vozidlo technickej kontrole (po prvej kontrole)?',
      a: ['Spravidla každé dva roky', 'Každých päť rokov', 'Len pri predaji vozidla'],
      c: 0,
      e: 'Nové osobné vozidlo ide na prvú kontrolu po štyroch rokoch a potom pravidelne každé dva roky.'
    },
    {
      id: 'VOZ-016', cat: 6, groups: ['*'],
      q: 'Na čo slúži systém ESP (stabilizačný systém)?',
      a: ['Cielene pribrzďuje kolesá a pomáha udržať vozidlo v požadovanom smere', 'Zvyšuje výkon motora', 'Nahrádza brzdy'],
      c: 0,
      e: 'ESP dokáže korigovať šmyk, ale nedokáže prekonať fyzikálne zákony – rýchlosť treba prispôsobiť podmienkam.'
    },
    {
      id: 'VOZ-017', cat: 6, groups: ['*'],
      q: 'Čo je potrebné skontrolovať pred dlhou jazdou?',
      a: ['Tlak a stav pneumatík, hladiny prevádzkových kvapalín, funkčnosť svetiel a stieračov',
          'Len množstvo paliva', 'Len tlak v pneumatikách'],
      c: 0,
      e: 'Krátka kontrola pred jazdou odhalí väčšinu porúch, ktoré by na ceste spôsobili problém.'
    },
    {
      id: 'VOZ-018', cat: 6, groups: ['*'],
      q: 'Prečo je zakázané jazdiť so znečisteným alebo poškodeným čelným sklom vo výhľade vodiča?',
      a: ['Znižuje to výhľad a bezpečnosť jazdy', 'Zvyšuje to spotrebu paliva', 'Nie je to zakázané'],
      c: 0,
      e: 'Vodič musí mať výhľad z vozidla voľný a nezakrytý; poškodené sklo v poli výhľadu je dôvodom na nespôsobilosť vozidla.'
    },
    {
      id: 'VOZ-019', cat: 6, groups: ['*'],
      q: 'Ako sa musia nastaviť svetlomety vozidla?',
      a: ['Tak, aby dostatočne osvetľovali vozovku a neoslňovali ostatných vodičov', 'Čo najvyššie pre lepší dosvit', 'Nastavenie nie je dôležité'],
      c: 0,
      e: 'Pri naloženom vozidle treba použiť korektor sklonu svetlometov.'
    },
    {
      id: 'VOZ-020', cat: 6, groups: ['*'],
      q: 'Čo znamená, ak z výfuku vychádza hustý čierny alebo modrý dym?',
      a: ['Ide o poruchu motora, vozidlo môže nadmerne znečisťovať ovzdušie', 'Je to normálny stav pri studenom motore', 'Motor pracuje úsporne'],
      c: 0,
      e: 'Nadmerné dymenie je dôvodom nespôsobilosti vozidla; poruchu treba dať odstrániť.'
    },
    {
      id: 'VOZ-021', cat: 6, groups: ['*'],
      q: 'Aký je účel spätných zrkadiel a ako majú byť nastavené?',
      a: ['Majú poskytovať výhľad dozadu; nastavujú sa pred jazdou tak, aby čo najviac zmenšili mŕtvy uhol',
          'Slúžia najmä na kontrolu posádky', 'Nastavenie zrkadiel nie je podstatné'],
      c: 0,
      e: 'Správne nastavené zrkadlá výrazne zmenšujú nebezpečné mŕtve uhly, ale úplne ich neodstránia.'
    },
    {
      id: 'VOZ-022', cat: 6, groups: ['*'],
      q: 'Ako treba postupovať pri pripájaní prívesu k vozidlu?',
      a: ['Skontrolovať spojovacie zariadenie, poistku, poistné lanko a funkčnosť osvetlenia prívesu',
          'Stačí zavesiť príves na guľu', 'Osvetlenie prívesu netreba kontrolovať cez deň'],
      c: 0,
      e: 'Nesprávne pripojený príves sa môže odpojiť; osvetlenie a smerovky prívesu musia fungovať vždy.'
    },
    {
      id: 'VOZ-023', cat: 6, groups: ['*'],
      q: 'Prečo sa nesmie prekročiť najväčšia povolená celková hmotnosť vozidla?',
      a: ['Preťažené vozidlo má horšie brzdenie, ovládateľnosť a poškodzuje cestu', 'Ide len o daňový údaj', 'Prekročenie je povolené o 20 %'],
      c: 0,
      e: 'Preťaženie mení jazdné vlastnosti a je porušením podmienok prevádzky vozidla.'
    },
    {
      id: 'VOZ-024', cat: 6, groups: ['*'],
      q: 'Ako sa má vodič zachovať, keď počas jazdy zbadá dym spod kapoty?',
      a: ['Bezpečne zastaviť mimo vozovky, vypnúť motor a opustiť vozidlo do bezpečnej vzdialenosti',
          'Pokračovať do najbližšieho servisu', 'Otvoriť kapotu ihneď po zastavení'],
      c: 0,
      e: 'Pri riziku požiaru je prvoradá bezpečnosť posádky; kapotu treba otvárať opatrne, prívod vzduchu môže oheň rozdúchať.'
    },
    {
      id: 'VOZ-025', cat: 6, groups: ['*'],
      q: 'Kedy je vhodné použiť snehové reťaze?',
      a: ['Na súvislej snehovej alebo ľadovej vrstve, ak to dovoľuje dopravná značka alebo stav vozovky',
          'Na suchej vozovke pre lepší záber', 'Vždy v zimnom období'],
      c: 0,
      e: 'Na vozovke bez súvislej snehovej vrstvy by reťaze poškodili vozovku aj vozidlo.'
    },
    {
      id: 'VOZ-026', cat: 6, groups: ['*'],
      q: 'Čo je potrebné urobiť s obsahom lekárničky vo vozidle?',
      a: ['Kontrolovať dátum exspirácie a v prípade potreby obsah vymeniť', 'Nič, lekárnička vydrží navždy', 'Vymeniť ju pri každej technickej kontrole'],
      c: 0,
      e: 'Lekárnička s prepadnutou exspiráciou nespĺňa požiadavky povinnej výbavy.'
    }
  ]);
})();

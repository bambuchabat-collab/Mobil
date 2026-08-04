/* Okruh 5 – Teória vedenia vozidla */
(function () {
  'use strict';
  BANK.add([
    {
      id: 'TEO-001', cat: 5, groups: ['*'],
      q: 'Z čoho sa skladá celková dráha potrebná na zastavenie vozidla?',
      a: ['Z reakčnej dráhy a brzdnej dráhy', 'Len z brzdnej dráhy', 'Z brzdnej dráhy a dĺžky vozidla'],
      c: 0,
      e: 'Kým vodič zareaguje, vozidlo prejde reakčnú dráhu; až potom začína brzdiť.'
    },
    {
      id: 'TEO-002', cat: 5, groups: ['*'],
      q: 'Ako sa zmení brzdná dráha, ak vodič zdvojnásobí rýchlosť jazdy?',
      a: ['Predĺži sa približne štyrikrát', 'Predĺži sa dvakrát', 'Nezmení sa'],
      c: 0,
      e: 'Brzdná dráha rastie s druhou mocninou rýchlosti – dvojnásobná rýchlosť znamená približne štvornásobnú brzdnú dráhu.'
    },
    {
      id: 'TEO-003', cat: 5, groups: ['*'],
      q: 'Aký je odporúčaný časový odstup od vozidla idúceho vpredu za dobrého počasia?',
      a: ['Približne 2 sekundy', 'Približne 0,5 sekundy', 'Odstup netreba merať v čase'],
      c: 0,
      e: 'Pravidlo dvoch sekúnd dáva čas na reakciu; v daždi a na snehu treba odstup zdvojnásobiť.'
    },
    {
      id: 'TEO-004', cat: 5, groups: ['*'],
      q: 'Čo je aquaplaning?',
      a: ['Strata kontaktu pneumatiky s vozovkou pre vodný film medzi pneumatikou a povrchom',
          'Zahmlievanie okien pri daždi', 'Preklzávanie spojky pri rozjazde'],
      c: 0,
      e: 'Pri aquaplaningu vozidlo prestane reagovať na volant a brzdy; treba ubrať plyn a nebrzdiť prudko.'
    },
    {
      id: 'TEO-005', cat: 5, groups: ['*'],
      q: 'Ako má vodič reagovať pri vzniku aquaplaningu?',
      a: ['Plynulo ubrať plyn, držať volant priamo a nebrzdiť prudko', 'Prudko zabrzdiť', 'Prudko strhnúť volant'],
      c: 0,
      e: 'Prudké manévre pri strate priľnavosti spôsobia šmyk; treba počkať, kým pneumatiky opäť „chytia“.'
    },
    {
      id: 'TEO-006', cat: 5, groups: ['*'],
      q: 'Prečo je pri dlhom klesaní vhodné brzdiť motorom (zaradiť nižší prevodový stupeň)?',
      a: ['Aby sa prevádzkové brzdy neprehriali a nestratili účinok', 'Aby sa šetrilo palivo', 'Aby vozidlo išlo rýchlejšie'],
      c: 0,
      e: 'Dlhé brzdenie prevádzkovou brzdou vedie k prehriatiu a strate brzdného účinku; brzdenie motorom brzdy chráni.'
    },
    {
      id: 'TEO-007', cat: 5, groups: ['*'],
      q: 'Ako pôsobí odstredivá sila v zákrute?',
      a: ['Tlačí vozidlo von zo zákruty a rastie s druhou mocninou rýchlosti', 'Tlačí vozidlo do stredu zákruty', 'Nemá vplyv na jazdu'],
      c: 0,
      e: 'Preto treba spomaliť pred zákrutou, nie v nej; v zákrute sa jazdí plynulo s miernym plynom.'
    },
    {
      id: 'TEO-008', cat: 5, groups: ['*'],
      q: 'Ako sa má správať vodič, ak sa dostane do šmyku zadnej nápravy (pretáčavý šmyk)?',
      a: ['Ubrať plyn a natočiť volant v smere šmyku (kontrovať)', 'Prudko zabrzdiť a držať volant priamo', 'Pridať plyn a strhnúť volant proti šmyku'],
      c: 0,
      e: 'Pri pretáčavom šmyku sa volantom vyrovnáva smer – tzv. kontrovanie, bez prudkého brzdenia.'
    },
    {
      id: 'TEO-009', cat: 5, groups: ['*'],
      q: 'Čo robí systém ABS pri intenzívnom brzdení?',
      a: ['Zabraňuje zablokovaniu kolies, takže vodič môže počas brzdenia riadiť', 'Skracuje brzdnú dráhu na ľade na polovicu', 'Nahrádza pozornosť vodiča'],
      c: 0,
      e: 'ABS udržiava ovládateľnosť vozidla; brzdnú dráhu nemusí vždy skrátiť, napríklad na snehu môže byť dlhšia.'
    },
    {
      id: 'TEO-010', cat: 5, groups: ['*'],
      q: 'Ako sa mení priľnavosť pneumatík pri prvom daždi po dlhom suchu?',
      a: ['Výrazne klesá, lebo voda zmieša prach a olej na vozovke', 'Zvyšuje sa', 'Nemení sa'],
      c: 0,
      e: 'Prvé minúty dažďa sú najnebezpečnejšie – vozovka je mimoriadne klzká.'
    },
    {
      id: 'TEO-011', cat: 5, groups: ['*'],
      q: 'Kde vzniká námraza na ceste najskôr?',
      a: ['Na mostoch, v tieni a v blízkosti vodných tokov', 'Na rovných úsekoch na slnku', 'Na diaľniciach s hustou premávkou'],
      c: 0,
      e: 'Mosty premŕzajú zospodu aj zvrchu, preto sú klzké skôr než ostatné časti cesty.'
    },
    {
      id: 'TEO-012', cat: 5, groups: ['*'],
      q: 'Ako má vodič svietiť v hustej hmle?',
      a: ['Stretávacími svetlami, prípadne hmlovými svetlami – nie diaľkovými', 'Diaľkovými svetlami', 'Len obrysovými svetlami'],
      c: 0,
      e: 'Diaľkové svetlá sa v hmle odrážajú späť a oslňujú vodiča; hmlové svetlá zlepšujú viditeľnosť pri okraji cesty.'
    },
    {
      id: 'TEO-013', cat: 5, groups: ['*'],
      q: 'Čo je „mŕtvy uhol“ (slepý uhol) vozidla?',
      a: ['Priestor okolo vozidla, ktorý vodič nevidí v zrkadlách', 'Miesto, kde nesvietia svetlá', 'Časť vozovky za horizontom'],
      c: 0,
      e: 'Pred zmenou jazdného pruhu je nutné otočiť hlavu a skontrolovať priestor vedľa vozidla.'
    },
    {
      id: 'TEO-014', cat: 5, groups: ['*'],
      q: 'Ako sa má vodič zachovať, keď ho oslní protiidúce vozidlo?',
      a: ['Znížiť rýchlosť, sledovať pravý okraj vozovky a v prípade potreby zastaviť',
          'Rozsvietiť diaľkové svetlá', 'Pokračovať v jazde rovnakou rýchlosťou'],
      c: 0,
      e: 'Pri oslnení sa vodič orientuje podľa pravého okraja vozovky a spomalí, kým sa zrak neprispôsobí.'
    },
    {
      id: 'TEO-015', cat: 5, groups: ['*'],
      q: 'Ako ovplyvňuje náklad na streche jazdné vlastnosti vozidla?',
      a: ['Zvyšuje ťažisko, zhoršuje stabilitu v zákrutách a predlžuje brzdnú dráhu', 'Zlepšuje priľnavosť', 'Nemá žiadny vplyv'],
      c: 0,
      e: 'S nákladom na streche treba jazdiť pomalšie a plynulejšie, najmä v zákrutách a pri bočnom vetre.'
    },
    {
      id: 'TEO-016', cat: 5, groups: ['*'],
      q: 'Ako sa prejaví bočný vietor pri výjazde z tunela alebo spoza mosta?',
      a: ['Vozidlo môže náhle vybočiť – treba pevne držať volant a spomaliť', 'Vozidlo sa spomalí samo', 'Zlepší sa priľnavosť pneumatík'],
      c: 0,
      e: 'Na miestach, kde končí ochrana pred vetrom, vodiča prekvapí náraz vetra; ohrozené sú najmä vysoké vozidlá a motocykle.'
    },
    {
      id: 'TEO-017', cat: 5, groups: ['*'],
      q: 'Ako sa má jazdiť v tuneli?',
      a: ['Dodržiavať odstup, zapnúť stretávacie svetlá, nepredchádzať, ak je to zakázané, a nezastavovať',
          'Zapnúť diaľkové svetlá a zrýchliť', 'Zastaviť pri prvom núdzovom zálive a skontrolovať vozidlo'],
      c: 0,
      e: 'V tuneli je zakázané otáčanie, cúvanie a zastavenie mimo núdzových zálivov.'
    },
    {
      id: 'TEO-018', cat: 5, groups: ['*'],
      q: 'Ako sa mení reakčný čas vodiča pri únave alebo po požití alkoholu?',
      a: ['Predlžuje sa, a tým sa predlžuje aj celková dráha zastavenia', 'Skracuje sa', 'Nemení sa'],
      c: 0,
      e: 'Bežný reakčný čas je približne 1 sekunda; únava, alkohol aj rozptýlenie ho výrazne predlžujú.'
    },
    {
      id: 'TEO-019', cat: 5, groups: ['*'],
      q: 'Prečo treba pred zákrutou spomaliť ešte pred jej začiatkom?',
      a: ['Aby vodič nemusel brzdiť v zákrute, kde hrozí strata priľnavosti a šmyk', 'Aby ušetril palivo', 'Aby ho nepredbehli iné vozidlá'],
      c: 0,
      e: 'V zákrute sú pneumatiky zaťažené bočnými silami; brzdenie v nej môže spôsobiť šmyk.'
    },
    {
      id: 'TEO-020', cat: 5, groups: ['*'],
      q: 'Aký vplyv má opotrebovaný dezén pneumatík na jazdu v daždi?',
      a: ['Zvyšuje riziko aquaplaningu a predlžuje brzdnú dráhu', 'Zlepšuje priľnavosť', 'Nemá vplyv, ak je tlak správny'],
      c: 0,
      e: 'Dezén odvádza vodu spod pneumatiky; plytký dezén vodu neodvedie a pneumatika stráca kontakt s vozovkou.'
    },
    {
      id: 'TEO-021', cat: 5, groups: ['*'],
      q: 'Ako sa má vodič správať pri predchádzaní dlhého nákladného vozidla?',
      a: ['Zvážiť, či má dostatok priestoru a výhľadu, a predchádzať plynule a rýchlo, ale bezpečne',
          'Predchádzať v zákrute, kde je lepší výhľad', 'Predchádzať tesne pred vrcholom stúpania'],
      c: 0,
      e: 'Predchádzanie dlhého vozidla trvá dlhšie; vodič musí mať dostatočný výhľad a rezervu do protismeru.'
    },
    {
      id: 'TEO-022', cat: 5, groups: ['*'],
      q: 'Čo znamená defenzívna jazda?',
      a: ['Predvídať chyby ostatných a jazdiť tak, aby vodič mal vždy možnosť bezpečne reagovať',
          'Jazdiť čo najpomalšie', 'Jazdiť len v pravom pruhu'],
      c: 0,
      e: 'Defenzívny vodič počíta s chybami iných a udržiava si priestor na únik.'
    },
    {
      id: 'TEO-023', cat: 5, groups: ['*'],
      q: 'Ako sa mení spotreba paliva a bezpečnosť pri agresívnej jazde (prudké zrýchľovanie a brzdenie)?',
      a: ['Spotreba rastie a bezpečnosť klesá', 'Spotreba klesá a bezpečnosť rastie', 'Nič sa nemení'],
      c: 0,
      e: 'Plynulá jazda šetrí palivo aj brzdy a znižuje riziko nehody.'
    },
    {
      id: 'TEO-024', cat: 5, groups: ['*'],
      q: 'Ako vplýva zaťaženie vozidla na jeho brzdnú dráhu?',
      a: ['Plne naložené vozidlo má dlhšiu brzdnú dráhu', 'Naložené vozidlo brzdí kratšie', 'Zaťaženie brzdnú dráhu neovplyvňuje'],
      c: 0,
      e: 'Väčšia hmotnosť znamená väčšiu kinetickú energiu, ktorú musia brzdy premeniť na teplo.'
    },
    {
      id: 'TEO-025', cat: 5, groups: ['*'],
      q: 'Ako sa má vodič zachovať pri jazde za cyklistom alebo motocyklistom?',
      a: ['Dodržiavať väčší odstup, lebo môžu náhle vybočiť pre nerovnosti alebo vietor',
          'Jazdiť tesne za nimi, aby ich mohol rýchlo predbehnúť', 'Používať zvukové znamenie'],
      c: 0,
      e: 'Jednostopové vozidlá sú zraniteľné a ich dráha môže byť nestabilná; treba im dať priestor.'
    },
    {
      id: 'TEO-026', cat: 5, groups: ['*'],
      q: 'Prečo je nebezpečné jazdiť v noci rovnakou rýchlosťou ako cez deň?',
      a: ['Dohľad je obmedzený svetlami – vodič musí byť schopný zastaviť na vzdialenosť, na ktorú vidí',
          'V noci je menšia priľnavosť pneumatík', 'V noci sa skracuje reakčný čas'],
      c: 0,
      e: 'Rýchlosť treba prispôsobiť dosvitu svetiel, aby vodič dokázal zastaviť pred prekážkou, ktorú osvetlí.'
    }
  ]);
})();

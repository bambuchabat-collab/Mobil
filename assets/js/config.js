/**
 * Konfigurácia aplikácie – skupiny vodičského oprávnenia, tematické okruhy
 * a bodovanie testu.
 *
 * Celý model testu (počet otázok, body, hranica úspešnosti, časový limit)
 * je zámerne na jednom mieste, aby sa dal jednoducho upraviť.
 */
(function (global) {
  'use strict';

  /* Tematické okruhy otázok.
     count = počet otázok v jednom teste, points = body za správnu odpoveď.
     Spolu 27 otázok a 50 bodov. */
  var CATEGORIES = [
    { id: 1, count: 5, points: 3, name: 'Pravidlá cestnej premávky', short: 'Pravidlá' },
    { id: 2, count: 5, points: 2, name: 'Dopravné značky a zariadenia', short: 'Značky' },
    { id: 3, count: 4, points: 3, name: 'Prednosť v jazde a križovatky', short: 'Križovatky' },
    { id: 4, count: 4, points: 1, name: 'Všeobecné predpisy a doklady', short: 'Predpisy' },
    { id: 5, count: 3, points: 1, name: 'Teória vedenia vozidla', short: 'Teória jazdy' },
    { id: 6, count: 3, points: 1, name: 'Konštrukcia a údržba vozidla', short: 'Vozidlo' },
    { id: 7, count: 3, points: 1, name: 'Bezpečná jazda a prvá pomoc', short: 'Bezpečnosť' }
  ];

  var TEST = {
    questions: 27,        // otázok v teste
    maxPoints: 50,        // maximálny počet bodov
    passPoints: 45,       // hranica na úspešné absolvovanie (90 %)
    timeLimitSec: 20 * 60,// časový limit testu
    testsPerGroup: 10     // koľko testov má každá skupina
  };

  /* Skupiny vodičského oprávnenia. `pack` je kód balíka otázok navyše,
     ktoré sa pridávajú k spoločnému základu (viď data/questions-90-skupiny.js). */
  var GROUPS = [
    { id: 'B',  pack: 'B',  name: 'Skupina B',  desc: 'Osobné auto do 3 500 kg', icon: '🚗' },
    { id: 'A',  pack: 'A',  name: 'Skupina A',  desc: 'Motocykle (AM, A1, A2, A)', icon: '🏍️' },
    { id: 'C',  pack: 'C',  name: 'Skupina C',  desc: 'Nákladné vozidlá nad 3 500 kg', icon: '🚚' },
    { id: 'D',  pack: 'D',  name: 'Skupina D',  desc: 'Autobusy a preprava osôb', icon: '🚌' },
    { id: 'T',  pack: 'T',  name: 'Skupina T',  desc: 'Traktory a pracovné stroje', icon: '🚜' },
    { id: 'BE', pack: 'BE', name: 'Skupina B+E', desc: 'Osobné auto s prívesom', icon: '🚙' }
  ];

  global.CFG = {
    CATEGORIES: CATEGORIES,
    GROUPS: GROUPS,
    TEST: TEST,
    category: function (id) {
      for (var i = 0; i < CATEGORIES.length; i++) {
        if (CATEGORIES[i].id === id) return CATEGORIES[i];
      }
      return null;
    },
    group: function (id) {
      for (var i = 0; i < GROUPS.length; i++) {
        if (GROUPS[i].id === id) return GROUPS[i];
      }
      return null;
    }
  };
})(typeof window !== 'undefined' ? window : globalThis);

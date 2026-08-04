/**
 * Banka otázok + deterministické zostavovanie testov.
 *
 * Otázky sa registrujú v súboroch assets/js/data/*.js cez BANK.add([...]).
 * Formát otázky:
 *   { id: 'PCP-001', cat: 1, groups: ['*'], q: 'text', a: ['A','B','C'], c: 0, e: 'vysvetlenie' }
 *   groups: ['*'] = otázka pre všetky skupiny, inak zoznam skupín ('B', 'C', ...)
 *   c = index správnej odpovede v poli a
 */
(function (global) {
  'use strict';

  var CFG = global.CFG;
  var all = [];
  var byId = Object.create(null);

  /* ---------- deterministický generátor náhodných čísel ---------- */

  function hashSeed(str) {
    var h = 2166136261 >>> 0;
    for (var i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h >>> 0;
  }

  function mulberry32(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function shuffle(arr, rng) {
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(rng() * (i + 1));
      var tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    }
    return arr;
  }

  /* ---------- registrácia otázok ---------- */

  function add(list) {
    for (var i = 0; i < list.length; i++) {
      var q = list[i];
      if (byId[q.id]) throw new Error('Duplicitné ID otázky: ' + q.id);
      byId[q.id] = q;
      all.push(q);
    }
  }

  function forGroup(groupId, catId) {
    var out = [];
    for (var i = 0; i < all.length; i++) {
      var q = all[i];
      if (catId != null && q.cat !== catId) continue;
      if (q.groups.indexOf('*') === -1 && q.groups.indexOf(groupId) === -1) continue;
      out.push(q);
    }
    return out;
  }

  /**
   * Rozdelí otázky okruhu medzi všetky testy skupiny tak, aby sa v jednom
   * teste žiadna otázka neopakovala a aby sa banka využila čo najrovnomernejšie.
   */
  function dealSequence(pool, total, blockSize, rng) {
    var seq = [];
    var bag = [];
    while (seq.length < total) {
      if (!bag.length) bag = shuffle(pool.slice(), rng);
      var blockStart = Math.floor(seq.length / blockSize) * blockSize;
      var idx = 0;
      while (idx < bag.length && seq.indexOf(bag[idx], blockStart) !== -1) idx++;
      if (idx === bag.length) idx = 0; // menej otázok ako je veľkosť bloku
      seq.push(bag.splice(idx, 1)[0]);
    }
    return seq;
  }

  /**
   * Vráti otázky testu č. `testNo` (1..testsPerGroup) pre danú skupinu.
   * Výber je deterministický – rovnaký test má vždy rovnaké otázky.
   */
  function buildTest(groupId, testNo) {
    var cats = CFG.CATEGORIES;
    var perGroup = CFG.TEST.testsPerGroup;
    var questions = [];

    for (var i = 0; i < cats.length; i++) {
      var cat = cats[i];
      var pool = forGroup(groupId, cat.id);
      if (!pool.length) throw new Error('Prázdna banka otázok pre okruh ' + cat.id);
      var rng = mulberry32(hashSeed('autoskola|' + groupId + '|cat' + cat.id));
      var seq = dealSequence(pool, perGroup * cat.count, cat.count, rng);
      var start = (testNo - 1) * cat.count;
      questions = questions.concat(seq.slice(start, start + cat.count));
    }
    return questions;
  }

  /** Náhodný test – rovnaká skladba okruhov, ale otázky sa losujú nanovo. */
  function buildRandomTest(groupId, seed) {
    var cats = CFG.CATEGORIES;
    var rng = mulberry32(seed >>> 0);
    var questions = [];
    for (var i = 0; i < cats.length; i++) {
      var cat = cats[i];
      var pool = shuffle(forGroup(groupId, cat.id).slice(), rng);
      questions = questions.concat(pool.slice(0, cat.count));
    }
    return questions;
  }

  /** Poradie odpovedí – deterministické pre daný test, voliteľne premiešané. */
  function answerOrder(question, seedStr, doShuffle) {
    var order = [];
    for (var i = 0; i < question.a.length; i++) order.push(i);
    if (!doShuffle) return order;
    return shuffle(order, mulberry32(hashSeed(seedStr + '|' + question.id)));
  }

  global.BANK = {
    add: add,
    all: function () { return all.slice(); },
    get: function (id) { return byId[id]; },
    forGroup: forGroup,
    buildTest: buildTest,
    buildRandomTest: buildRandomTest,
    answerOrder: answerOrder,
    hashSeed: hashSeed,
    mulberry32: mulberry32
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = global.BANK;
})(typeof window !== 'undefined' ? window : globalThis);

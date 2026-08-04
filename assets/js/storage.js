/**
 * Ukladanie výsledkov a nastavení do localStorage.
 * Všetko je uložené pod jedným kľúčom, aby sa dalo jednoducho zmazať.
 */
(function (global) {
  'use strict';

  var KEY = 'autoskola-testy-v1';
  var state = null;

  function defaults() {
    return {
      group: null,
      settings: { shuffleAnswers: true, timer: true, instantFeedback: false },
      results: {} // 'B|3' -> { attempts, best, bestPct, lastPoints, passed, updated }
    };
  }

  function load() {
    if (state) return state;
    try {
      var raw = global.localStorage.getItem(KEY);
      state = raw ? JSON.parse(raw) : defaults();
    } catch (e) {
      state = defaults();
    }
    var d = defaults();
    if (!state.settings) state.settings = d.settings;
    if (!state.results) state.results = d.results;
    for (var k in d.settings) {
      if (typeof state.settings[k] !== 'boolean') state.settings[k] = d.settings[k];
    }
    return state;
  }

  function save() {
    try {
      global.localStorage.setItem(KEY, JSON.stringify(load()));
    } catch (e) { /* súkromný režim – ticho ignorujeme */ }
  }

  function key(groupId, testNo) { return groupId + '|' + testNo; }

  var STORE = {
    settings: function () { return load().settings; },
    setSetting: function (name, value) { load().settings[name] = value; save(); },

    group: function () { return load().group; },
    setGroup: function (groupId) { load().group = groupId; save(); },

    result: function (groupId, testNo) { return load().results[key(groupId, testNo)] || null; },

    saveResult: function (groupId, testNo, points, maxPoints, passed) {
      var s = load();
      var k = key(groupId, testNo);
      var r = s.results[k] || { attempts: 0, best: 0, passed: false };
      r.attempts += 1;
      r.lastPoints = points;
      r.best = Math.max(r.best || 0, points);
      r.bestPct = Math.round((r.best / maxPoints) * 100);
      r.passed = r.passed || passed;
      r.updated = Date.now();
      s.results[k] = r;
      save();
      return r;
    },

    /** Súhrn za skupinu: koľko testov je splnených, priemer, počet pokusov. */
    groupStats: function (groupId, testsPerGroup, maxPoints) {
      var s = load();
      var done = 0, passed = 0, attempts = 0, bestSum = 0;
      for (var i = 1; i <= testsPerGroup; i++) {
        var r = s.results[key(groupId, i)];
        if (!r) continue;
        done += 1;
        attempts += r.attempts;
        bestSum += r.best;
        if (r.passed) passed += 1;
      }
      return {
        done: done,
        passed: passed,
        attempts: attempts,
        avgPct: done ? Math.round((bestSum / (done * maxPoints)) * 100) : 0
      };
    },

    resetGroup: function (groupId, testsPerGroup) {
      var s = load();
      for (var i = 1; i <= testsPerGroup; i++) delete s.results[key(groupId, i)];
      save();
    },

    resetAll: function () { state = defaults(); save(); }
  };

  global.STORE = STORE;
})(typeof window !== 'undefined' ? window : globalThis);

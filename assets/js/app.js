/**
 * Autoškola testy – logika aplikácie a vykresľovanie obrazoviek.
 * Bez frameworku, aby sa aplikácia dala otvoriť aj priamo zo súboru v mobile.
 */
(function () {
  'use strict';

  var app = document.getElementById('app');
  var topbarTitle = document.getElementById('topbarTitle');
  var topbarSlot = document.getElementById('topbarSlot');
  var btnBack = document.getElementById('btnBack');
  var sheet = document.getElementById('sheet');

  var state = {
    screen: 'home',   // home | tests | test | result | review | stats
    group: STORE.group() || null,
    run: null,        // prebiehajúci alebo dokončený test
    reviewOnlyWrong: false
  };
  var timerId = null;

  /* ------------------------------------------------------------------ */
  /* pomocné funkcie na tvorbu DOM                                       */
  /* ------------------------------------------------------------------ */

  function h(tag, opts, children) {
    var node = document.createElement(tag);
    opts = opts || {};
    if (opts.cls) node.className = opts.cls;
    if (opts.text != null) node.textContent = opts.text;
    if (opts.html != null) node.innerHTML = opts.html;
    if (opts.attrs) {
      for (var a in opts.attrs) node.setAttribute(a, opts.attrs[a]);
    }
    if (opts.on) {
      for (var ev in opts.on) node.addEventListener(ev, opts.on[ev]);
    }
    (children || []).forEach(function (child) {
      if (child) node.appendChild(child);
    });
    return node;
  }

  function fmtTime(sec) {
    sec = Math.max(0, Math.round(sec));
    var m = Math.floor(sec / 60), s = sec % 60;
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function showSheet(title, text, actions) {
    document.getElementById('sheetTitle').textContent = title;
    document.getElementById('sheetText').textContent = text || '';
    var box = document.getElementById('sheetActions');
    box.innerHTML = '';
    actions.forEach(function (a) {
      box.appendChild(h('button', {
        cls: 'btn ' + (a.kind || 'btn--ghost'),
        text: a.label,
        attrs: { type: 'button' },
        on: { click: function () { hideSheet(); if (a.onClick) a.onClick(); } }
      }));
    });
    sheet.hidden = false;
  }

  function hideSheet() { sheet.hidden = true; }

  sheet.addEventListener('click', function (e) {
    if (e.target.getAttribute('data-close')) hideSheet();
  });

  /* ------------------------------------------------------------------ */
  /* priebeh testu                                                       */
  /* ------------------------------------------------------------------ */

  function startTest(groupId, testNo) {
    var questions = testNo === 0
      ? BANK.buildRandomTest(groupId, Date.now())
      : BANK.buildTest(groupId, testNo);
    var seed = 'test|' + groupId + '|' + (testNo === 0 ? Date.now() : testNo);
    var shuffleOn = STORE.settings().shuffleAnswers;

    state.run = {
      groupId: groupId,
      testNo: testNo,
      questions: questions,
      orders: questions.map(function (q) { return BANK.answerOrder(q, seed, shuffleOn); }),
      answers: questions.map(function () { return null; }),
      current: 0,
      startedAt: Date.now(),
      remaining: CFG.TEST.timeLimitSec,
      finished: false,
      score: null
    };
    state.screen = 'test';
    startTimer();
    render();
  }

  function startTimer() {
    stopTimer();
    if (!STORE.settings().timer) return;
    timerId = setInterval(function () {
      var run = state.run;
      if (!run || run.finished) { stopTimer(); return; }
      run.remaining -= 1;
      var box = document.getElementById('timer');
      if (box) {
        box.textContent = fmtTime(run.remaining);
        box.classList.toggle('is-low', run.remaining <= 120);
      }
      if (run.remaining <= 0) {
        stopTimer();
        finishTest(true);
      }
    }, 1000);
  }

  function stopTimer() {
    if (timerId) { clearInterval(timerId); timerId = null; }
  }

  function scoreRun(run) {
    var byCat = {};
    var points = 0, correct = 0;
    CFG.CATEGORIES.forEach(function (c) {
      byCat[c.id] = { earned: 0, max: c.count * c.points, correct: 0, count: 0 };
    });
    run.questions.forEach(function (q, i) {
      var cat = CFG.category(q.cat);
      var rec = byCat[q.cat];
      rec.count += 1;
      if (run.answers[i] === q.c) {
        points += cat.points;
        correct += 1;
        rec.earned += cat.points;
        rec.correct += 1;
      }
    });
    return {
      points: points,
      correct: correct,
      total: run.questions.length,
      passed: points >= CFG.TEST.passPoints,
      byCat: byCat,
      timeUsed: STORE.settings().timer
        ? CFG.TEST.timeLimitSec - run.remaining
        : Math.round((Date.now() - run.startedAt) / 1000)
    };
  }

  function finishTest(auto) {
    var run = state.run;
    if (!run || run.finished) return;
    var unanswered = run.answers.filter(function (a) { return a === null; }).length;

    function done() {
      stopTimer();
      run.finished = true;
      run.score = scoreRun(run);
      if (run.testNo !== 0) {
        STORE.saveResult(run.groupId, run.testNo, run.score.points, CFG.TEST.maxPoints, run.score.passed);
      }
      state.screen = 'result';
      render();
    }

    if (!auto && unanswered > 0) {
      showSheet(
        'Ukončiť test?',
        'Bez odpovede ' + (unanswered === 1 ? 'ostala 1 otázka.' : 'ostalo ' + unanswered + ' otázok.') +
        ' Nezodpovedané otázky sa počítajú ako nesprávne.',
        [
          { label: 'Vyhodnotiť test', kind: 'btn--primary', onClick: done },
          { label: 'Pokračovať v teste' }
        ]
      );
      return;
    }
    done();
  }

  function leaveTest() {
    showSheet('Ukončiť rozpracovaný test?', 'Odpovede sa neuložia.', [
      { label: 'Ukončiť', kind: 'btn--danger', onClick: function () {
        stopTimer();
        state.run = null;
        state.screen = 'tests';
        render();
      } },
      { label: 'Späť do testu' }
    ]);
  }

  /* ------------------------------------------------------------------ */
  /* obrazovky                                                           */
  /* ------------------------------------------------------------------ */

  function screenHome() {
    var wrap = h('div', { cls: 'screen' });

    wrap.appendChild(h('div', { cls: 'hero' }, [
      h('h1', { cls: 'hero__title', text: 'Autoškola testy' }),
      h('p', { cls: 'hero__sub', text: 'Vyber si skupinu vodičského oprávnenia a precvičuj sa na ' + CFG.TEST.testsPerGroup + ' testoch.' })
    ]));

    wrap.appendChild(h('h2', { cls: 'section-title', text: 'Skupina vodičského oprávnenia' }));

    var grid = h('div', { cls: 'grid' });
    CFG.GROUPS.forEach(function (g) {
      var st = STORE.groupStats(g.id, CFG.TEST.testsPerGroup, CFG.TEST.maxPoints);
      var card = h('button', {
        cls: 'card card--group' + (state.group === g.id ? ' is-active' : ''),
        attrs: { type: 'button' },
        on: { click: function () {
          state.group = g.id;
          STORE.setGroup(g.id);
          state.screen = 'tests';
          render();
        } }
      }, [
        h('span', { cls: 'card__icon', text: g.icon }),
        h('span', { cls: 'card__body' }, [
          h('span', { cls: 'card__title', text: g.name }),
          h('span', { cls: 'card__desc', text: g.desc }),
          st.done ? h('span', { cls: 'card__meta', text: 'Splnené ' + st.passed + '/' + CFG.TEST.testsPerGroup + ' · úspešnosť ' + st.avgPct + ' %' }) : null
        ]),
        h('span', { cls: 'card__chev', text: '›' })
      ]);
      grid.appendChild(card);
    });
    wrap.appendChild(grid);

    wrap.appendChild(h('div', { cls: 'note' }, [
      h('p', { text: 'Test má ' + CFG.TEST.questions + ' otázok a ' + CFG.TEST.maxPoints + ' bodov. Na úspešné absolvovanie treba ' + CFG.TEST.passPoints + ' bodov a čas ' + (CFG.TEST.timeLimitSec / 60) + ' minút.' }),
      h('p', { cls: 'note__small', text: 'Aplikácia slúži na precvičovanie – nejde o oficiálne testy Policajného zboru.' })
    ]));

    return wrap;
  }

  function screenTests() {
    var g = CFG.group(state.group);
    var wrap = h('div', { cls: 'screen' });
    var st = STORE.groupStats(g.id, CFG.TEST.testsPerGroup, CFG.TEST.maxPoints);

    wrap.appendChild(h('div', { cls: 'summary' }, [
      h('div', { cls: 'summary__item' }, [
        h('div', { cls: 'summary__value', text: st.passed + '/' + CFG.TEST.testsPerGroup }),
        h('div', { cls: 'summary__label', text: 'úspešné testy' })
      ]),
      h('div', { cls: 'summary__item' }, [
        h('div', { cls: 'summary__value', text: st.avgPct + ' %' }),
        h('div', { cls: 'summary__label', text: 'priemer najlepších' })
      ]),
      h('div', { cls: 'summary__item' }, [
        h('div', { cls: 'summary__value', text: String(st.attempts) }),
        h('div', { cls: 'summary__label', text: 'pokusov' })
      ])
    ]));

    wrap.appendChild(h('h2', { cls: 'section-title', text: 'Testy' }));

    var list = h('div', { cls: 'list' });
    for (var i = 1; i <= CFG.TEST.testsPerGroup; i++) {
      list.appendChild(testRow(i));
    }
    wrap.appendChild(list);

    wrap.appendChild(h('button', {
      cls: 'btn btn--ghost btn--block',
      text: '🎲 Náhodný test',
      attrs: { type: 'button' },
      on: { click: function () { startTest(state.group, 0); } }
    }));

    wrap.appendChild(h('div', { cls: 'row-actions' }, [
      h('button', {
        cls: 'btn btn--link', text: 'Vymazať výsledky skupiny', attrs: { type: 'button' },
        on: { click: function () {
          showSheet('Vymazať výsledky?', 'Výsledky testov skupiny ' + g.id + ' sa natrvalo odstránia.', [
            { label: 'Vymazať', kind: 'btn--danger', onClick: function () {
              STORE.resetGroup(g.id, CFG.TEST.testsPerGroup);
              render();
            } },
            { label: 'Zrušiť' }
          ]);
        } }
      })
    ]));

    return wrap;
  }

  function testRow(no) {
    var r = STORE.result(state.group, no);
    var pct = r ? r.bestPct : null;
    var statusCls = !r ? 'is-new' : (r.passed ? 'is-pass' : 'is-fail');
    var statusText = !r ? 'Neabsolvovaný' : (r.passed ? 'Úspešný' : 'Neúspešný');

    return h('button', {
      cls: 'row ' + statusCls,
      attrs: { type: 'button' },
      on: { click: function () { startTest(state.group, no); } }
    }, [
      h('span', { cls: 'row__no', text: String(no) }),
      h('span', { cls: 'row__body' }, [
        h('span', { cls: 'row__title', text: 'Test č. ' + no }),
        h('span', { cls: 'row__meta', text: r
          ? statusText + ' · najlepšie ' + r.best + '/' + CFG.TEST.maxPoints + ' b (' + pct + ' %) · pokusov: ' + r.attempts
          : statusText })
      ]),
      h('span', { cls: 'row__badge', text: r ? (r.passed ? '✓' : pct + '%') : '›' })
    ]);
  }

  function screenTest() {
    var run = state.run;
    var q = run.questions[run.current];
    var cat = CFG.category(q.cat);
    var wrap = h('div', { cls: 'screen screen--test' });

    var answeredCount = run.answers.filter(function (a) { return a !== null; }).length;
    wrap.appendChild(h('div', { cls: 'progress' }, [
      h('div', { cls: 'progress__bar', attrs: { style: 'width:' + Math.round((answeredCount / run.questions.length) * 100) + '%' } })
    ]));

    wrap.appendChild(h('div', { cls: 'qmeta' }, [
      h('span', { cls: 'chip', text: 'Otázka ' + (run.current + 1) + '/' + run.questions.length }),
      h('span', { cls: 'chip chip--cat', text: cat.short }),
      h('span', { cls: 'chip chip--pts', text: cat.points + ' ' + (cat.points === 1 ? 'bod' : 'body') })
    ]));

    wrap.appendChild(h('p', { cls: 'question', text: q.q }));

    var opts = h('div', { cls: 'answers' });
    var instant = STORE.settings().instantFeedback;
    run.orders[run.current].forEach(function (origIdx, pos) {
      var selected = run.answers[run.current] === origIdx;
      var cls = 'answer';
      if (selected) cls += ' is-selected';
      if (instant && run.answers[run.current] !== null) {
        if (origIdx === q.c) cls += ' is-correct';
        else if (selected) cls += ' is-wrong';
      }
      opts.appendChild(h('button', {
        cls: cls, attrs: { type: 'button' },
        on: { click: function () { selectAnswer(origIdx); } }
      }, [
        h('span', { cls: 'answer__key', text: String.fromCharCode(97 + pos) }),
        h('span', { cls: 'answer__text', text: q.a[origIdx] })
      ]));
    });
    wrap.appendChild(opts);

    if (instant && run.answers[run.current] !== null) {
      wrap.appendChild(h('p', { cls: 'explain', text: q.e }));
    }

    var nav = h('div', { cls: 'navgrid' });
    run.questions.forEach(function (_, i) {
      var cls = 'navgrid__item';
      if (run.answers[i] !== null) cls += ' is-done';
      if (i === run.current) cls += ' is-current';
      nav.appendChild(h('button', {
        cls: cls, text: String(i + 1), attrs: { type: 'button' },
        on: { click: function () { run.current = i; render(); } }
      }));
    });
    wrap.appendChild(h('div', { cls: 'navgrid-wrap' }, [nav]));

    wrap.appendChild(h('div', { cls: 'actionbar' }, [
      h('button', {
        cls: 'btn btn--ghost', text: '‹ Späť', attrs: { type: 'button', disabled: run.current === 0 ? 'disabled' : null },
        on: { click: function () { if (run.current > 0) { run.current--; render(); } } }
      }),
      run.current < run.questions.length - 1
        ? h('button', {
            cls: 'btn btn--primary btn--grow', text: 'Ďalšia ›', attrs: { type: 'button' },
            on: { click: function () { run.current++; render(); } }
          })
        : h('button', {
            cls: 'btn btn--primary btn--grow', text: 'Vyhodnotiť test', attrs: { type: 'button' },
            on: { click: function () { finishTest(false); } }
          })
    ]));

    return wrap;
  }

  function selectAnswer(origIdx) {
    var run = state.run;
    var idx = run.current;
    run.answers[idx] = origIdx;
    var instant = STORE.settings().instantFeedback;
    render();
    if (!instant && idx < run.questions.length - 1) {
      // pri vypnutej spätnej väzbe sa automaticky posunieme na ďalšiu otázku;
      // posun preskočíme, ak medzitým používateľ prešiel na inú otázku
      setTimeout(function () {
        if (state.screen === 'test' && state.run === run && run.current === idx) {
          run.current = idx + 1;
          render();
        }
      }, 180);
    }
  }

  function screenResult() {
    var run = state.run;
    var s = run.score;
    var wrap = h('div', { cls: 'screen' });

    var pct = Math.round((s.points / CFG.TEST.maxPoints) * 100);
    wrap.appendChild(h('div', { cls: 'result ' + (s.passed ? 'is-pass' : 'is-fail') }, [
      h('div', { cls: 'result__ring', attrs: { style: '--pct:' + pct } }, [
        h('div', { cls: 'result__ringInner' }, [
          h('div', { cls: 'result__points', text: s.points }),
          h('div', { cls: 'result__max', text: 'z ' + CFG.TEST.maxPoints + ' b' })
        ])
      ]),
      h('div', { cls: 'result__verdict', text: s.passed ? 'Test si zvládol' : 'Test nie je splnený' }),
      h('div', { cls: 'result__detail', text: 'Správne ' + s.correct + ' z ' + s.total + ' otázok · ' + pct + ' % · potrebných ' + CFG.TEST.passPoints + ' b' }),
      h('div', { cls: 'result__detail', text: 'Čas: ' + fmtTime(s.timeUsed) })
    ]));

    wrap.appendChild(h('h2', { cls: 'section-title', text: 'Podľa okruhov' }));
    var table = h('div', { cls: 'cats' });
    CFG.CATEGORIES.forEach(function (c) {
      var rec = s.byCat[c.id];
      var w = rec.max ? Math.round((rec.earned / rec.max) * 100) : 0;
      table.appendChild(h('div', { cls: 'cats__row' }, [
        h('div', { cls: 'cats__name', text: c.name }),
        h('div', { cls: 'cats__bar' }, [h('div', { cls: 'cats__fill', attrs: { style: 'width:' + w + '%' } })]),
        h('div', { cls: 'cats__val', text: rec.earned + '/' + rec.max + ' b' })
      ]));
    });
    wrap.appendChild(table);

    wrap.appendChild(h('div', { cls: 'stack' }, [
      h('button', {
        cls: 'btn btn--primary btn--block', text: 'Prezrieť odpovede', attrs: { type: 'button' },
        on: { click: function () { state.reviewOnlyWrong = false; state.screen = 'review'; render(); } }
      }),
      s.correct < s.total ? h('button', {
        cls: 'btn btn--ghost btn--block', text: 'Zobraziť len chyby', attrs: { type: 'button' },
        on: { click: function () { state.reviewOnlyWrong = true; state.screen = 'review'; render(); } }
      }) : null,
      h('button', {
        cls: 'btn btn--ghost btn--block', text: 'Skúsiť znova', attrs: { type: 'button' },
        on: { click: function () { startTest(run.groupId, run.testNo); } }
      }),
      h('button', {
        cls: 'btn btn--link btn--block', text: 'Späť na zoznam testov', attrs: { type: 'button' },
        on: { click: function () { state.screen = 'tests'; render(); } }
      })
    ]));

    return wrap;
  }

  function screenReview() {
    var run = state.run;
    var wrap = h('div', { cls: 'screen' });

    var shown = 0;
    run.questions.forEach(function (q, i) {
      var given = run.answers[i];
      var ok = given === q.c;
      if (state.reviewOnlyWrong && ok) return;
      shown++;

      var card = h('div', { cls: 'review ' + (ok ? 'is-ok' : 'is-bad') }, [
        h('div', { cls: 'review__head' }, [
          h('span', { cls: 'review__no', text: (i + 1) + '.' }),
          h('span', { cls: 'review__cat', text: CFG.category(q.cat).short }),
          h('span', { cls: 'review__mark', text: ok ? '✓' : '✗' })
        ]),
        h('p', { cls: 'review__q', text: q.q })
      ]);

      q.a.forEach(function (text, idx) {
        var cls = 'review__a';
        if (idx === q.c) cls += ' is-correct';
        if (idx === given && idx !== q.c) cls += ' is-wrong';
        var prefix = idx === q.c ? '✓ ' : (idx === given ? '✗ ' : '· ');
        card.appendChild(h('div', { cls: cls, text: prefix + text }));
      });

      if (given === null) card.appendChild(h('div', { cls: 'review__note', text: 'Bez odpovede' }));
      card.appendChild(h('p', { cls: 'review__e', text: q.e }));
      wrap.appendChild(card);
    });

    if (!shown) wrap.appendChild(h('p', { cls: 'note', text: 'Žiadne chyby – všetky odpovede sú správne.' }));

    wrap.appendChild(h('button', {
      cls: 'btn btn--ghost btn--block', text: 'Späť na výsledok', attrs: { type: 'button' },
      on: { click: function () { state.screen = 'result'; render(); } }
    }));
    return wrap;
  }

  function screenSettings() {
    var wrap = h('div', { cls: 'screen' });
    var s = STORE.settings();

    function toggle(name, label, desc) {
      var input = h('input', { attrs: { type: 'checkbox', id: 'set-' + name } });
      input.checked = s[name];
      input.addEventListener('change', function () {
        STORE.setSetting(name, input.checked);
      });
      return h('label', { cls: 'switch', attrs: { for: 'set-' + name } }, [
        h('span', { cls: 'switch__body' }, [
          h('span', { cls: 'switch__label', text: label }),
          h('span', { cls: 'switch__desc', text: desc })
        ]),
        input,
        h('span', { cls: 'switch__ui' })
      ]);
    }

    wrap.appendChild(h('h2', { cls: 'section-title', text: 'Nastavenia' }));
    wrap.appendChild(h('div', { cls: 'stack' }, [
      toggle('shuffleAnswers', 'Miešať odpovede', 'Poradie odpovedí sa v každom teste premieša.'),
      toggle('timer', 'Časový limit', 'Test má limit ' + (CFG.TEST.timeLimitSec / 60) + ' minút.'),
      toggle('instantFeedback', 'Okamžitá kontrola', 'Po odpovedi sa hneď zobrazí správne riešenie a vysvetlenie.')
    ]));

    wrap.appendChild(h('h2', { cls: 'section-title', text: 'O aplikácii' }));
    wrap.appendChild(h('div', { cls: 'note' }, [
      h('p', { text: 'Banka obsahuje ' + BANK.all().length + ' otázok rozdelených do ' + CFG.CATEGORIES.length + ' okruhov.' }),
      h('p', { text: 'Každá skupina má ' + CFG.TEST.testsPerGroup + ' testov po ' + CFG.TEST.questions + ' otázok.' }),
      h('p', { cls: 'note__small', text: 'Otázky sú učebnou pomôckou, nie oficiálnym testom. Platné znenie pravidiel nájdeš v zákone č. 8/2009 Z. z.' })
    ]));

    wrap.appendChild(h('button', {
      cls: 'btn btn--link btn--block', text: 'Vymazať všetky výsledky', attrs: { type: 'button' },
      on: { click: function () {
        showSheet('Vymazať všetko?', 'Odstránia sa výsledky všetkých skupín aj nastavenia.', [
          { label: 'Vymazať', kind: 'btn--danger', onClick: function () {
            STORE.resetAll();
            state.group = null;
            state.screen = 'home';
            render();
          } },
          { label: 'Zrušiť' }
        ]);
      } }
    }));

    return wrap;
  }

  /* ------------------------------------------------------------------ */
  /* vykreslenie a navigácia                                             */
  /* ------------------------------------------------------------------ */

  function render() {
    var g = state.group ? CFG.group(state.group) : null;
    var titles = {
      home: 'Autoškola testy',
      tests: g ? g.name : 'Testy',
      test: state.run ? (state.run.testNo === 0 ? 'Náhodný test' : 'Test č. ' + state.run.testNo) : 'Test',
      result: 'Výsledok',
      review: state.reviewOnlyWrong ? 'Chybné odpovede' : 'Prehľad odpovedí',
      settings: 'Nastavenia'
    };
    topbarTitle.textContent = titles[state.screen] || 'Autoškola';
    btnBack.hidden = state.screen === 'home';

    topbarSlot.innerHTML = '';
    if (state.screen === 'test' && STORE.settings().timer) {
      topbarSlot.appendChild(h('span', {
        cls: 'timer' + (state.run.remaining <= 120 ? ' is-low' : ''),
        attrs: { id: 'timer' },
        text: fmtTime(state.run.remaining)
      }));
    } else if (state.screen === 'home') {
      topbarSlot.appendChild(h('button', {
        cls: 'iconbtn', text: '⚙', attrs: { type: 'button', 'aria-label': 'Nastavenia' },
        on: { click: function () { state.screen = 'settings'; render(); } }
      }));
    }

    var view;
    switch (state.screen) {
      case 'tests': view = screenTests(); break;
      case 'test': view = screenTest(); break;
      case 'result': view = screenResult(); break;
      case 'review': view = screenReview(); break;
      case 'settings': view = screenSettings(); break;
      default: view = screenHome();
    }
    app.innerHTML = '';
    app.appendChild(view);
    if (state.screen !== 'test' && state.screen !== 'review') window.scrollTo(0, 0);
  }

  function goBack() {
    switch (state.screen) {
      case 'test': leaveTest(); break;
      case 'review': state.screen = 'result'; render(); break;
      case 'result': state.screen = 'tests'; render(); break;
      case 'tests':
      case 'settings':
      default:
        state.screen = 'home';
        render();
    }
  }

  btnBack.addEventListener('click', goBack);

  /* servisný pracovník pre offline režim (funguje pri hostovaní cez http/https) */
  if ('serviceWorker' in navigator && location.protocol.indexOf('http') === 0) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () { /* offline režim nie je dostupný */ });
    });
  }

  render();
})();

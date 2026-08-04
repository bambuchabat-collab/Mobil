#!/usr/bin/env node
/**
 * Kontrola banky otázok a zloženia testov.
 *
 * Spustenie:  node tools/validate.js
 * Skript overí, že každá otázka má správny formát, že v každej skupine je dosť
 * otázok pre všetky okruhy a že každý z testov má predpísaný počet otázok a bodov.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');

/* Skripty načítavame v presne takom poradí, v akom ich uvádza index.html –
   inak by kontrola prehliadla chybné poradie <script> značiek.
   app.js sa vynecháva, potrebuje DOM. */
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const FILES = (html.match(/<script src="([^"]+)"><\/script>/g) || [])
  .map(tag => tag.replace(/^<script src="|"><\/script>$/g, ''))
  .filter(src => src !== 'assets/js/app.js');

const errors = [];
const warnings = [];
function err(msg) { errors.push(msg); }
function warn(msg) { warnings.push(msg); }

/* Prostredie prehliadača nahradíme jednoduchým kontextom. */
const sandbox = {};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

sandbox.localStorage = {
  getItem: () => null, setItem: () => {}, removeItem: () => {}
};

for (const f of FILES) {
  try {
    vm.runInContext(fs.readFileSync(path.join(ROOT, f), 'utf8'), sandbox, { filename: f });
  } catch (e) {
    console.error(`✗ skript ${f} zlyhal pri načítaní: ${e.message}`);
    console.error('  skontroluj poradie <script> značiek v index.html');
    process.exit(1);
  }
}

const CFG = sandbox.CFG;
const BANK = sandbox.BANK;
if (!CFG || !BANK) {
  console.error('✗ index.html nenačítal config.js alebo bank.js');
  process.exit(1);
}
const questions = BANK.all();
const groupIds = CFG.GROUPS.map(g => g.id);

/* ---------- 1. formát otázok ---------- */

const seen = new Set();
for (const q of questions) {
  const at = `otázka ${q.id}`;
  if (!q.id || typeof q.id !== 'string') err(`chýba alebo je neplatné ID: ${JSON.stringify(q).slice(0, 80)}`);
  if (seen.has(q.id)) err(`duplicitné ID: ${q.id}`);
  seen.add(q.id);

  if (!CFG.category(q.cat)) err(`${at}: neznámy okruh ${q.cat}`);
  if (!Array.isArray(q.groups) || q.groups.length === 0) err(`${at}: chýba zoznam skupín`);
  else {
    for (const g of q.groups) {
      if (g !== '*' && groupIds.indexOf(g) === -1) err(`${at}: neznáma skupina "${g}"`);
    }
  }
  if (typeof q.q !== 'string' || q.q.trim().length < 10) err(`${at}: chýba text otázky`);
  if (!Array.isArray(q.a) || q.a.length < 2) err(`${at}: musí mať aspoň dve odpovede`);
  else {
    const texts = new Set();
    q.a.forEach((t, i) => {
      if (typeof t !== 'string' || !t.trim()) err(`${at}: prázdna odpoveď č. ${i + 1}`);
      if (texts.has(t)) err(`${at}: dve rovnaké odpovede ("${t}")`);
      texts.add(t);
    });
    if (!Number.isInteger(q.c) || q.c < 0 || q.c >= q.a.length) err(`${at}: neplatný index správnej odpovede`);
  }
  if (typeof q.e !== 'string' || q.e.trim().length < 10) warn(`${at}: chýba alebo je veľmi krátke vysvetlenie`);
}

/* ---------- 2. dosť otázok pre každú skupinu a okruh ---------- */

for (const g of CFG.GROUPS) {
  for (const c of CFG.CATEGORIES) {
    const pool = BANK.forGroup(g.id, c.id).length;
    if (pool < c.count) {
      err(`skupina ${g.id}, okruh ${c.id}: v banke je ${pool} otázok, test ich potrebuje ${c.count}`);
    } else if (pool < c.count * 2) {
      warn(`skupina ${g.id}, okruh ${c.id}: len ${pool} otázok pre ${CFG.TEST.testsPerGroup} testov`);
    }
  }
}

/* ---------- 3. zloženie testu ---------- */

const catSum = CFG.CATEGORIES.reduce((s, c) => s + c.count, 0);
const pointSum = CFG.CATEGORIES.reduce((s, c) => s + c.count * c.points, 0);
if (catSum !== CFG.TEST.questions) err(`súčet otázok v okruhoch je ${catSum}, očakáva sa ${CFG.TEST.questions}`);
if (pointSum !== CFG.TEST.maxPoints) err(`súčet bodov v okruhoch je ${pointSum}, očakáva sa ${CFG.TEST.maxPoints}`);

let reuseWorst = 0;
for (const g of CFG.GROUPS) {
  const usage = new Map();
  for (let no = 1; no <= CFG.TEST.testsPerGroup; no++) {
    const test = BANK.buildTest(g.id, no);
    const label = `skupina ${g.id}, test ${no}`;

    if (test.length !== CFG.TEST.questions) err(`${label}: má ${test.length} otázok namiesto ${CFG.TEST.questions}`);

    const ids = new Set();
    const perCat = {};
    let points = 0;
    for (const q of test) {
      if (ids.has(q.id)) err(`${label}: otázka ${q.id} je v teste dvakrát`);
      ids.add(q.id);
      perCat[q.cat] = (perCat[q.cat] || 0) + 1;
      points += CFG.category(q.cat).points;
      if (q.groups.indexOf('*') === -1 && q.groups.indexOf(g.id) === -1) {
        err(`${label}: otázka ${q.id} nepatrí do tejto skupiny`);
      }
      usage.set(q.id, (usage.get(q.id) || 0) + 1);
    }
    for (const c of CFG.CATEGORIES) {
      if ((perCat[c.id] || 0) !== c.count) {
        err(`${label}: okruh ${c.id} má ${perCat[c.id] || 0} otázok namiesto ${c.count}`);
      }
    }
    if (points !== CFG.TEST.maxPoints) err(`${label}: má ${points} bodov namiesto ${CFG.TEST.maxPoints}`);

    /* determinizmus – rovnaký test musí mať vždy rovnaké otázky */
    const again = BANK.buildTest(g.id, no).map(q => q.id).join(',');
    if (again !== test.map(q => q.id).join(',')) err(`${label}: zostavenie testu nie je deterministické`);
  }
  const worst = Math.max(...usage.values());
  reuseWorst = Math.max(reuseWorst, worst);
}

/* ---------- výpis ---------- */

const perCatCount = CFG.CATEGORIES
  .map(c => `${c.id}: ${questions.filter(q => q.cat === c.id).length}`)
  .join(', ');

console.log(`Otázok v banke: ${questions.length}  (${perCatCount})`);
console.log(`Skupín: ${CFG.GROUPS.length} × ${CFG.TEST.testsPerGroup} testov po ${CFG.TEST.questions} otázok / ${CFG.TEST.maxPoints} bodov`);
console.log(`Najviac opakovaní jednej otázky v rámci testov skupiny: ${reuseWorst}×`);

if (warnings.length) {
  console.log(`\nUpozornenia (${warnings.length}):`);
  warnings.forEach(w => console.log('  ! ' + w));
}
if (errors.length) {
  console.error(`\nChyby (${errors.length}):`);
  errors.forEach(e => console.error('  ✗ ' + e));
  process.exit(1);
}
console.log('\n✓ Banka otázok aj zloženie testov sú v poriadku.');

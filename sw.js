/* Offline režim – funguje pri hostovaní cez http(s), napr. na GitHub Pages. */
var CACHE = 'autoskola-testy-v1';
var ASSETS = [
  './',
  'index.html',
  'manifest.webmanifest',
  'assets/css/app.css',
  'assets/js/config.js',
  'assets/js/bank.js',
  'assets/js/storage.js',
  'assets/js/app.js',
  'assets/js/data/questions-01-pravidla.js',
  'assets/js/data/questions-02-znacky.js',
  'assets/js/data/questions-03-krizovatky.js',
  'assets/js/data/questions-04-predpisy.js',
  'assets/js/data/questions-05-teoria.js',
  'assets/js/data/questions-06-konstrukcia.js',
  'assets/js/data/questions-07-bezpecnost.js',
  'assets/js/data/questions-90-skupiny.js',
  'assets/icons/icon.svg',
  'assets/icons/icon-180.png',
  'assets/icons/icon-512.png'
];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(ASSETS); }).then(function () {
    return self.skipWaiting();
  }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.map(function (k) { return k === CACHE ? null : caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(function (hit) {
      return hit || fetch(e.request).then(function (res) {
        var copy = res.clone();
        caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
        return res;
      }).catch(function () { return caches.match('index.html'); });
    })
  );
});

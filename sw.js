// Меняй VERSION при каждом деплое — этого достаточно, чтобы установленное
// приложение подхватило обновление: браузер видит изменившийся байт-в-байт sw.js,
// ставит новую версию в ожидание, страница показывает кнопку «Обновить».
const VERSION = "2026-08-29.3";
const CACHE = "rt-kodeks-" + VERSION;
const ASSETS = ["./", "./index.html", "./data.json", "./manifest.webmanifest",
                "./icon.svg", "./icon-192.png", "./icon-512.png", "./icon-180.png"];
const FRESH = /\/(index\.html|data\.json)$|\/$/;   // network-first: оболочка + данные

self.addEventListener("install", e => {
  // без skipWaiting: новая версия ждёт, пока страница не разрешит переключиться
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    if (self.registration.navigationPreload) await self.registration.navigationPreload.enable();
    const ks = await caches.keys();
    await Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("message", e => {
  if (e.data === "skip-waiting") self.skipWaiting();
  if (e.data === "version") e.source && e.source.postMessage({ version: VERSION });
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;

  const put = res => {
    if (res && res.ok) { const cp = res.clone(); caches.open(CACHE).then(c => c.put(req, cp)); }
    return res;
  };
  if (FRESH.test(new URL(req.url).pathname) || req.mode === "navigate") {
    e.respondWith(fetch(req).then(put).catch(() =>
      caches.match(req).then(r => r || caches.match("./index.html"))));
  } else {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(put)));
  }
});

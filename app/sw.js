/* Caches the app, library, and every lesson's audio, video, and images so
 * it keeps working with no connection after the first visit. */
const CACHE = "know-my-body-v6";
const FILES = ["./", "index.html", "style.css", "engine.js", "app.js", "library.json", "manifest.webmanifest",
  "brand/vulvai_logo_white.png", "brand/vulvai_mark_white.png"];

async function precache() {
  const cache = await caches.open(CACHE);
  await cache.addAll(FILES);
  const bundle = await (await fetch("library.json")).json();
  const media = bundle.modules.flatMap(m => m.lessons.flatMap(l => [l.audio, l.video, l.image].filter(Boolean)));
  await cache.addAll([...new Set(media)]);
}

self.addEventListener("install", e => e.waitUntil(precache()));
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))));
self.addEventListener("fetch", e => e.respondWith(
  caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request).then(r => {
    if (r.ok && r.status === 200) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return r;
  }))));

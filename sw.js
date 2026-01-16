// Simple Service Worker: cache all app shell
const CACHE='corolla-v1';
const FILES=[
  '/corolla/index.html','/corolla/chatbot.html','/corolla/roadmap.html',
  '/corolla/test1.html','/corolla/test2.html','/corolla/test3.html','/corolla/test4.html',
  '/corolla/playground.html','/corolla/results.html','/corolla/manifest.json'
];

self.addEventListener('install', evt=>{
  evt.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)));
  self.skipWaiting();
});

self.addEventListener('activate', evt=>{
  evt.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', evt=>{
  evt.respondWith(caches.match(evt.request).then(resp=>resp || fetch(evt.request).then(r=>{
    const copy = r.clone();
    caches.open(CACHE).then(c=>c.put(evt.request, copy));
    return r;
  }).catch(()=>caches.match('/corolla/index.html'))));
});
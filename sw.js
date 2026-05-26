const CACHE_NAME = 'escolinha-jacare-v2';
const urlsToCache = [
  '/escolinha-jacare/splash.html',
  '/escolinha-jacare/index.html',
  '/escolinha-jacare/diretoria.html',
  '/escolinha-jacare/funcionarios.html',
  '/escolinha-jacare/prematricula.html',
  '/escolinha-jacare/galerias.html',
  '/escolinha-jacare/club.html',
  '/escolinha-jacare/uniforme.html',
  '/escolinha-jacare/comentarios.html',
  '/escolinha-jacare/aniversario.html',
  '/escolinha-jacare/manifest.json'
];
 
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});
 
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});
 
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
 

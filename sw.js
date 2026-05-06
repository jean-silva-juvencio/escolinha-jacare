const CACHE_NAME = 'escolinha-jacare-v1';
const urlsToCache = [
  '/frontend/index.html',
  '/frontend/diretoria.html',
  '/frontend/funcionarios.html',
  '/frontend/prematricula.html',
  '/frontend/galerias.html',
  '/frontend/club.html',
  '/frontend/uniforme.html',
  '/frontend/comentarios.html',
  '/frontend/aniversario.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

const CACHE_NAME = 'escolinha-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/diretoria.html',
  '/funcionarios.html',
  '/club.html',
  '/uniforme.html',
  '/aniversario.html',
  '/comentarios.html',
  '/galerias.html',
  '/prematricula.html',
  '/manifest.json',
  '/icons/jacare.jpeg'
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

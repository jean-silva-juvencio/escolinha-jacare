const CACHE_NAME = 'escolinha-jacare-v3';

self.addEventListener('install', event => {
  console.log('Service Worker instalado');
  self.skipWaiting();
});

self.addEventListener('fetch', event => {
  // Só processa requisições HTTP/HTTPS (ignora chrome-extension, etc)
  if (!event.request.url.startsWith('http')) {
    return;
  }
  
  event.respondWith(fetch(event.request));
});

self.addEventListener('activate', event => {
  console.log('Service Worker ativado');
  self.clients.claim();
});

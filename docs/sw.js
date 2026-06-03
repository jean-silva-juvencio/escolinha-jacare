const CACHE_NAME = 'escolinha-jacare-v1';
const urlsToCache = [
  '/docs/',
  '/docs/index.html',
  '/docs/manifest.json',
  '/docs/sw.js',
  '/docs/icones/icon-192.png',
  '/docs/icones/icon-512.png',
  '/docs/icones/facebook.png',
  '/docs/icones/gmail.png',
  '/docs/icones/instagram.png',
  '/docs/icones/maps.png',
  '/docs/icones/whatsapp.png'
];

// Instala o Service Worker e cacheia os arquivos
self.addEventListener('install', event => {
  console.log('Service Worker instalado com sucesso!');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
      .catch(err => console.log('Erro no cache:', err))
  );
  self.skipWaiting();
});

// Intercepta requisições e serve do cache quando possível
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - retorna do cache
        if (response) {
          return response;
        }
        // Clone da requisição
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest).then(response => {
          // Verifica se é uma resposta válida
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone da resposta
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
          
          return response;
        });
      })
  );
});

// Ativa e limpa caches antigos
self.addEventListener('activate', event => {
  console.log('Service Worker ativado');
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

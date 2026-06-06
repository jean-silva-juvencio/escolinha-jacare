importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "AIzaSyBUPquSeneayoS-eiCgJB0K47eLM44eqIs",
    authDomain: "alvorada-4d410.firebaseapp.com",
    projectId: "alvorada-4d410",
    storageBucket: "alvorada-4d410.firebasestorage.app",
    messagingSenderId: "12705241722",
    appId: "1:12705241722:web:f95f70821505043e1f39c3"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
    console.log('Notificação em background:', payload);
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: '/escolinha-jacare/icones/icon-192.png',
        badge: '/escolinha-jacare/icones/icon-192.png',
        data: payload.data
    };
    self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('https://jean-silva-juvencio.github.io/escolinha-jacare/diretoria.html')
    );
});

// Cache básico para PWA
const CACHE_NAME = 'escolinha-v3';
const urlsToCache = [
    '/escolinha-jacare/',
    '/escolinha-jacare/index.html'
];

self.addEventListener('install', event => {
    event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache)));
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))));
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    event.respondWith(caches.match(event.request).then(response => response || fetch(event.request)));
});

// Increment CACHE_VERSION for each release so a new shell is installed atomically.
const CACHE_PREFIX = 'tcg-tableforge-shell-';
const CACHE_VERSION = '__BUILD_CACHE_VERSION__';
const CACHE_NAME = `${CACHE_PREFIX}${CACHE_VERSION}`;
const APP_ROOT = self.registration.scope;
const SHELL = ['./', './index.html', './app.js', './data.js', './manifest.webmanifest', './icon.svg', './icon-192.png', './icon-512.png', './apple-touch-icon.png']
  .map(path => new URL(path, APP_ROOT).href);

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL)));
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names
      .filter(name => name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME)
      .map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  const scopePath = new URL(APP_ROOT).pathname;
  if (!url.pathname.startsWith(scopePath)) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request);
    if (cached) return cached;

    try {
      const response = await fetch(request);
      if (response.ok && response.status === 200) {
        await cache.put(request, response.clone());
      }
      return response;
    } catch (error) {
      if (request.mode === 'navigate') {
        const appShell = await cache.match(new URL('./index.html', APP_ROOT).href);
        return appShell || Response.error();
      }
      return Response.error();
    }
  })());
});

self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});

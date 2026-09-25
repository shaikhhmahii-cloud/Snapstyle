/**
 * SnapStyle Service Worker
 * Network-First strategy ensures mobile WebView and browsers always load fresh UI updates,
 * with graceful offline caching fallback.
 */

const CACHE_NAME = "snapstyle-cache-v5";
const STATIC_ASSETS = [
  "/app",
  "/static/index.html",
  "/static/css/style.css",
  "/static/js/app.js",
  "/static/js/api.js",
  "/static/js/state.js",
  "/static/manifest.json",
  "/static/assets/icon-192.png",
  "/static/assets/icon-512.png"
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[SnapStyle SW] Pre-caching static app shell");
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn("[SnapStyle SW] Partial asset cache note:", err);
      });
    })
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log("[SnapStyle SW] Removing stale cache:", key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  // Only handle GET requests; AI and upload endpoints bypass cache
  if (
    event.request.method !== "GET" ||
    event.request.url.includes("/analyze") ||
    event.request.url.includes("/search-products") ||
    event.request.url.includes("/upload") ||
    event.request.url.includes("/health")
  ) {
    return;
  }

  // Network-First strategy: always fetch fresh from network
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // Fallback to cache if network is unavailable
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          if (event.request.mode === "navigate") {
            return caches.match("/static/index.html") || caches.match("/app");
          }
        });
      })
  );
});

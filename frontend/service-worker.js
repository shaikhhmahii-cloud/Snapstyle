/**
 * SnapStyle Service Worker
 * Enables offline caching, fast background asset loading, and mobile installability.
 */

const CACHE_NAME = "snapstyle-cache-v1";
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
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[SnapStyle SW] Pre-caching static app shell");
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn("[SnapStyle SW] Partial asset cache note:", err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log("[SnapStyle SW] Removing old cache:", key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  // Only cache GET requests; dynamic API calls (/analyze, /search-products) bypass cache for real AI results
  if (event.request.method !== "GET" || event.request.url.includes("/analyze") || event.request.url.includes("/search-products")) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((response) => {
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return response;
      }).catch(() => {
        // Fallback for document navigation
        if (event.request.mode === "navigate") {
          return caches.match("/static/index.html");
        }
      });
    })
  );
});

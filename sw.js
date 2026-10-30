const CACHE = "toefl-v8";
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(["./", "./index.html", "./manifest.json", "./icon.svg"])).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  /* 文章每天更新：网络优先，断网才用缓存（离线也能读） */
  if (url.pathname.endsWith("articles.json")) {
    e.respondWith(
      fetch(e.request).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(url.pathname, copy));
        return res;
      }).catch(() => caches.match(url.pathname))
    );
    return;
  }
  /* 其他文件（页面/词库）：缓存优先，改版本号才更新 */
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(r =>
      r || fetch(e.request).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return res;
      }).catch(() => caches.match("./index.html"))
    )
  );
});

/* Weaver API bridge for the static GitHub Pages frontend. */
(function () {
  'use strict';

  const defaultBackend = 'https://ai-dream-weaver.onrender.com';
  const configured = window.WEAVER_BACKEND_URL || document.documentElement.dataset.backendUrl || defaultBackend;
  const backend = String(configured).replace(/\/+$/, '');
  const nativeFetch = window.fetch.bind(window);

  function getSessionToken() {
    try {
      return localStorage.getItem('session_token') || '';
    } catch (_) {
      return '';
    }
  }

  function isApiPath(url) {
    return typeof url === 'string' && (url.startsWith('/api/') || url === '/api');
  }

  function buildRequest(resource, init) {
    const original = resource instanceof Request ? resource : null;
    const originalUrl = original ? original.url : String(resource);
    const relativeUrl = originalUrl.startsWith(location.origin)
      ? originalUrl.slice(location.origin.length)
      : originalUrl;
    const targetUrl = isApiPath(relativeUrl) ? `${backend}${relativeUrl}` : originalUrl;
    const options = Object.assign({}, init || {});

    if (original) {
      options.method = options.method || original.method;
      options.headers = new Headers(original.headers);
      if (!options.body && !['GET', 'HEAD'].includes(original.method)) {
        options.body = original.clone().body;
      }
    } else {
      options.headers = new Headers(options.headers || {});
    }

    const token = getSessionToken();
    if (token) options.headers.set('Authorization', `Bearer ${token}`);
    options.headers.set('Accept', 'application/json');
    options.credentials = 'include';
    return { targetUrl, options };
  }

  window.WeaverAPI = {
    baseUrl: backend,
    token: getSessionToken,
    url: function (path) {
      return isApiPath(path) ? `${backend}${path}` : path;
    }
  };

  window.fetch = function (resource, init) {
    const rawUrl = resource instanceof Request ? resource.url : String(resource);
    const relativeUrl = rawUrl.startsWith(location.origin)
      ? rawUrl.slice(location.origin.length)
      : rawUrl;
    if (!isApiPath(relativeUrl)) return nativeFetch(resource, init);

    const request = buildRequest(resource, init);
    return nativeFetch(request.targetUrl, request.options).then(function (response) {
      if (response.status === 401) {
        try {
          localStorage.removeItem('session_token');
          localStorage.removeItem('user_id');
          localStorage.removeItem('username');
        } catch (_) {}
      }
      return response;
    });
  };
})();

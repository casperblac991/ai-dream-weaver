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

/* Language switch for the static site: there is no /set-lang server route on GitHub Pages. */
(function () {
  'use strict';
  var NAV = {
    ar: { n3: '👥 المجتمع', n4: '🧪 مختبر الأحلام', n_dict: '🌌 القاموس الكوني', n_map: '🌍 خارطة الأحلام', n_test: '🧠 تحليل الشخصية', n_offers: '💎 عروض خاصة', loginBtn: '🔐 تسجيل الدخول', signupBtn: '🚀 إنشاء حساب' },
    en: { n3: '👥 Community', n4: '🧪 Dream Lab', n_dict: '🌌 Cosmic Dictionary', n_map: '🌍 Dream Map', n_test: '🧠 Personality Analysis', n_offers: '💎 Special Offers', loginBtn: '🔐 Log in', signupBtn: '🚀 Sign up' }
  };
  document.addEventListener('DOMContentLoaded', function () {
    var links = document.querySelectorAll('a[href^="/set-lang/"]');
    if (!links.length) return;
    try {
      if (typeof T !== 'undefined' && T.ar && T.en) {
        Object.assign(T.ar, NAV.ar);
        Object.assign(T.en, NAV.en);
      }
    } catch (_) {}
    links.forEach(function (a) {
      var lang = a.getAttribute('href').split('/').pop();
      if (lang !== 'ar' && lang !== 'en') { a.style.display = 'none'; return; }
      a.classList.remove('on');
      if (!document.getElementById('btn-' + lang)) a.id = 'btn-' + lang;
      a.setAttribute('href', '#');
      a.addEventListener('click', function (e) {
        e.preventDefault();
        if (typeof window.setLang === 'function') window.setLang(lang);
      });
    });
  });
})();

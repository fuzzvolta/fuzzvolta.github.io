(function () {
  // Mobile menu + About submenu
  var hdr = document.querySelector('.hdr');
  var menu = document.querySelector('[data-menu]');
  if (menu) menu.addEventListener('click', function () {
    var open = hdr.classList.toggle('open');
    menu.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  document.querySelectorAll('[data-sub]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var li = btn.parentNode, open = li.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-item.has-sub')) document.querySelectorAll('.nav-item.has-sub.open').forEach(function (li) {
      li.classList.remove('open'); li.querySelector('[data-sub]').setAttribute('aria-expanded', 'false');
    });
  });

  // YouTube: load the iframe only on click (keeps pages fast, no third-party requests until asked)
  document.querySelectorAll('.yt[data-yt]').forEach(function (fig) {
    var btn = fig.querySelector('.yt-play');
    btn.addEventListener('click', function () {
      var id = fig.getAttribute('data-yt');
      var ifr = document.createElement('iframe');
      ifr.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
      ifr.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      ifr.allowFullscreen = true;
      ifr.title = btn.getAttribute('aria-label') || 'YouTube video';
      fig.replaceChild(ifr, btn);
    });
  });

  // Loops (converted GIFs): nothing downloads until the loop is near the viewport; pause when it leaves.
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var loops = document.querySelectorAll('video.loop');
  if (reduce) { loops.forEach(function (v) { v.removeAttribute('autoplay'); v.pause(); }); }
  else if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting) { if (v.dataset.poster) { v.poster = v.dataset.poster; delete v.dataset.poster; } if (v.preload === 'none') v.preload = 'auto'; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else if (!v.paused) v.pause();
      });
    }, { rootMargin: '300px 0px' });
    loops.forEach(function (v) { io.observe(v); });
  } else { loops.forEach(function (v) { if (v.dataset.poster) v.poster = v.dataset.poster; v.setAttribute('autoplay', ''); v.preload = 'auto'; }); }

  // Players: pause others when one starts
  var players = document.querySelectorAll('.player video');
  players.forEach(function (v) {
    v.addEventListener('play', function () { players.forEach(function (o) { if (o !== v) o.pause(); }); });
  });
})();

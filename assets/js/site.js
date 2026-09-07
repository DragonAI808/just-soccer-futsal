/* ==========================================================================
   Just Soccer Futsal Center — interactions
   All motion is transform/opacity only, rAF-batched, and disabled wholesale
   under prefers-reduced-motion.
   ========================================================================== */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var clamp01 = function (n) { return n < 0 ? 0 : n > 1 ? 1 : n; };

  /* ---------------------------------------------------------------
     1. Preloader — lift once assets are in, with a hard fallback so a
        slow font or the hero photograph can never trap the page behind
        the curtain.
     --------------------------------------------------------------- */
  var MIN_SHOW = reduced ? 0 : 600;
  var start = Date.now();
  var lifted = false;

  function lift() {
    if (lifted) return;
    lifted = true;
    var wait = Math.max(0, MIN_SHOW - (Date.now() - start));
    setTimeout(function () {
      document.body.classList.add('is-loaded');
      splitHero();
      revealHero();
      onScroll();
    }, wait);
  }
  window.addEventListener('load', lift);
  // Hard stop: if load never fires, the page is never trapped behind the curtain.
  setTimeout(lift, 3500);

  /* ---------------------------------------------------------------
     2. Split the hero headline into words that rise in sequence
     --------------------------------------------------------------- */
  function splitHero() {
    var t = $('[data-split]');
    if (!t || t.dataset.done) return;
    t.dataset.done = '1';

    // Walk child NODES, not textContent. Reading textContent flattened any
    // <br> in the markup away, so the only way to influence where the headline
    // broke was to fight it with max-width and hope. Walking the nodes lets the
    // HTML say exactly where the line ends.
    var nodes = Array.prototype.slice.call(t.childNodes);
    t.textContent = '';
    var n = 0;

    nodes.forEach(function (node) {
      if (node.nodeType === 1 && node.tagName === 'BR') {
        t.appendChild(document.createElement('br'));
        return;
      }
      var words = (node.textContent || '').trim().split(/\s+/).filter(Boolean);
      words.forEach(function (w, wi) {
        var fly = document.createElement('span');
        fly.className = 'wfly';
        fly.textContent = w;
        // the photograph holds alone for a beat, then the words arrive in
        // sequence rather than as one block
        fly.style.transitionDelay = (0.35 + n * 0.11) + 's';
        n++;
        t.appendChild(fly);
        if (wi < words.length - 1) t.appendChild(document.createTextNode(' '));
      });
    });
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { t.classList.add('is-in'); });
    });
  }
  splitHero();

  /* ---------------------------------------------------------------
     2b. Section headings — wrap the text so the reveal mask has a
         child to clip.

         The mask must NOT go on the <h2>: clip-path is folded into
         IntersectionObserver's intersection rect, so a fully clipped
         heading reports ratio 0 and the observer that would reveal it
         never fires. The heading then stays hidden forever, silently.
         Clipping an injected child keeps the observed box unclipped.
     --------------------------------------------------------------- */
  function maskHeadings() {
    $$('.h2[data-reveal]').forEach(function (h) {
      if (h.dataset.masked) return;
      h.dataset.masked = '1';
      var inner = document.createElement('span');
      inner.className = 'h2__in';
      while (h.firstChild) inner.appendChild(h.firstChild);
      h.appendChild(inner);
    });
  }
  maskHeadings();

  /* ---------------------------------------------------------------
     3. Reveal on scroll
     --------------------------------------------------------------- */
  var revealIO = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      revealIO.unobserve(e.target);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });

  $$('[data-reveal]').forEach(function (el) { revealIO.observe(el); });

  // The hero is above the fold on load, so its content must not wait on a
  // scroll observer — on a phone the CTAs sit right on the observer's -8%
  // bottom edge and may never intersect enough to fire.
  function revealHero() {
    $$('#hero [data-reveal]').forEach(function (el) {
      revealIO.unobserve(el);
      el.classList.add('is-in');
    });
  }

  /* ---------------------------------------------------------------
     4. Nav — stuck state + mobile menu
     --------------------------------------------------------------- */
  var nav = $('#nav');
  var burger = $('#burger');
  var navLinks = $('#navLinks');

  function onNavScroll() {
    if (!nav) return;
    nav.classList.toggle('is-stuck', window.scrollY > window.innerHeight * 0.72);
  }
  onNavScroll();

  // --navh feeds the mobile menu's top inset. It used to be a hand-written
  // 3.35rem while the bar actually measured 66px, so the overlay started 12px
  // too high and tucked under the header. Measuring it removes the guess — and
  // the coupling, since the badge's size drives the bar's height.
  function syncNavHeight() {
    if (!nav) return;
    document.documentElement.style.setProperty('--navh', nav.offsetHeight + 'px');
  }
  syncNavHeight();
  window.addEventListener('resize', syncNavHeight, { passive: true });
  window.addEventListener('load', syncNavHeight);

  function closeMenu() {
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', 'Open menu');
    navLinks.classList.remove('is-open');
    nav.classList.remove('is-menu-open');
    document.body.style.overflow = '';
  }

  if (burger && navLinks) {
    burger.addEventListener('click', function () {
      if (burger.getAttribute('aria-expanded') === 'true') { closeMenu(); return; }
      burger.setAttribute('aria-expanded', 'true');
      burger.setAttribute('aria-label', 'Close menu');
      navLinks.classList.add('is-open');
      nav.classList.add('is-menu-open');
      document.body.style.overflow = 'hidden';
    });
    navLinks.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') closeMenu();
    });
  }

  /* ---------------------------------------------------------------
     5. Statement — words light up as the block crosses the viewport
     --------------------------------------------------------------- */
  var stmt = $('[data-words]');
  var stmtWords = [];
  if (stmt) {
    var txt = stmt.textContent.trim().split(/\s+/);
    stmt.textContent = '';
    txt.forEach(function (w, i) {
      var s = document.createElement('span');
      s.className = 'wd';
      s.textContent = w;
      stmt.appendChild(s);
      if (i < txt.length - 1) stmt.appendChild(document.createTextNode(' '));
      stmtWords.push(s);
    });
  }

  function paintWords() {
    if (!stmt || !stmtWords.length) return;
    var r = stmt.getBoundingClientRect();
    var vh = window.innerHeight;
    // 0 when the block's top hits 78% of the viewport, 1 once it clears 26%
    var p = clamp01((vh * 0.78 - r.top) / (r.height + vh * 0.52));
    var lit = Math.round(p * stmtWords.length);
    for (var i = 0; i < stmtWords.length; i++) {
      stmtWords[i].classList.toggle('is-lit', i < lit);
    }
  }

  /* ---------------------------------------------------------------
     6. Scroll-driven zoom
        [data-zoom="in"]  grows as its frame scrolls up and away  (hero)
        [data-zoom="out"] starts pushed in and settles as it arrives (arena)

        The transform goes on the <img>, never on the clipping frame: scaling
        the frame would widen the document and push a horizontal scrollbar out.
        Progress is read off the FRAME's rect, not the image's, because the
        image's own rect is what the scale is changing — feeding that back in
        makes the value chase itself and judder.

        The frame is found by class, NOT by el.parentElement: the image's real
        parent is the <picture>, and picture{display:contents} generates no box
        at all, so its rect is all zeros. That silently pinned progress at one
        end and both images sat at scale(1) with no error anywhere.
     --------------------------------------------------------------- */
  var zooms = $$('[data-zoom]');

  function paintZoom() {
    if (reduced) return;
    var vh = window.innerHeight;
    zooms.forEach(function (el) {
      var frame = el.closest('.js-zoomframe');
      if (!frame) return;
      var r = frame.getBoundingClientRect();
      if (!r.height) return;
      if (r.bottom < -120 || r.top > vh + 120) return;

      var dir  = el.dataset.zoom;
      var from = parseFloat(el.dataset.zoomFrom);
      var to   = parseFloat(el.dataset.zoomTo);
      var p;

      if (dir === 'out') {
        // 0 as the band's top edge enters from below, 1 once it is seated
        p = clamp01((vh - r.top) / (vh * 0.55 + r.height * 0.45));
      } else {
        // 0 at rest at the top, 1 once the frame has fully scrolled past
        p = clamp01(-r.top / Math.max(1, r.height));
      }

      el.style.transform = 'scale(' + (from + (to - from) * p).toFixed(4) + ')';
    });
  }

  /* ---------------------------------------------------------------
     6b. Multiplane camera — the hero.

         One scroll progress drives every [data-cam] plane at its own
         rate. Depth is expressed as how far a plane travels and how
         much it grows: the far wall barely shifts while the netting in
         front of the lens sweeps past and out of frame. That difference
         IS the parallax — there is no separate depth value to keep in
         sync, which is what made earlier versions of this drift.

         Progress is read once, off #hero, and reused for all four
         planes. Reading each plane's own rect would feed the transform
         we just wrote back into the next frame's input.
     --------------------------------------------------------------- */
  var camPlanes = $$('[data-cam]');
  var heroRail = $('#hero');                 // the tall wrapper: the scroll budget
  var heroStick = $('#hero > .hero');        // the sticky pane: what stays on screen

  // Phones get a shallower push. Two reasons, both measured rather than assumed:
  // the portrait crop tops out at the source photograph's 1414px height, so a
  // full-depth zoom there upscales into mush; and 2.6 screens of pinned scroll
  // before the first fact is a lot of thumb. The rail is shorter on phones too
  // (see .hero-rail's media query) — this scales the depth to match.
  var narrowCam = window.matchMedia('(max-width:700px)');
  function camGain() { return narrowCam.matches ? 0.5 : 1; }

  function paintCamera() {
    if (reduced || !heroRail || !camPlanes.length) return;
    var r = heroRail.getBoundingClientRect();
    if (r.bottom < -60) return;                       // hero fully behind us

    // Progress runs over the STICKY TRAVEL (rail height minus the pinned pane),
    // not the rail's full height. Measured against the rail, the arc peaked at
    // p=0.5 — but a 168svh rail holding a 100svh pane unsticks at p=0.40, so the
    // push-in reached its peak only after the hero had begun scrolling away.
    // This way the whole in-and-out completes while the frame is still pinned.
    var travel = Math.max(1, r.height - (heroStick ? heroStick.offsetHeight : 0));
    var p = clamp01(-r.top / travel);                 // 0 at rest, 1 when it unsticks

    // The picture planes travel on an ARC, not a ramp: sin(p*PI) is 0 at rest,
    // peaks halfway through the hero, and returns to 0 before the hero leaves.
    // So the frame opens on the whole photograph, the camera pushes in to a
    // detail, and pulls back out again — rather than shoving ever deeper until
    // the image is an unreadable blur at the moment you scroll past it.
    // The copy is deliberately NOT on the arc: it has to leave and stay gone.
    var arc = Math.sin(p * Math.PI);
    var g = camGain();

    camPlanes.forEach(function (el) {
      var dy = (parseFloat(el.dataset.camY) || 0) * g;      // % of its own height at peak
      var ds = (parseFloat(el.dataset.camScale) || 0) * g;  // scale added at peak
      var df = parseFloat(el.dataset.camFade) || 0;    // opacity removed at p=1
      // 'in dataset', not a truthiness test: a valueless HTML attribute like
      // data-cam-arc reads back as the empty string, which is falsy — so
      // `el.dataset.camArc ? ...` silently left every plane on the linear ramp.
      var t  = ('camArc' in el.dataset) ? arc : p;
      el.style.transform =
        'translate3d(0,' + (t * dy).toFixed(3) + '%,0) scale(' + (1 + t * ds).toFixed(4) + ')';
      if (df) el.style.opacity = (1 - clamp01(p * df)).toFixed(3);
    });
  }

  /* ---------------------------------------------------------------
     7. Parallax
     --------------------------------------------------------------- */
  var paras = $$('[data-parallax]');

  function paintParallax() {
    if (reduced) return;
    var vh = window.innerHeight;
    paras.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      var speed = parseFloat(el.dataset.parallax) || 0.08;
      // -1 above the fold .. +1 below it
      var mid = (r.top + r.height / 2 - vh / 2) / vh;
      el.style.transform = 'translate3d(0,' + (mid * speed * 100).toFixed(2) + 'px,0)';
    });
  }

  /* ---------------------------------------------------------------
     8. Scroll loop — one rAF, every reader batched
     --------------------------------------------------------------- */
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      onNavScroll();
      paintWords();
      paintCamera();
      paintZoom();
      paintParallax();
      ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  onScroll();

  /* ---------------------------------------------------------------
     9. Small stuff
     --------------------------------------------------------------- */
  var yr = $('#yr');
  if (yr) yr.textContent = new Date().getFullYear();

})();

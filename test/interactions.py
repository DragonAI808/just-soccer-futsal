"""Exercise the Just Soccer Futsal Center build.

    node serve.js          # in one terminal
    py -3 test/interactions.py

Guards three separate things:
  1. the interactions actually run (scroll zoom, statement, mobile menu)
  2. the layout does not overflow sideways
  3. the *facts* on the page still match the business, and no invented
     content has crept back in
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:4174"
results = []


def settled(page):
    """Wait for the preloader to lift, not for a guessed number of ms.

    The curtain has a minimum hold that has already been retuned once;
    waiting on body.is-loaded keeps these tests correct whatever it becomes."""
    page.wait_for_selector("body.is-loaded", timeout=15000)
    page.wait_for_timeout(300)


def at(page, y):
    page.evaluate("y => window.scrollTo({top:y, behavior:'instant'})", y)
    page.wait_for_timeout(350)


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(("  PASS  " if ok else "  FAIL  ") + name + f"   got={got!r} want={want!r}")


def check_true(name, got):
    check(name, bool(got), True)


with sync_playwright() as p:
    b = p.chromium.launch(headless=True, channel="chrome")

    # ---------------- desktop ----------------
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(URL)
    pg.wait_for_load_state("networkidle")
    settled(pg)

    print("\n[1] MULTIPLANE CAMERA — the hero")

    def scale_of(t):
        # "scale(1.1733)" -> 1.1733 ; "" means JS never wrote one
        return float(t[6:-1]) if t.startswith("scale(") else None

    def plane(sel):
        """Resolved translateY (px) and scale for a plane, from the matrix."""
        return pg.locator(sel).evaluate("""e => {
            const m = new DOMMatrixReadOnly(getComputedStyle(e).transform);
            return { y: m.f, scale: m.a };
        }""")

    # The camera runs over the STICKY TRAVEL — the rail's height minus the pinned
    # pane — not the rail's full height. Sampling anywhere else reads the arc at
    # the wrong point entirely.
    rail = pg.locator("#hero").evaluate("e => e.getBoundingClientRect().height")
    stick = pg.locator("#hero > .hero").evaluate("e => e.offsetHeight")
    travel = rail - stick
    check_true("hero rail is taller than the pinned pane", travel > 200)

    PLANES = (".hero__frame", ".hero__court", ".hero__net")

    at(pg, 0)
    rest = {s: plane(s) for s in PLANES}
    for s, v in rest.items():
        check(f"{s} opens at scale 1 — the whole photograph", round(v["scale"], 2), 1.0)
        check(f"{s} opens unmoved", round(v["y"]), 0)

    at(pg, int(travel / 2))                                  # the arc's peak
    peak = {s: plane(s) for s in PLANES}
    for s, v in peak.items():
        check_true(f"{s} has pushed in at the peak", v["scale"] > 1.02)
        check_true(f"{s} has travelled at the peak", abs(v["y"]) > 4)

    # The hero must still be PINNED at the peak. Before the progress divisor was
    # fixed this fired after the hero had begun scrolling away, so the push-in
    # was only ever seen on its way off screen.
    check("hero is still pinned at the arc's peak",
          round(pg.locator("#hero > .hero").evaluate("e => e.getBoundingClientRect().top")), 0)

    # And it must come back out again — that is the whole point of the arc.
    at(pg, int(travel))
    end = {s: plane(s) for s in PLANES}
    for s, v in end.items():
        check(f"{s} pulls back out to scale 1", round(v["scale"], 2), 1.0)

    # THE assertion. Parallax only exists if the planes disagree — if a refactor
    # ever collapses them onto one shared transform every check above still
    # passes and the depth silently disappears. Near must outrun far.
    check_true("net (near) travels further than the photo (far)",
               abs(peak[".hero__net"]["y"]) > abs(peak[".hero__frame"]["y"]) * 1.5)
    check_true("court (mid) sits between the two",
               abs(peak[".hero__frame"]["y"]) < abs(peak[".hero__court"]["y"]) < abs(peak[".hero__net"]["y"]))
    check_true("net grows faster than the photo",
               peak[".hero__net"]["scale"] > peak[".hero__frame"]["scale"])

    arena_y = pg.locator("#arena").evaluate("e => e.offsetTop")
    at(pg, arena_y - 700)           # band entering from below
    arena_in = scale_of(pg.locator(".arena__media").evaluate("e => e.style.transform"))
    at(pg, arena_y)                 # band seated
    arena_seated = scale_of(pg.locator(".arena__media").evaluate("e => e.style.transform"))
    check_true("arena starts zoomed in", (arena_in or 0) > 1.05)
    check("arena settles to scale 1", round(arena_seated or 0, 2), 1.0)

    print("\n[2] STATEMENT — words light up through the block")
    stmt_y = pg.locator(".stmt").evaluate("e => e.offsetTop")
    at(pg, stmt_y - 700)
    early = pg.locator(".wd.is-lit").count()
    at(pg, stmt_y + 400)
    late = pg.locator(".wd.is-lit").count()
    total = pg.locator(".wd").count()
    check_true("statement was split into words", total > 10)
    check_true("more words lit further down", late > early)

    print("\n[3] REVEALS + LAYOUT")
    check_true("hero content revealed without scrolling",
               pg.locator("#hero [data-reveal]:not(.is-in)").count() == 0)
    at(pg, 2000)
    check_true("programs revealed on scroll",
               pg.locator(".prog__item.is-in").count() >= 3)

    # Nothing may stick out sideways unless an ancestor clips it.
    unclipped = pg.evaluate("""() => {
      const vw = document.documentElement.clientWidth; let n = 0;
      document.querySelectorAll('*').forEach(el => {
        const r = el.getBoundingClientRect();
        if (!r.width || r.right <= vw + 4) return;
        let a = el.parentElement;
        while (a && a !== document.body) {
          const o = getComputedStyle(a).overflowX;
          if (o === 'hidden' || o === 'clip' || o === 'auto' || o === 'scroll') return;
          a = a.parentElement;
        }
        n++;
      });
      return n;
    }""")
    check("nothing overflows sideways unclipped", unclipped, 0)

    print("\n[4] THE FACTS ON THE PAGE")
    body = pg.locator("body").inner_text()
    html = pg.content()
    for fact in ["(951) 525-1846", "210 Dupont Street", "Corona, CA 92879",
                 "info@justsoccerfutsal.org", "5,000"]:
        check_true(f"page still states {fact!r}", fact in body)
    check_true("phone is dialable", "tel:+19515251846" in html)

    # Bookings go to Squarespace Scheduling, not to a page on their own site.
    # There are five of these on the home page and two more on About; asserting
    # the SET rather than "one of them is right" is the point — a missed one
    # sends somebody to a dead URL and nothing else here would notice.
    BOOKING = "https://app.squarespacescheduling.com/schedule/9e3bd3ec"
    book = pg.evaluate("""() => [...document.querySelectorAll('a')]
        .filter(a => a.textContent.trim().toLowerCase() === 'book a session')
        .map(a => a.getAttribute('href'))""")
    check_true(f"home has every Book a session link ({len(book)} found)", len(book) >= 5)
    check("and all of them point at Squarespace Scheduling", sorted(set(book)), [BOOKING])
    check("no link still points at the retired /session page",
          [h for h in book if "justsoccerfutsal.org/session" in h], [])

    # Every in-page nav target must exist, or the nav silently does nothing.
    missing = pg.evaluate("""() => [...document.querySelectorAll('a[href^="#"]')]
        .map(a => a.getAttribute('href'))
        .filter(h => h !== '#' && !document.querySelector(h))""")
    check("every in-page link resolves", missing, [])

    print("\n[5] NOTHING INVENTED, NOTHING NON-US")
    # There are no testimonials, prices or class times on this site because none
    # were supplied. If any appear, they were made up — fail rather than ship it.
    low = body.lower()
    for banned in ["$", "enquir", "colour", "centre", "programme", "testimonial"]:
        check(f"no {banned!r} on the page", banned in low, False)
    # The footer used to carry a photo credit, required while the images were
    # CC-licensed stock. Every photograph is the client's own now, so crediting
    # them on their own site read as odd and the line was removed. What still
    # has to be there is the copyright notice.
    check_true("copyright line is present", "just soccer futsal center," in low)
    check("no self-credit for their own material", "courtesy of just soccer" in low, False)
    check("draft build is still noindex", 'content="noindex, nofollow"' in html, True)

    print("\n[6] DESIGN.md COMPLIANCE")
    # Zero hardcoded PALETTE color outside the :root token block. This is the
    # rule that rots first, because a one-off #fff always looks harmless in
    # isolation.
    #
    # Two exclusions, both deliberate rather than convenient:
    #   - comments, which quote hexes while explaining contrast decisions
    #   - mask gradient stops (mask-image and the --htmask custom properties),
    #     where only the alpha channel is read; the
    #     #000 there is a mask value, not a color, and tokenizing it would imply
    #     it tracks the palette when it must not.
    import re
    css = open("assets/css/site.css", encoding="utf-8").read()
    after_root = css[css.index(":root{"):]
    after_root = after_root[after_root.index("}") + 1:]
    scanned = re.sub(r"/\*.*?\*/", "", after_root, flags=re.S)
    scanned = "\n".join(l for l in scanned.splitlines() if "mask" not in l)
    check("no hardcoded palette hex outside :root",
          re.findall(r"#[0-9A-Fa-f]{3,8}\b", scanned), [])
    check("no raw rgba() channels outside :root",
          re.findall(r"rgba\(\s*\d", scanned), [])
    check("token defines no circular reference",
          re.findall(r"--([a-z-]+):\s*var\(--\1\)", css), [])

    # Every button state the spec requires.
    for state in [r"\.btn:hover", r"\.btn:focus-visible", r"\.btn:active", r"\.btn\[disabled\]"]:
        check_true(f"button has {state}", re.search(state, css) is not None)

    # Headings get their own reveal gesture, not the shared body fade — and the
    # mask must live on the injected child. clip-path is folded into
    # IntersectionObserver's intersection rect, so clipping the observed <h2>
    # itself pins its ratio at 0 and the reveal deadlocks: the heading hides
    # itself and nothing can ever un-hide it. Assert both halves.
    at(pg, 1900)
    head = pg.locator(".game .h2").evaluate("""e => ({
        outer: getComputedStyle(e).clipPath,
        inner: getComputedStyle(e.querySelector('.h2__in')).clipPath,
        isIn:  e.classList.contains('is-in')
    })""")
    check("observed heading box is never clipped", head["outer"], "none")
    check_true("heading has an injected mask child", head["inner"] not in ("none", ""))
    check_true("heading actually revealed when scrolled to", head["isIn"])
    check_true("revealed heading is no longer hidden", "110%" not in head["inner"])
    check("every heading got a mask child",
          pg.locator(".h2[data-reveal]").count(), pg.locator(".h2[data-reveal] > .h2__in").count())

    print("\n[7] LOCAL BUSINESS METADATA")
    import json as _json
    ld = pg.evaluate("""() => {
        const s = document.querySelector('script[type="application/ld+json"]');
        return s ? s.textContent : null; }""")
    check_true("JSON-LD block exists", ld is not None)
    data = _json.loads(ld)
    check("schema type is a local business", data["@type"], "SportsActivityLocation")
    check("structured phone matches the page", data["telephone"], "+1-951-525-1846")
    check("structured street matches the page",
          data["address"]["streetAddress"], "210 Dupont Street")
    check("structured zip matches the page", data["address"]["postalCode"], "92879")
    # Hours live in two places; if they drift apart Google shows the wrong one.
    hours = data["openingHoursSpecification"][0]
    check("structured hours cover all 7 days", len(hours["dayOfWeek"]), 7)
    check("structured closing time matches the scoreboard",
          hours["closes"], "23:00")
    check_true("scoreboard shows the 11PM close", "11:00 PM" in body)

    for tag in ['rel="canonical"', 'property="og:image"', 'name="twitter:card"',
                'rel="icon"', 'name="theme-color"']:
        check_true(f"head carries {tag}", tag in html)
    check_true("og:image is an absolute url",
               'content="https://www.justsoccerfutsal.org/assets/img/og-1200x630.jpg"' in html)

    print("\n[8] INSTAGRAM REELS — facades, nothing loads until asked")
    # The entire point of a facade is that Meta is not contacted on page load.
    # If someone ever swaps these for Instagram's stock blockquote+script, every
    # visitor gets ~1MB of Meta JS and a tracking cookie whether they watch or
    # not — and the page would still look completely fine. Hence a network test
    # rather than a DOM one. A fresh context, so cookies start empty.
    ig_ctx = b.new_context(viewport={"width": 1440, "height": 950})
    ig = ig_ctx.new_page()
    seen_hosts = set()
    ig.on("request", lambda r: seen_hosts.add(r.url.split("/")[2]))
    ig.goto(URL)
    ig.wait_for_load_state("networkidle")
    settled(ig)
    doc_h = ig.evaluate("document.documentElement.scrollHeight")
    yy = 0
    while yy < doc_h:                       # scroll the lot; lazy images fire
        ig.evaluate("y => window.scrollTo({top:y, behavior:'instant'})", yy)
        ig.wait_for_timeout(80)
        yy += 700

    def meta_hosts():
        return sorted(h for h in seen_hosts
                      if "instagram" in h or "facebook" in h or "cdninstagram" in h)

    check("no Meta request on page load", meta_hosts(), [])
    check("no cookies set on page load", len(ig_ctx.cookies()), 0)
    check("both reels render as facades", ig.locator(".reel .reel__btn").count(), 2)
    check("no live embed before a click", ig.locator(".reel.is-live").count(), 0)
    # The covers must be self-hosted, or the facade leaks the request it exists to prevent.
    covers = ig.evaluate("""() => [...document.querySelectorAll('.reel__btn img')]
        .map(i => new URL(i.currentSrc, location.href).host)""")
    check("reel covers are served from our own origin",
          [h for h in covers if "localhost" not in h and "127.0.0.1" not in h], [])

    ig.locator(".latest").scroll_into_view_if_needed()
    ig.wait_for_timeout(400)
    ig.locator(".reel").first.locator(".reel__btn").click()
    ig.wait_for_timeout(6000)
    check_true("clicking a reel marks it live", ig.locator(".reel.is-live").count() == 1)
    check_true("clicking a reel reaches Instagram", len(meta_hosts()) > 0)
    check_true("an embed iframe was built", ig.locator(".reel.is-live iframe").count() >= 1)
    check("the other reel is still a facade", ig.locator(".reel:not(.is-live)").count(), 1)
    ig_ctx.close()

    # ---------------- phone ----------------
    print("\n[9] PHONE — menu + no sideways scroll")
    ph = b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    ph.goto(URL)
    ph.wait_for_load_state("networkidle")
    settled(ph)

    check("menu starts closed", ph.locator("#navLinks").evaluate(
        "e => e.classList.contains('is-open')"), False)
    ph.locator("#burger").click()
    ph.wait_for_timeout(500)
    check("burger opens the menu", ph.locator("#navLinks").evaluate(
        "e => e.classList.contains('is-open')"), True)
    check("body scroll is locked while open",
          ph.evaluate("getComputedStyle(document.body).overflow"), "hidden")
    ph.locator("#navLinks a[href='#programs']").click()
    ph.wait_for_timeout(500)
    check("choosing a link closes the menu", ph.locator("#navLinks").evaluate(
        "e => e.classList.contains('is-open')"), False)
    check("body scroll is restored",
          ph.evaluate("document.body.style.overflow"), "")

    check("phone hero uses the portrait crop",
          "portrait" in ph.locator(".hero__media").evaluate("e => e.currentSrc"), True)

    # Narrow widths, WITHOUT mobile emulation. Playwright's is_mobile pins
    # innerWidth at 392 whatever viewport you ask for, so a phone-emulated page
    # cannot see an overflow below that — which is how a real one hid here for
    # ages, reading as a harmless 2px at 390 while an iPhone SE at 375 got a
    # horizontal scrollbar. Measure the document itself at true widths.
    for narrow in (320, 375):
        nb = b.new_page(viewport={"width": narrow, "height": 900})
        nb.goto(URL)
        nb.wait_for_load_state("networkidle")
        settled(nb)
        nh = nb.evaluate("document.documentElement.scrollHeight")
        ny = 0
        while ny < nh:                       # walk it; reveals change widths
            nb.evaluate("y => window.scrollTo({top:y, behavior:'instant'})", ny)
            nb.wait_for_timeout(60)
            ny += 800
        over = nb.evaluate(
            "document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check(f"no document overflow at {narrow}px", over, 0)
        nb.close()

    print("\n[10] THE MENU MUST NOT STRAND ANYONE")

    # Open the menu on a phone, then rotate to landscape (or resize past the
    # 900px breakpoint). The burger becomes display:none, so if the menu keeps
    # its open state the body stays overflow:hidden with no control on screen
    # that can release it — the page cannot be scrolled and only a reload gets
    # you out. A scripted window.scrollTo does NOT reproduce this (it ignores
    # the lock), which is why this drives a real wheel gesture.
    rt = b.new_page(viewport={"width": 390, "height": 844})
    rt.goto(URL)
    rt.wait_for_load_state("networkidle")
    settled(rt)
    rt.click("#burger")
    rt.wait_for_timeout(300)
    check_true("menu opens on the phone",
               rt.evaluate("document.getElementById('navLinks').classList.contains('is-open')"))
    rt.set_viewport_size({"width": 1280, "height": 800})
    rt.wait_for_timeout(600)
    check("widening closes the menu",
          rt.evaluate("document.getElementById('navLinks').classList.contains('is-open')"), False)
    check("widening releases the scroll lock", rt.evaluate("document.body.style.overflow"), "")
    rt.mouse.move(640, 400)
    rt.mouse.wheel(0, 900)
    rt.wait_for_timeout(500)
    check_true("the page still scrolls afterwards", rt.evaluate("window.scrollY") > 100)
    rt.close()

    print("\n[11] CONTRAST + TAP TARGETS")

    cw = b.new_page(viewport={"width": 1440, "height": 900})
    cw.goto(URL)
    cw.wait_for_load_state("networkidle")
    settled(cw)

    # Every .btn on the page must be ink-on-orange. `.nav__links a` is (0,1,1)
    # and outranks `.btn` (0,1,0), so the header CTA silently rendered white on
    # #EF6C00 — 3.08:1, the exact pairing DESIGN.md rejects, on the one button
    # visible for the whole visit. Assert all of them, not just the nav one.
    btn_colors = cw.evaluate(
        "() => [...document.querySelectorAll('.btn:not(.btn--ghost)')]"
        ".map(e => getComputedStyle(e).color)")
    check("every solid button uses ink on orange",
          sorted(set(btn_colors)), ["rgb(6, 22, 52)"])

    # WCAG 2.2 SC 2.5.8: interactive targets are at least 24x24 CSS px.
    small = cw.evaluate("""() => {
        const bad = [];
        document.querySelectorAll('a, button').forEach(el => {
            const r = el.getBoundingClientRect();
            if (!r.width || !r.height) return;
            if (getComputedStyle(el).visibility === 'hidden') return;
            if (r.height < 24 || r.width < 24) bad.push(
                (el.textContent.trim() || el.getAttribute('aria-label') || el.tagName).slice(0, 30)
                + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
        });
        return bad;
    }""")
    check("no interactive target under 24px", small, [])

    print("\n[12] THE WAIVER PDF")

    wv = cw.locator('a[href$="clinic-waiver.pdf"]')
    check("the footer links the waiver", wv.count(), 1)
    # A PDF that swallows the site tab is the failure mode this link exists to
    # avoid, so target and rel are asserted, not assumed.
    check("it opens in its own tab", wv.get_attribute("target"), "_blank")
    check_true("it carries rel=noopener", "noopener" in (wv.get_attribute("rel") or ""))
    # WCAG 3.2.5: a link that moves you somewhere unexpected has to say so.
    check_true("it announces the new tab",
               "new tab" in (wv.get_attribute("aria-label") or "").lower())
    check_true("(PDF) is visible in the link text", "PDF" in wv.inner_text())

    # The file has to exist and be served AS a PDF. Falling through to
    # octet-stream makes the browser download it instead of opening it, which
    # defeats the whole point of the new tab.
    pdf = cw.request.get(URL + "/assets/docs/clinic-waiver.pdf")
    check("the file is actually there", pdf.status, 200)
    check_true("served as application/pdf", "application/pdf" in pdf.headers.get("content-type", ""))
    check_true("and it is a real PDF", pdf.body()[:5] == b"%PDF-")
    cw.close()

    print("\n[13] THE ABOUT PAGE")

    ab = b.new_page(viewport={"width": 1440, "height": 900})
    ab.goto(URL + "/about.html")
    ab.wait_for_load_state("networkidle")
    ab.wait_for_timeout(1200)

    # Their words, not a paraphrase of them. The home page already carries a
    # compressed version of the mission in the statement band; the whole point
    # of this page is that the original survives intact here. If someone
    # rewrites these, the page stops being an About page and becomes a second
    # home page.
    mission = ab.locator(".mission__body").inner_text()
    for phrase in ("positive and entertaining environment",
                   "highest potential",
                   "purest forms of the Sport",
                   "health, respect and love for the community"):
        check_true(f"mission keeps: {phrase[:34]}", phrase in mission)

    founder = ab.locator("#founder").inner_text()
    check_true("founder section names Hernan Garcia", "Hernan Garcia" in founder)
    check_true("and Coach Ernie", "Coach Ernie" in founder)

    facility = ab.locator("#facility").inner_text()
    check_true("facility keeps the 5,000 sq ft line", "5,000 sq ft" in facility)

    # This page has no photographic hero, so a transparent bar would put white
    # nav text on the white mission band with nothing in the console.
    check_true("nav is solid from the top",
               ab.locator("#nav").evaluate(
                   "e => getComputedStyle(e).backgroundColor !== 'rgba(0, 0, 0, 0)'"))
    # inner_text() returns the CSS-transformed string, and the nav uppercases.
    check("the current page is marked in the nav",
          ab.locator('.nav__links a[aria-current="page"]').inner_text().lower(), "about")

    # Heading levels must not skip. The footer heads used to be <h4>; on the
    # home page h3s sat between them and the h2s, but this page has none, so
    # h2 -> h4 skipped a level for anyone navigating by heading.
    levels = ab.evaluate(
        "() => [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => +h.tagName[1])")
    skips = [(a, c) for a, c in zip(levels, levels[1:]) if c > a + 1]
    check("no skipped heading levels on About", skips, [])
    check("exactly one h1", levels.count(1), 1)

    # Both pages have to reach each other, or the nav is decorative.
    check_true("About links home", ab.locator('a[href="index.html"]').count() > 0)
    abook = ab.evaluate("""() => [...document.querySelectorAll('a')]
        .filter(a => a.textContent.trim().toLowerCase() === 'book a session')
        .map(a => a.getAttribute('href'))""")
    check("About's booking links go to Squarespace too", sorted(set(abook)),
          ["https://app.squarespacescheduling.com/schedule/9e3bd3ec"])

    # The nav and footer are copy-pasted into every page rather than templated,
    # so they can silently drift apart — the h4 -> h3 change touched both files
    # and would have desynced them if only one had been edited. Compare the
    # rendered typography of the shared chrome page against page, at one
    # viewport, rather than trusting that the markup still matches.
    CHROME = """() => {
        const t = s => { const e = document.querySelector(s); if (!e) return s + ':MISSING';
            const c = getComputedStyle(e);
            return [c.fontSize, c.fontWeight, c.letterSpacing, c.lineHeight,
                    c.fontFamily.split(',')[0], c.textTransform].join('|'); };
        return { footLink: t('.foot ul a'), footHead: t('.foot h3'),
                 footSign: t('.foot__sign'), footAddr: t('.foot__addr'),
                 footBase: t('.foot__base p'), navLink: t('.nav__links a:not(.btn)'),
                 navBtn: t('.nav__links .btn'), brand: t('.brand__txt') };
    }"""
    chrome_home = pg.evaluate(CHROME)
    chrome_about = ab.evaluate(CHROME)
    for part in chrome_home:
        check(f"shared chrome matches across pages: {part}",
              chrome_about[part], chrome_home[part])
    hm = b.new_page(viewport={"width": 1440, "height": 900})
    hm.goto(URL)
    hm.wait_for_load_state("networkidle")
    settled(hm)
    check_true("home links About from the nav",
               hm.locator('.nav__links a[href="about.html"]').count() == 1)
    check_true("home links About from the footer",
               hm.locator('.foot a[href="about.html"]').count() == 1)
    hlv = hm.evaluate(
        "() => [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => +h.tagName[1])")
    check("no skipped heading levels on home",
          [(a, c) for a, c in zip(hlv, hlv[1:]) if c > a + 1], [])
    hm.close()

    over = []
    for w in (320, 375, 768, 1024, 1920):
        nb = b.new_page(viewport={"width": w, "height": 900})
        nb.goto(URL + "/about.html")
        nb.wait_for_load_state("networkidle")
        nb.wait_for_timeout(700)
        if nb.evaluate("document.documentElement.scrollWidth"
                       " - document.documentElement.clientWidth"):
            over.append(w)
        nb.close()
    check("About does not overflow sideways at any width", over, [])

    # The founder picture must clear the touchline BADGE, not just the rule.
    # The circle hangs half its diameter below the line and the crest's halftone
    # spray reaches past that again, so a gap measured to the line looked like a
    # collision on screen.
    clearance = ab.evaluate("""() => {
        const mark = document.querySelector('.touchline__mark').getBoundingClientRect();
        const fig  = document.querySelector('.about-split__figure').getBoundingClientRect();
        return Math.round(fig.top - mark.bottom);
    }""")
    check_true(f"picture clears the divider badge ({clearance}px)", clearance >= 40)

    # And it has to sit BESIDE the copy, not tower over it.
    ratio = ab.evaluate("""() => {
        const f = document.querySelector('.about-split__figure').getBoundingClientRect().height;
        const t = document.querySelector('.about-split__body').getBoundingClientRect().height;
        return f / t;
    }""")
    check_true(f"picture is not more than 1.5x the text ({ratio:.2f}x)", ratio <= 1.5)

    # Copy on the left at the page margin, picture on the right — and the copy
    # must come FIRST in the DOM, so the heading leads on a phone and in a
    # screen reader rather than trailing the illustration.
    order = ab.evaluate("""() => {
        const s = document.querySelector('.about-split');
        return [...s.children].map(c => c.className.split(' ')[0]);
    }""")
    check("copy comes before the picture", order[0], "about-split__body")
    sides = ab.evaluate("""() => {
        const b = document.querySelector('.about-split__body').getBoundingClientRect();
        const f = document.querySelector('.about-split__figure').getBoundingClientRect();
        return { copyLeft: Math.round(b.left), figLeft: Math.round(f.left) };
    }""")
    check_true("copy sits left of the picture", sides["copyLeft"] < sides["figLeft"])

    # The illustration is exactly 4:5 and is the one image on the site that must
    # not be cropped — the ball and the tactics board are what make it read as a
    # coach, and both sit in the corners.
    crop = ab.evaluate("""() => {
        const img = document.querySelector('.about-split__figure img');
        const box = document.querySelector('.about-split__figure').getBoundingClientRect();
        return Math.abs((box.width / box.height) - (img.naturalWidth / img.naturalHeight));
    }""")
    check_true(f"coach illustration is not cropped (ratio delta {crop:.3f})", crop < 0.02)
    check_true("and it is the coach artwork, not the old photo",
               "coach" in ab.locator(".about-split__figure img").get_attribute("src"))

    # The facility band ends on the same colour the footer begins on, so with no
    # tonal difference the two blues ran together as one endless field. The fix
    # is a genuine step in value rather than a drawn rule, so assert the two
    # grounds actually differ — this is invisible to every other check here.
    step = ab.evaluate("""() => {
        const scrim = getComputedStyle(document.querySelector('#facility .arena__scrim'));
        const foot  = getComputedStyle(document.querySelector('.foot')).backgroundColor;
        // last colour stop of the scrim gradient is what meets the footer
        const stops = scrim.backgroundImage.match(/rgba?\\([^)]*\\)/g) || [];
        return { last: stops[stops.length - 1], foot };
    }""")
    check_true("the scrim ends on a different value than the footer",
               step["last"] is not None and "42, 120" not in step["last"])
    check_true("and it resolves to the lighter royal", "0, 57, 165" in (step["last"] or ""))
    check("no drawn rule is needed at the seam",
          ab.evaluate("() => parseFloat(getComputedStyle("
                      "document.getElementById('facility')).borderBottomWidth)"), 0)
    ab.close()

    b.close()

print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)

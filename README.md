# Just Soccer Futsal Center — website

A two-page, dependency-free site for the futsal center at 210 Dupont Street,
Corona, California. Plain HTML, CSS and JavaScript: no build step, no framework,
no `npm install`. Open it, edit it, ship it.

## Preview it locally

```bash
node serve.js
```

Then open <http://localhost:4174>. (`serve.js` is a ~60-line static server that
supports HTTP range requests. `file://` works for this site since there is no
video yet, but use the server anyway — the tests point at it, and range support
is already there for when clips get added.)

## Files

```
index.html                  the home page - all its markup and copy
about.html                  the About page - mission, founder, facility
DESIGN.md                   the design spec — read this before restyling anything
assets/css/site.css         design tokens + every style
assets/js/site.js           preloader, reveal, nav, statement, camera, zoom, parallax
                            (shared by both pages - about.html loads the same file)
assets/img/logo-source.png  the club badge, 1298x1212 with alpha (master)
assets/img/logo-{720,260}.webp  derived sizes actually used by the page
assets/img/favicon-180.png  tab icon (the ball, cropped from the master)
assets/img/og-1200x630.jpg  social share card
assets/img/coach-source.png the Coach Ernie illustration, 1122x1402 (master)
assets/img/coach-900.{webp,jpg}  derived size used by about.html
assets/docs/clinic-waiver.pdf   the club's liability waiver, linked from the footer
assets/video/               empty; drop clips here when there are any
serve.js                    local preview server
tools/add-clip.sh           ffmpeg pipeline for making a raw clip web-ready
tools/site.ps1              take the live site off/on (see below)
test/interactions.py        Playwright suite — run it after any change
```

`DESIGN.md` is the readable version of the `:root` block: palette with RGB helpers
and the role each color plays, the measured contrast table, the type scale, every
component's five states, layout tokens, the motion tier and why it is L2 and not
L3, twelve do's-and-don'ts, and the responsive rules. It documents the identity
rather than proposing one — **both brand colors are sampled from the pixels of the
club badge**, so they are not ours to change. Read it before restyling; the test
suite enforces parts of it.

## What's on the page

| Section | Notes |
|---|---|
| Hero | **Multiplane parallax with a scroll-driven camera** — see below. Headline rises word by word. Phones get an art-directed portrait crop, not a squeezed landscape. |
| Ticker | Infinite marquee of what runs at the center. Pauses on hover. |
| **Tonight** | An arena **scoreboard** carrying the hours. It is second on the page because "is it open" is the question most visitors arrive with. |
| Statement | The mission. Words light up one at a time as you scroll through. |
| Futsal | Four cells explaining what futsal actually is, as distinct from indoor soccer. |
| Programs | The six things that run, numbered in outlined **jersey numerals**. |
| Arena | Full-bleed band of the hall whose photograph **zooms out as it arrives** — the opposite move to the hero, so the trick does not read as the same effect twice. |
| **Latest** | Two Instagram reels as **click-to-load facades**, under the scoreboard. Meta is not contacted until someone plays one. Meant to be swapped — the posts are dated. |
| Story | Coach Ernie and why the place exists — a **triptych**: photograph, text, photograph. Both pictures render at identical size and stretch to the height of the text. |
| Visit | Address, phone, both email addresses, map link. |
| Footer | A closing line in Anton, badge, address linked to Maps, socials, nav columns, the waiver PDF, copyright. |

### about.html

| Section | Notes |
|---|---|
| Page head | Their own sign-off, "Live your passion! Play the game!", as the h1. Solid nav — see below. |
| Mission | **Their words, verbatim.** See the warning under it. |
| Founder | Coach Ernie. Copy left at the page margin, the brand illustration right, and his own email address below the copy. |
| Facility | The arena band reused from the home page, left-aligned because it holds body copy here rather than four stats. |

The copy came from `justsoccerfutsal.org/about`. The home page already carries a
**compressed** version of the mission in its statement band ("A positive,
entertaining place where players reach their highest potential") and of the
founder story in the triptych ("Built to give the game a stage" is lifted from
"provide the stage"). That split is deliberate: **home teases, About tells.** If
someone rewrites the About copy into a paraphrase, the page stops earning its
place. The suite asserts four phrases from the mission survive intact.

Only four edits were made to their text, all mechanical, none to meaning:
`devoted to provide` → `devoted to providing`; `player's development` →
`players' development`; a stray comma removed from `our non-stop action, will
push`; and `Sports Facility` lowercased mid-sentence. **Their capitalisation of
"the Sport", "the Game" and "Essence of the Game" is left exactly as written** —
that is house style, not an error.

One thing worth deciding: the About copy says **"Just Soccer FC"** throughout,
the site says **"Just Soccer Futsal Center"**, and the waiver says **"Just Soccer
FC LLC"**. Three names for one business. Left as-is because it is quoted text,
but it is the sort of thing a visitor notices.

**The coach illustration must not be cropped.** `coach-source.png` is 1122x1402,
exactly 4:5, and `.about-split__figure` is set to 4:5 to match so `object-fit`
takes nothing off. The ball sits in the bottom-left corner and the tactics board
in the top-right, and those are the two things that make it read as a coach
rather than a portrait. It is capped by WIDTH, never by height, for that reason.
It is also the only illustration on the site - everything else is photography.

**The footer seam.** The facility band ends on `rgb(1,42,120)` and the footer
begins on `rgb(1,42,120)`. Identical, so with nothing between them the two read
as one endless blue field. The home page never hits this because its footer
follows the chalk Visit section. It is solved by ending the facility scrim on
`--royal` instead of `--royal-dp`, so the boundary is a genuine step in value
rather than a rule drawn across it - a line was tried first and looked like a
line. If you restyle either background, keep them different or put something
back. The suite asserts the two grounds differ.

`#nav.is-solid` exists for this page: the home bar is transparent until you
scroll past 72% of the hero, which works because it sits on a photograph for
that whole distance. About has no photographic hero, so a transparent bar would
put white nav text on the white mission band — invisible, with nothing in the
console. Any future page without a full-height photo hero needs that class.

It is defined **beside `#nav.is-stuck`**, not in the About section, and the
order of the three nav-state rules matters. `.is-stuck`, `.is-solid` and
`.is-menu-open` are all `(1,1,0)`, so source order decides — and
`.is-menu-open` must come last, because it is the one that removes the
`backdrop-filter`. See the comment on it: that removal is load-bearing.

### The multiplane camera

The hero sits in a **250svh rail** with a `position: sticky` pane inside it, and
four planes driven by one scroll progress. It opens on the whole photograph,
pushes in to the centre-circle ball graphic, and **pulls back out** before the
page moves on — an arc, not a one-way ramp. The whole move happens while the
frame is pinned, over about 1.5 screens of scroll.

Tuned entirely from HTML attributes:

```html
<div class="hero__plane hero__frame" data-cam data-cam-arc data-cam-y="-4"  data-cam-scale="0.52">
<div class="hero__plane hero__court" data-cam data-cam-arc data-cam-y="-15" data-cam-scale="0.92" data-cam-fade="0.6">
<div class="hero__plane hero__net"   data-cam data-cam-arc data-cam-y="-38" data-cam-scale="1.75" data-cam-fade="0.9">
<div class="hero__inner"             data-cam             data-cam-y="-7"  data-cam-scale="0"    data-cam-fade="1.25">
```

`data-cam-y` is travel as a percentage of the plane's own height at the arc's
peak, `data-cam-scale` the growth added, `data-cam-fade` the opacity removed.
`data-cam-arc` opts a plane into the in-and-out curve; the copy is deliberately
left off it, because it has to leave and stay gone.

The far wall barely shifts; the netting in front of the lens sweeps past. That
difference *is* the parallax.

The push peaks at **1.52×** on the centre-circle ball graphic — `.hero__frame`
overrides `transform-origin` to 54% 74% so the camera converges on the ball
rather than on the middle of the frame. At that scale the image renders 2408px
wide from a 2400px source, so it stays sharp; go much deeper and it will soften.

**Phones get half of it.** The rail drops to 160svh and `site.js` halves every
camera value at the same breakpoint, peaking at ~1.26. The phone crop is capped
at 1180×1414 by the source photograph's height, so a full-depth push would
upscale into mush — and 2.6 screens of pinned scroll is a lot of thumb.

It is native `position: sticky`, not scroll-jacking — scroll velocity, momentum
and the scrollbar are all untouched. **The cost is real:** the scoreboard sits
2.6 screens down on desktop, 1.7 on a phone. That is why **Hours** is the first
item in the nav. If that trade stops feeling worth it, drop `.hero-rail` to
`140svh` and lower `data-cam-scale` to taste — nothing else needs to change.

**If you retune it, keep near > mid > far.** Parallax exists only because the
planes disagree — flatten them toward each other and the depth quietly vanishes
while everything still appears to work. The suite asserts the ordering for that
reason.

The near plane is netting because every photograph of the building is shot through
the net; the foreground is observed rather than invented. All of it is off under
`prefers-reduced-motion`.

Three things that are load-bearing and not obvious:

- Transforms go on **planes**, never on `.hero`. Scaling the section widens the
  document and pushes a horizontal scrollbar out.
- Progress divides by the **sticky travel**, not the rail height, and is read
  **once**. Reading each plane's own rect feeds the
  transform just written back in as the next frame's input, and it judders.
- The arena band still uses the simpler `data-zoom` module, and that one finds its
  frame with `el.closest('.js-zoomframe')`, **not** `el.parentElement` — the
  image's real parent is `<picture>`, and `picture{display:contents}` generates no
  box, so its rect is all zeros. That silently pinned it at `scale(1)` once
  already. If a zoom ever stops working, look there first.

## Swapping the Instagram reels

The two reels under the scoreboard are **facades**: a self-hosted cover image
plus a play badge. Instagram is contacted only when a visitor clicks one. To
change a reel you need its id (the code in its URL) and a cover image.

Get the cover from Instagram's own oEmbed endpoint — not a scraper, not one of
those third-party downloader sites:

```powershell
curl -s "https://www.instagram.com/api/v1/oembed/?url=https://www.instagram.com/reel/REEL_ID/"
```

Take `thumbnail_url` from the JSON, download it, then:

```powershell
ffmpeg -i cover.jpg -c:v libwebp -quality 82 -y assets/img/reel-NAME.webp
ffmpeg -i cover.jpg -q:v 4 -y assets/img/reel-NAME.jpg
```

Then in `index.html` update that tile's `data-reel` id, its two image paths, the
`alt` text and the `.reel__cap` line. Nothing in the CSS or JS changes.

**Keep them current.** These posts are dated by nature — the Futsal Fridays reel
literally says *"tomorrow"* in its Instagram caption, which is why the caption
written on the site leaves that word out. A reel that was news in September
reads as neglect by March.

**Do not replace the facades with Instagram's stock embed code.** It pulls ~1MB
of Meta script and sets a tracking cookie on every visitor, whether or not they
ever play a reel — and the page would look identical either way, which is
exactly why it would go unnoticed. `test/interactions.py` asserts that no Meta
request happens before a click, so that swap fails the suite.

## Taking the live site off and on

`tools/site.ps1` is the switch. Run it from PowerShell in the project root:

```powershell
.\tools\site.ps1 status
.\tools\site.ps1 off
.\tools\site.ps1 on
```

| Command | Effect |
|---|---|
| `status` | Prints repo visibility, Pages state, and the live HTTP code |
| `off` | Disables Pages. Repo stays public and browsable; only the site goes |
| `on` | Re-enables Pages from `main`, waits for the build, confirms it is up |
| `hide` | `off` **and** makes the repo private, so the source is hidden too |
| `show` | Public again, then back online |

The URL never changes — it is derived from owner and repo name — and nothing
here touches your commits. Tested end to end: off, verified, on, verified.

### One caveat worth knowing before you rely on `off`

**It is not instant.** GitHub Pages sits behind Fastly, and the HTML is cached
at the edge with `max-age=600`. After `off`:

- The origin stops serving **immediately** — CSS, JS and images 404 at once
- Anyone whose edge node already has the HTML cached can still get the page for
  up to ~10 minutes, but it will be **unstyled**, because the stylesheet is
  already gone
- New visitors, and anyone on an edge without a cached copy, get a 404 straight
  away

So `off` is reliable for "stop showing people this," but there is a window where
a visitor mid-session sees a broken-looking page rather than a clean 404. If you
need a clean handover, `off` and then wait ten minutes before assuming it is
fully down. Nothing on our side can shorten that; it is Fastly's TTL.

`on` has no such issue: the build takes 30-60 seconds and the script waits for
it, then verifies the URL actually returns 200 before telling you it is live.

## Cache busting — bump this when you change CSS or JS

`index.html` loads the stylesheet and script with a version marker:

```html
<link rel="stylesheet" href="assets/css/site.css?v=14">
<script src="assets/js/site.js?v=14"></script>
```

**Increment both numbers whenever you edit `site.css` or `site.js`.** GitHub
Pages serves those files with `Cache-Control: max-age=600`, and phone browsers
routinely hold them far longer than that. Without a changed URL a returning
visitor keeps the old stylesheet and simply does not see your change — which is
exactly what happened after the phone-layout fix: the deployed CSS was correct
and the phone was still rendering the previous one.

`index.html` itself is served with a short cache, so the new marker propagates
on the next page load. Images are content-named already and do not need this.

## Before this goes live — please read

### 1. The photography is yours now — but check the resolution ceiling

Every image on the page is pulled from your own site's CDN, so there is no
licensing question left: the hero and social card come from `Futsal 4.jpg`, the
arena band and the story crop from `Futsal wide angle pics-126.jpg`. The badge came separately
and is covered in section 2. The Czech stock placeholders are gone.

Two ceilings worth knowing:

| Asset | Native size | Consequence |
|---|---|---|
| `Futsal 4.jpg` (hero) | 2500px | Plenty. No issue. |
| `Futsal wide angle pics-126.jpg` | **1291px** | Mild upscale in the arena band; the scrim hides it. Don't promote it to a full-height hero. |
| `logo-source.png` (badge) | **1298×1212, alpha** | No longer a constraint. Only a vector would beat it, and only for print. |

**If you have the originals** — on a phone, a camera card, a hard drive — they are
a drop-in replacement. Same filenames, same crops, no code changes. That is the
one remaining upgrade to this site.

About the Yelp photos you sent: I could see them but not read them as files, so
none of them are in the build. If you want any of them in, save them into
`assets/img/` and say which goes where. The ones your business took and posted are
yours to use; ones uploaded by customers belong to those customers, so pick from
your own.

### 2. The badge — done, and how to regenerate it

`assets/img/logo-source.png` is the master: **1298×1212 with a real alpha
channel**. The page never loads it directly; it uses two derived sizes:

| File | Size | Used by |
|---|---|---|
| `logo-720.webp` | 208 KB | preloader, story section |
| `logo-260.webp` | 48 KB | nav mark, footer |
| `favicon-180.png` | 64 KB | tab icon — the ball, cropped from the master |

To regenerate after replacing the master:

```powershell
ffmpeg -i assets/img/logo-source.png -vf "scale=720:-1:flags=lanczos" -c:v libwebp -quality 82 -y assets/img/logo-720.webp
ffmpeg -i assets/img/logo-source.png -vf "scale=260:-1:flags=lanczos" -c:v libwebp -quality 86 -y assets/img/logo-260.webp
ffmpeg -i assets/img/logo-source.png -vf "crop=490:490:352:344,scale=180:180:flags=lanczos" -y assets/img/favicon-180.png
```

**Encode lossy, not lossless.** The halftone dots and spray spatter behave like
photographic noise: lossless WebP produced 816 KB at 900px, lossy at q82 gives
208 KB at 720px with nothing visibly lost. `libwebp` preserves the alpha channel
either way — check with `ffprobe`, the pixel format should read `yuva420p`.

The nav badge has no white chip behind it any more. That only ever existed
because the earlier badge was a full-colour mark on opaque white, and keying that
white out would have taken the ball's own white panels with it.

### 3. Details that disagree between sources — check before publishing

Your own site and the directory listings do not match. I used your site in every
case, but three are worth confirming:

| | On this site (from justsoccerfutsal.org) | Directories say |
|---|---|---|
| Phone | (951) 525-1846 | (949) 701-3266 |
| Address | 210 Dupont Street, Corona, CA 92879 | 210 Dupont **Ave, Ste 104** |
| Hours | Daily 4pm–11pm | Mon 4:30pm–12am, Tue–Fri 4pm–12am, Sat–Sun 8am–8pm |

The hours one matters most: the site currently tells people the court closes at
11pm every day, and the weekend difference is large if the directory is right.

### 4. The hours now live in two places — keep them in step

The page carries `SportsActivityLocation` structured data (JSON-LD in `<head>`).
That block is what puts your hours, phone number and map pin into a Google
result, so it is worth having — but it means **the hours are now written twice**:
once on the scoreboard, once in `openingHoursSpecification`. Change one and you
must change the other, or Google will publish a closing time your own page
contradicts. `test/interactions.py` asserts the two agree and fails if they drift.

The same applies to the phone number, street address and zip, which are also
asserted against the structured data.

`og:image` and `canonical` point at `https://www.justsoccerfutsal.org/`. They are
absolute by necessity — social scrapers cannot resolve relative paths — so the
share card will not preview from localhost. That is expected, not broken.

### 5. There is deliberately nothing invented

No prices, no class times, no testimonials, no founding year, no coach bios
beyond Coach Ernie's name — because none were supplied. Everything on the page
traces to justsoccerfutsal.org. `test/interactions.py` fails if a currency
symbol or the word "testimonial" appears, which is a guard against filler
quietly becoming permanent. Add real ones; don't let placeholder ones ship.

Program schedules are written as "call for the current schedule" rather than
naming days, for the same reason. Fill those in once you have them.

### 6. Bookings go off-site, to Squarespace Scheduling

Every **Book a session** button points at
`https://app.squarespacescheduling.com/schedule/9e3bd3ec` - **seven of them**:
nav, hero, Programs head, Visit card and footer on `index.html`, plus nav and
footer on `about.html`. They used to point at `justsoccerfutsal.org/session`.

If the scheduling link ever changes, change all seven. `test/interactions.py`
asserts the whole SET matches, not that one of them is right, so a missed link
fails loudly rather than quietly sending somebody to a dead URL.

Every off-site link opens in a new tab - booking, Google Maps, and the three
social profiles: 12 on `index.html`, 6 on `about.html`, plus the waiver PDF.
`tel:`, `mailto:` and in-page anchors deliberately do NOT, since `target` on a
`mailto:` leaves a blank tab behind in some browsers.

Each one says so in its accessible name (WCAG 3.2.5). Icon links extend the
`aria-label` they already carry; text links get `<span class="vh"> (opens in a
new tab)</span>` appended, which keeps the visible words at the START of the
accessible name so voice control still matches what a user can read (WCAG
2.5.3). The `.vh` span is `position:absolute`, so it is not a flex item and adds
no gap inside a `.btn`.

### 7. The waiver PDF is a blank template — keep it that way

`assets/docs/clinic-waiver.pdf` is the club's own "Just Soccer FC LLC Release
and Waiver of Liability" form, supplied by Stewart and linked from the footer's
*Get on the court* column. It is a **blank** template: no names, no signatures,
no participant details. That is the only version that belongs on a public URL —
if a completed one ever replaces it, it publishes somebody's personal data, and
a signed minor release publishes a child's.

The link is `target="_blank"` on purpose so a PDF viewer never swallows the site
tab, with `rel="noopener"` and an `aria-label` that says it opens a new tab.
`serve.js` maps `.pdf` so local preview matches what GitHub Pages sends; without
it the file downloads instead of opening and the new tab looks broken.

To replace it, drop the new file at the same path and keep the name — the
footer link and `test/interactions.py` both point at `clinic-waiver.pdf`.

Note the legal entity on the form is "Just Soccer FC LLC" while the site trades
as "Just Soccer Futsal Center". That is presumably correct, but worth a glance.

## Running the tests

```bash
py -3 test/interactions.py
```

Eighty-seven assertions across desktop and phone: that the multiplane camera actually
scales, that the statement lights up, that the mobile menu opens and closes and
restores body scroll, that nothing overflows sideways unclipped, that every
in-page link resolves, that the real contact details are still on the page, and
that no invented content or British spelling has crept in. Needs Chrome and
`playwright`; start `node serve.js` first.

## What came from the Soap project, and what didn't

Worth recording, since this folder started empty.

**Nothing had to be reinstalled.** Skills (`higgsfield-*`, `webapp-testing`,
`motion-design`), MCP connectors, and the global `~/.claude/CLAUDE.md` notes are
user-level and apply in every folder automatically.

**Copied from `../Soap` and kept:** `serve.js`, `tools/add-clip.sh`,
`.claude/launch.json`, `.gitignore`, `.nojekyll`, `robots.txt`, and the
structural half of `assets/css/site.css` + `assets/js/site.js` — the reset, type
scale, button wipe, reveal system, preloader, sticky nav and burger, the
statement word-lighting, the parallax, and the single rAF scroll loop everything
is batched through.

**Rewritten for this project:** the entire `:root` palette and type stack, every
section's styles and markup, and the video modules — which were replaced by the
scroll-zoom module, since this site has photographs where Soap had clips.

So: infrastructure and interaction machinery carry over; theme and content do
not. Copying the seven files above is the whole of the setup step.

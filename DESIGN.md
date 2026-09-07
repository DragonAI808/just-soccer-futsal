# DESIGN.md — Just Soccer Futsal Center

Reverse-engineered from the shipped build, not invented for it. Every token below
is live in `assets/css/site.css`; this file is the readable version of it.

**The identity is not ours to choose.** Both brand colors are read off the pixels
of the club badge (`assets/img/logo-source.png`), not picked. Royal `#0039A5` and orange
`#EF6C00` are the modal saturated colors in that file — 10,173 and 8,125 pixels
respectively. The badge is spray-paint and halftone dots, so the page carries that
texture too. A "bolder" or more "distinctive" palette would make this a worse site,
because the job is to look like the club.

---

## 1. Visual Theme & Atmosphere

**One line:** A lit hard court — royal blue, orange, chalk lines and halftone dots,
with type that behaves like a scoreboard.

| | |
|---|---|
| Philosophy | Sports-facility utility, not sports-brand bombast. It answers "what runs here and when," fast. |
| Atmosphere keywords | Floodlit, royal blue, spray-painted, hard-edged, kinetic |
| Tone | Confident, plain-spoken, US English, zero hype |
| Interaction tier | **L2** — scroll reveal, scroll-driven zoom, nav state change, parallax. Deliberately **not L3**. |

### Where the visual grammar comes from

The badge is built from two things, and so is the page:

- **Halftone dot fields** — `.halftone`, two offset radial-gradient dot grids at
  different scales, always masked so they fade out. A flat, unmasked dot field
  reads as a bug rather than a texture.
- **Painted court markings** — `.touchline`, a 3px chalk rule with the halfway
  circle notched into it, used to separate sections. Plus `.hero__court`, the
  hero's mid plane: three drawn circles sitting behind the headline the way the
  badge's ring sits behind the ball.
- **Netting** — `.hero__net`, a diamond mesh from two crossed
  `repeating-linear-gradient`s, masked to fade upward. It is the hero's nearest
  plane because every photograph of this building is shot through the net.

Both are pure CSS. No images, no requests, no libraries.

### Why not L3

The audience is parents and adult league players checking hours and booking a
court, usually on a phone, often on cellular, always in a hurry. A WebGL signature
scene would cost seconds of load to impress nobody who came to find out whether
the court is open at 7pm. Spectacle is a cost the visitor pays and the business
doesn't recover. **This is a considered refusal, not an omission** — the web-design
skill mandates three spectacle moments and a 3D scene for L2+ pages, and that
guidance was rejected on purpose for this brief.

---

## 2. Color Palette & Roles

RGB triplets sit alongside each hex so `rgba()` composes from the token rather
than re-typing channel values. Before that, the scrims and hairlines were
seventeen magic numbers that no longer tracked the palette.

```css
:root{
  /* brand — modal colors sampled from logo-source.png */
  --royal:      #0039A5;  --royal-rgb:      0, 57,165;   /* the badge blue */
  --royal-dp:   #012A78;  --royal-dp-rgb:   1, 42,120;
  --royal-lt:   #2B62D4;  --royal-lt-rgb:  43, 98,212;
  --orange:     #EF6C00;  --orange-rgb:   239,108,  0;   /* the badge orange */
  --orange-ink: #C25400;  --orange-ink-rgb:194, 84,  0;  /* orange as TEXT on white */
  --orange-lt:  #FF9A4A;  --orange-lt-rgb:255,154, 74;   /* large text on royal only */

  --paper:      #FFFFFF;  --paper-rgb:    255,255,255;
  --chalk:      #EDF2FB;  --chalk-rgb:    237,242,251;
  --ink:        #061634;  --ink-rgb:        6, 22, 52;
  --ink-soft:   #46557A;
  --board:      #07101F;  --board-rgb:      7, 16, 31;   /* scoreboard ground */

  --line:      rgba(var(--ink-rgb),.14);
  --line-lt:   rgba(var(--chalk-rgb),.24);
  --chalkline: rgba(var(--paper-rgb),.85);
}
```

### Roles

| Role | Token | Notes |
|---|---|---|
| Page ground | `--paper` | White; `--chalk` sections break it up |
| Inverted ground | `--royal` | Futsal explainer, visit card, stuck nav |
| Deepest ground | `--royal-dp` | Footer, preloader, photo scrims |
| Scoreboard ground | `--board` | The one near-black surface on the site |
| Primary action | `--orange` | Button grounds, numerals, jersey digits |
| Orange as text on white | `--orange-ink` | Eyebrows, inline links |
| Orange on royal | `--orange-lt` | Large text only |

### Contrast — this drove a real design decision

Measured, not assumed:

| Pair | Ratio | Verdict |
|---|---|---|
| `--royal` ⇄ white | **9.87** | Passes both directions |
| `--orange` + white text | 3.08 | **Fails** at button-label size |
| `--orange` + `--ink` text | **5.51** | Passes |
| `--orange-ink` on white | 4.60 | Passes |
| `--orange-lt` on `--royal` | 4.26 | Large text only |

So **buttons take dark ink on orange, not white**. That is an accessibility
requirement first, but it also reads as jersey lettering — which is where the
whole palette came from. Never put white text on `--orange`, and never
`--orange-lt` on white.

---

## 3. Typography Rules

```css
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow:wght@400;500;600;700&display=swap');

--display: "Anton", "Haettenschweiler", "Arial Narrow", sans-serif;
--sans:    "Barlow", "Jost", "Avenir Next", "Segoe UI", system-ui, sans-serif;
```

Anton is a condensed grotesque that reads as jersey lettering and scoreboard —
the entire sports signal, carried by one font. Barlow is its natural companion.

| Level | Family | Size | Weight | LH | Tracking |
|---|---|---|---|---|---|
| Hero H1 | display | `clamp(2.4rem, .5rem + 6.5vw, 9rem)` | 400 | .90 | .006em |
| H2 | display | `clamp(2.2rem, 1.1rem + 4.1vw, 4.4rem)` | 400 | .94 | .005em |
| H3 | display | `clamp(1.35rem, 1.1rem + .9vw, 1.9rem)` | 400 | 1.02 | .01em |
| Statement | display | `clamp(1.7rem, .9rem + 3.3vw, 3.4rem)` | 400 | 1.08 | — |
| Board numeral | display | `clamp(1.4rem, 1rem + 1.5vw, 2.2rem)` | 400 | 1 | .02em |
| Jersey numeral | display | `clamp(2.6rem, 2rem + 1.8vw, 3.8rem)` | 400 | .82 | — |
| Lede | sans | `clamp(1.05rem, .98rem + .4vw, 1.25rem)` | 400 | 1.6 | — |
| Body | sans | `clamp(1rem, .94rem + .28vw, 1.075rem)` | 400 | 1.6 | — |
| Eyebrow | sans | .72rem | 700 | — | .26em |
| Button | sans | .78rem | 700 | — | .16em |

The hero cap came **down** from 9.5rem to 5.6rem: at the larger size it filled the
frame and crowded the photograph it was supposed to sit on.

Board numerals carry `font-variant-numeric: tabular-nums` so the times align in a
column like a real board.

**Forbidden:** Inter, Roboto, Arial, Helvetica, Montserrat, Poppins, or system-ui
as a *primary*. Also any script, rounded or "friendly" face — this is a sports
facility, even though children play here.

**No gradient or shadow on any heading.** Anton at these sizes on flat brand color
is already the loudest thing on the page.

---

## 4. Component Stylings

### Buttons — all five states

```css
.btn{
  padding:.95rem 1.9rem;                     /* ≥44px tall at every size */
  border:3px solid var(--orange);
  background:var(--orange); color:var(--ink);   /* ink, not white — see Contrast */
  font:700 .78rem var(--sans); letter-spacing:.16em; text-transform:uppercase;
  position:relative; overflow:hidden; isolation:isolate;
}
.btn::after{ /* royal wipe, left→right */
  content:''; position:absolute; inset:0; z-index:-1; background:var(--royal);
  transform:scaleX(0); transform-origin:left;
  transition:transform .42s var(--ease-io);
}
.btn:hover::after, .btn:focus-visible::after{ transform:scaleX(1); }
.btn:hover, .btn:focus-visible{ color:var(--paper); border-color:var(--royal); }
.btn:active{ transform:translateY(1px) scale(.994); }
.btn:focus-visible{ outline:3px solid var(--orange); outline-offset:3px; }
.btn[disabled]{ opacity:.45; pointer-events:none; }
```

`:active` is not optional. The wipe is a hover affordance and never fires on
touch — without a pressed state a tap gave no feedback at all on the devices this
audience actually uses.

### The badge

`assets/img/logo-source.png` is 1298×1212 **with a real alpha channel**, so the
badge sits directly on any ground — no chip, no plate, no knockout. Its lettering
is blue with a white outline, which is why it holds on both the royal grounds and
the white ones.

Two derived sizes, both lossy WebP with alpha:

| File | Used by |
|---|---|
| `logo-720.webp` (208 KB) | preloader, story section |
| `logo-260.webp` (48 KB) | nav mark, footer |

**Encode lossy, not lossless.** The halftone dots and spray spatter are
effectively photographic noise: lossless WebP took the 900px version to 816 KB,
lossy at q82 gives 208 KB with no visible loss. `libwebp` keeps the alpha channel
either way.

An earlier build wrapped the badge in a white circular chip, because the only
copy available then was a full-colour mark on an opaque white ground — keying
that white out would have taken the ball's own white panels with it and left a
hollow outline. The chip is gone.

### Scoreboard (`.board__panel`)

The most-asked question at a futsal centre is "is it open and what's on," so it
gets the most on-theme container in the building. Near-black ground, a 6px
dot-matrix wash at 6% opacity, chalk rules top and bottom, amber numerals, and a
pulsing indicator. It is a `<dl>` — label/value pairs, which is what a board is.

### Jersey numerals (`.prog__no`)

Outlined via `-webkit-text-stroke: 2px var(--orange)`, filling solid on row hover,
the way a squad number is printed on a shirt back. `@supports not` fallback fills
them solid where text-stroke is unsupported.

### The story triptych (`.split`)

Photograph, text, photograph — `1fr 1.5fr 1fr`. The two source shots are
different shapes (654×715 and 451×744) and **neither is cropped in the file**:
both sit in a shared box and `object-fit: cover` does the cropping, so they read
as a matched pair and stay matched if either is swapped for a photo of any shape.

The sizing rule is the fiddly part, and it differs by breakpoint on purpose:

| Width | Figure sizing | Why |
|---|---|---|
| ≥881px | `aspect-ratio: auto` + `align-self: stretch` | The text column is the tall one (838px vs the 544px a 3:4 box gives). Stretching makes both pictures exactly the text's height, at any copy length. |
| ≤880px | `aspect-ratio: 3/4` + `align-self: start` | Pictures share a row above the text. Stretch here would resolve *height* first and derive a width from the ratio, leaving each picture narrower than its own column. |
| ≤520px | single column, `aspect-ratio: 4/3` | Both pictures, full width, bracketing the copy the way they do on the triptych. Side by side at this size they land ~170px each and neither reads. |

That interaction — `aspect-ratio` plus `align-self: stretch` means height wins
and width is derived — is the thing to remember if this layout is ever reworked.

### Cards

All **square-cornered**. No border radius anywhere except the court circles and
the badge's own artwork. Court markings are straight lines; the geometry follows.

---

## 5. Layout Principles

```css
--pad:  clamp(1.25rem, 5vw, 5.5rem);   /* every section's horizontal gutter */
--maxw: 1440px;
--navh: 3.35rem;
```

One gutter token, used everywhere; sections never invent their own. Vertical
rhythm is `clamp(4rem, 11vh, 8rem)`. Full-bleed bands (hero, arena) escape
`--maxw`; their content does not. Measure: 56ch ledes, 52ch body, 19ch statement.
Anchor targets carry `scroll-margin-top: 4.5rem` to clear the fixed nav.

**Page order is deliberate:** hero → scoreboard → statement → what futsal is →
programs → arena → story → visit. The scoreboard is second because the hours are
what most visitors came for.

---

## 6. Depth & Elevation

Effectively flat, and that is a decision. **No drop shadows anywhere.** Depth
comes from ground changes (paper → chalk → royal → royal-dp → board) and from
photographic scrims.

| Level | Use | Implementation |
|---|---|---|
| 0 | Everything | flat |
| 1 | Stuck nav | `box-shadow: 0 3px 0 rgba(orange,.95)` — an orange touchline, not a shadow |
| 2 | Hero / arena photography | layered gradient scrims inside `isolation:isolate` |

---

## 7. Animation & Interaction — L2

**Dependencies: none.** No GSAP, Lenis, ScrollTrigger or Motion. CSS transitions
plus one `requestAnimationFrame` loop; ~230 lines of JS total. Every scroll reader
is batched into a single rAF so there is one layout read per frame.

### The multiplane camera — the hero's signature move

The hero sits in a **250svh rail** with a `position: sticky` pane inside it. The
camera runs over the *sticky travel* — rail height minus the pinned pane, about
1.5 screens — so the whole move completes while the frame is still pinned.

This is native sticky, not scroll-jacking: scroll velocity, momentum and the
scrollbar are untouched. The cost is that the scoreboard sits ~1.5 screens lower,
which is why **Hours** is the first item in the nav.

Planes travel on an **arc**, not a ramp: `Math.sin(p * Math.PI)` is 0 at rest,
peaks halfway, and returns to 0. The frame opens on the whole photograph, the
camera pushes in to the centre-circle ball graphic, and pulls back out before the
page moves on. A monotonic ramp left the image at maximum magnification exactly
when you scrolled past it, which read as a blur rather than as a move.

| Plane | `data-cam-y` | `data-cam-scale` | `data-cam-fade` | arc? |
|---|---|---|---|---|
| `.hero__frame` — the photograph (far) | -4% | +0.52 | — | yes |
| `.hero__court` — painted markings (mid) | -15% | +0.92 | 0.6 | yes |
| `.hero__net` — the netting (near) | -38% | +1.75 | 0.9 | yes |
| `.hero__inner` — the copy | -7% | 0 | 1.25 | **no** |

The copy is deliberately off the arc: it has to leave and stay gone.

`.hero__frame` overrides the shared `transform-origin` to **54% 74%** — the
centre-circle ball graphic in the framed photograph — so the push converges on
that rather than on the middle of the frame.

### Phones get a shallower push

`.hero-rail` drops to **160svh** below 700px and `site.js` halves every camera
value at the same breakpoint (`camGain()`), giving a peak of ~1.26 instead of
1.52. Two measured reasons, not taste:

- The phone crop is capped at **1180×1414** — the full height of the source
  photograph. A 1.52 push there would upscale into mush.
- 2.6 screens of pinned scroll before the first fact is a lot of thumb. At
  160svh the scoreboard is 1.7 screens down instead of 2.6.

That spread is the whole effect — the far wall barely shifts while the netting
in front of the lens sweeps past. The near plane is netting because **every
photograph of this building is shot through the net**; the foreground is
observed, not invented.

Four rules are load-bearing:

1. Transforms go on **planes**, never on `.hero`. Scaling the section widens the
   document and pushes out a horizontal scrollbar.
2. Progress divides by **sticky travel**, not rail height. A 250svh rail holding
   a 100svh pane unsticks at p=0.40, so dividing by the rail put the peak after
   the hero had already begun to leave.
3. Progress is read **once**, off the rail. Reading each plane's own rect feeds
   the transform just written back in as the next frame's input.
4. Planes bleed only as far as their own travel (-5%/-10%). An earlier -12% made
   the photograph 24% larger than the frame before any scroll at all, so the
   hero never once showed the whole image.

Tune it from the `data-cam-*` attributes; nothing in CSS or JS needs touching.
**Keep near > mid > far.** Parallax exists only because the planes disagree —
flatten them and the depth vanishes while everything still appears to work.
`test/interactions.py` asserts the ordering, the pinning at peak, and the return
to rest for exactly that reason.

One JS gotcha worth remembering: `data-cam-arc` is a valueless attribute, so
`el.dataset.camArc` reads back as the **empty string**, which is falsy. Testing it
for truthiness silently left every plane on the linear ramp. The check is
`'camArc' in el.dataset`.

### Arena band

`.arena__media` still uses the simpler `data-zoom="out"` module, easing 1.24 → 1
as the band arrives — the opposite move to the hero, so the two never read as the
same trick twice. Its progress is read from `.js-zoomframe` via `closest()`,
**not** `parentElement`: the image's parent is `<picture>`, and
`picture{display:contents}` generates no box, so its rect is all zeros.

Also: statement words light one at a time; section headings rise out of a mask;
body blocks fade up 1.6rem; the story image parallaxes at 0.06.

### The heading mask — read before touching it

The mask goes on a JS-injected `.h2__in` span, **never on the `<h2>`**. `clip-path`
is folded into IntersectionObserver's intersection rect, so a fully clipped `<h2>`
reports `intersectionRatio: 0` — and the very observer that would add `.is-in` and
un-clip it can then never fire. The heading hides itself permanently with nothing
in the console. Both halves are asserted in `test/interactions.py`.

### Reduced motion

Complete removal, not shortening — none of the motion carries meaning. Transitions
and animations collapse to `.001ms`; reveals, masks, zooms, the ticker and the
board pulse are all disabled, and `paintZoom()`/`paintParallax()` return early in
JS so no transform is ever written.

---

## 8. Do's and Don'ts

### Do

1. Take color from the badge. Both brand colors are sampled from `logo-source.png`.
2. Compose translucency from `--*-rgb` tokens, never fresh channel numbers.
3. Keep square corners. Court lines are straight.
4. Put dark ink on orange; use `--orange-ink` for orange text on white.
5. Give every interactive element all five states.
6. Let ground changes carry depth instead of shadows.
7. Mask every halftone field so it fades out.
8. Write "call for the current schedule" when the schedule isn't known.

### Don't

1. **Don't invent facts.** No prices, testimonials, class times, coach bios or
   founding year exist here because none were supplied. The suite fails on `$`
   or "testimonial".
2. **Don't add a WebGL/3D signature scene.** See §1.
3. **Don't introduce scroll-jacking** (Lenis, smooth-scroll libraries).
4. **Don't round the corners.**
5. **Don't gradient-fill or shadow the headings.**
6. **Don't put white text on `--orange`** — 3.08:1, fails.
7. **Don't blur moving elements.** No `filter:blur()` on anything that transforms.
8. **Don't hardcode a hex or rgba channel** outside `:root`.
9. **Don't transform a full-bleed clipping frame** — transform its child image.
10. **Don't clip the observed element** in a reveal. Clip an injected child.
11. **Don't repeat the hours** outside the scoreboard and the JSON-LD. They were in
    three places and had three chances to drift.
12. **Don't switch to British English.** The suite fails on "colour", "centre",
    "enquiries", "programme".

---

## 9. Responsive Behavior

| Breakpoint | Change |
|---|---|
| `≤ 700px` | Hero swaps to an art-directed **portrait crop**, not a squeezed landscape. H1 drops to `max-width:12ch`; the centre circle narrows. |
| `≤ 760px` | Program ledger 3 → 2 columns; timing moves under the description, left-aligned. Footer 3 → 2 columns. |
| `≤ 880px` | Split and visit stack to one column. |
| `≤ 900px` | Nav collapses to a burger; links become a full-screen royal overlay; body scroll locks while open and is restored on close. |

- Touch targets ≥ 44×44px throughout (buttons ~46px, burger 2.75rem, social 2.75rem).
- No horizontal overflow at any width — the suite walks every element and fails on
  any that overflows without a clipping ancestor.
- `100svh` on the hero so mobile browser chrome doesn't crop the CTAs.
- Images ship WebP with JPEG fallback at 1200/1600/2400 widths.

---

## Known state

**The photography is now theirs.** Every image on the page comes from Just Soccer's
own Squarespace CDN: the hero and social card from `Futsal 4.jpg` (2500px, kids
training on the real centre-circle ball graphic), the arena band and the story crop
from `Futsal wide angle pics-126.jpg` (1291px, the hall with its flags of many
nations). The Czech stock placeholders are gone.

Two resolution ceilings to know about:

- The wide-angle of the hall is **1291px** native — the largest their CDN holds.
  It covers a 1440px band with a mild upscale, and the arena scrim is heavy enough
  to hide it. Do not push that image into a full-height hero.
- The badge is **1298x1212 with alpha** and is no longer a constraint. Only a
  vector would beat it, and only for print.

If higher-resolution originals exist on a phone or a hard drive somewhere, they
are a drop-in replacement — same filenames, same crops, no code change.
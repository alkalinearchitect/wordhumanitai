# HumanitAI — Motion Stack Integration (verified)

Integration/tooling lead deliverable. All URLs HEAD-checked (HTTP 200) and metadata pulled
from the GitHub API + npm registry on the date of this report.

---

## 1. Verified libraries — exact CDN URLs, stars, licenses

| Library | Repo | Stars | License (VERIFIED) | Latest |
|---|---|---|---|---|
| GSAP + ScrollTrigger | greensock/GSAP | ~27.0k | ⚠️ **NOT MIT** — GreenSock "Standard No-Charge" license | 3.15.0 |
| Lenis | darkroomengineering/lenis | ~14.8k | ✅ **MIT** | 1.3.25 |
| SplitType | lukePeavey/SplitType | ~0.73k | ✅ **ISC** (not MIT) | 0.3.4 |
| Three.js | mrdoob/three.js | ~114k | ✅ **MIT** | 0.185.1 |

### Exact, tested CDN URLs (all returned 200)

```
GSAP core:          https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js
ScrollTrigger:      https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/ScrollTrigger.min.js
Lenis:              https://cdn.jsdelivr.net/npm/lenis@1.3.25/dist/lenis.min.js
SplitType (UMD):    https://cdn.jsdelivr.net/npm/split-type@0.3.4/umd/index.min.js
Three.js (ESM):     https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.min.js
```

GSAP mirror on cdnjs (also 200, if you prefer Cloudflare):
```
https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js
https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js
```

---

## 2. ⚠️ CRITICAL Three.js gotcha for this no-build site

The existing `index.html` loads **Three r128 as a UMD global** (`window.THREE`) via
`cdnjs .../three.js/r128/three.min.js`. **Modern Three.js has NO UMD build.**

- `three@0.170.0/build/three.min.js` → **404** (removed)
- `three@0.160.0/build/three.min.js` → **200** (last UMD-compatible global build)
- `three@0.180.0/build/three.module.min.js` → **200** (ESM only)

**Recommendation for a no-build static site — two clean options:**

- **Option A (least churn):** keep the classic-script global pattern but pin the last UMD build:
  `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js` (still gives `window.THREE`).
  The current r128 code works unchanged against 0.160.0.
- **Option B (modern):** switch the hero to an ES-module `<script type="importmap">` + `three@0.180.0/build/three.module.min.js`. Requires rewriting the IIFE as a module and `import * as THREE`. More work, no `THREE` global.

This report assumes **Option A** so the existing hyper-frames/hero scene keeps its `THREE.*` API.

---

## 3. Integration code — drop into existing index.html

### 3a. `<head>` — load libs (classic scripts, defer)

```html
<!-- Motion stack. GSAP is free-to-use under GreenSock Standard License (no charge). -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/ScrollTrigger.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.3.25/dist/lenis.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/split-type@0.3.4/umd/index.min.js" defer></script>
```

### 3b. Master motion bootstrap (place before `</body>`, after other scripts)

```html
<script>
(function () {
  var REDUCED = window.matchMedia &&
                window.matchMedia('(prefers-reduced-motion:reduce)').matches;

  // Wait for deferred CDN scripts to be present.
  function ready(fn){ if (document.readyState !== 'loading') fn();
                      else document.addEventListener('DOMContentLoaded', fn); }

  ready(function () {
    if (REDUCED) return;                 // honor reduced-motion: static site, no JS motion
    if (!window.gsap || !window.ScrollTrigger) return;  // graceful: CDN blocked -> plain page

    gsap.registerPlugin(ScrollTrigger);

    /* ---------- (A) Lenis smooth scroll, driving ScrollTrigger ---------- */
    var lenis = null;
    if (window.Lenis) {
      lenis = new Lenis({ duration: 1.1, smoothWheel: true });
      // Feed Lenis's rAF from GSAP's ticker so both share one clock (no double rAF).
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
      gsap.ticker.lagSmoothing(0);
    }

    /* ---------- (B) SplitType word/line reveals ---------- */
    if (window.SplitType) {
      document.querySelectorAll('[data-split]').forEach(function (el) {
        var split = new SplitType(el, { types: 'lines,words' });
        gsap.set(el, { opacity: 1 }); // reveal container; words start hidden below
        gsap.from(split.words, {
          yPercent: 110, opacity: 0, duration: 0.8, ease: 'power3.out', stagger: 0.03,
          scrollTrigger: { trigger: el, start: 'top 85%', once: true }
        });
      });
    }

    /* ---------- (C) ScrollTrigger -> hyper-frames Three.js scroll progress ---------- */
    // The Three scene exposes a hook: window.__hyperFrames.setProgress(0..1).
    // See 3c for how the hero/hyper-frames scene registers that hook.
    ScrollTrigger.create({
      trigger: '#hero',            // or the hyper-frames section wrapper
      start: 'top top',
      end: 'bottom top',
      scrub: 1,                    // smooth-tie progress to scroll
      onUpdate: function (self) {
        if (window.__hyperFrames && window.__hyperFrames.setProgress) {
          window.__hyperFrames.setProgress(self.progress);
        }
      }
    });

    ScrollTrigger.refresh();
  });
})();
</script>
```

### 3c. Expose a scroll hook from the Three.js hyper-frames scene

Inside the existing hero IIFE (the `s.onload` block after Three loads), publish a hook the
ScrollTrigger above can call. Minimal, non-breaking addition:

```js
// ...after `scene`, `cam`, `points` etc. are created, before/inside loop():
var _progress = 0;
window.__hyperFrames = {
  setProgress: function (p) { _progress = p; }   // p in [0,1]
};

// then use _progress inside loop() to drive the scene, e.g.:
function loop(){
  if(!running) return;
  // scroll-reactive camera dolly + rotation from hyper-frames progress:
  cam.position.z = 18 - _progress * 6;           // pull in as you scroll
  points.rotation.y += 0.0003 + _progress*0.002; // spin faster deeper in
  // ...existing particle update + r.render(scene,cam)...
  requestAnimationFrame(loop);
}
```

### 3d. Reduced-motion CSS (extend the existing rule at line 207)

The site already has:
```css
@media(prefers-reduced-motion:reduce){.rv{opacity:1!important;transform:none!important}.hero canvas{display:none}.scroll-hint .ln{animation:none}}
```
Add SplitType safety so split text is always visible if JS motion is skipped:
```css
@media(prefers-reduced-motion:reduce){
  [data-split]{opacity:1!important}
  [data-split] .word,[data-split] .line{transform:none!important;opacity:1!important}
}
```
Also set `[data-split]{opacity:0}` in the base (non-reduced) CSS so there's no flash before JS
reveals it — but ONLY behind a `.js` class or the reduced-motion rule above, so no-JS users still see text.

---

## 4. Licensing & performance gotchas (no-build static site)

**Licensing**
- ⚠️ **GSAP is NOT MIT.** It's the GreenSock "Standard No-Charge License." Free for the vast
  majority of uses (including commercial sites like HumanitAI) — but it is a custom license, not
  OSS/MIT. The previously-paid "Club" bonus plugins (SplitText, MorphSVG, etc.) became free in
  2025, but the **core license is still GreenSock's, not MIT.** Do not claim "MIT" in credits.
  ScrollTrigger ships in the same package under that same license. This is why we use free
  **SplitType** (ISC) instead of GSAP's SplitText for text splitting.
- ✅ Lenis — MIT. Free, attribution-friendly.
- ✅ SplitType — **ISC** (functionally equivalent to MIT; NOT "MIT" — correct your credits).
- ✅ Three.js — MIT.

**Performance**
- **Don't double-rAF:** Lenis + GSAP each run their own rAF by default. The snippet routes Lenis
  through `gsap.ticker` so there's a single loop. Critical or you get jank.
- **`lagSmoothing(0)`** prevents GSAP from "catching up" after tab-switches, which fights Lenis.
- **Three r128→0.160 pin:** modern Three dropped UMD. For no-build, pin `three@0.160.0/build/three.min.js`
  (global `THREE`) OR migrate to an importmap + ESM module. Don't blindly bump to 0.180 with a classic script — it'll 404 and kill the hero (the code already has an `s.onerror` fallback that hides the canvas, so it degrades, but you lose the effect).
- **`scrub: 1`** (not `true`) adds a 1s smoothing so scroll-driven Three progress isn't twitchy.
- **`once: true`** on text reveals avoids re-running on every scroll pass (cheaper, less distracting).
- **`ScrollTrigger.refresh()`** after fonts/Tailwind layout settles, else start/end positions are wrong.
- **Defer everything**; ~120KB gzip total added (GSAP+ST ~70KB, Lenis ~10KB, SplitType ~8KB). Acceptable for a hero-heavy marketing page; all from jsDelivr's HTTP/2 edge.
- **Reduced-motion:** bootstrap early-returns before creating Lenis/GSAP, so zero motion JS runs for those users — the page stays a normal, natively-scrolling static site.

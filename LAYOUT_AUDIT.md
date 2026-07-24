# HumanitAI — Layout & Visual Hierarchy Audit

Scope: composition, section rhythm, hierarchy, whitespace, section contrast,
and "wow" moments only. Copy tone and colour palette are out of scope (other agents).

Source audited: `/opt/data/wordhumanitai_v2/index.html` (single-page static site).

---

## Prioritized weaknesses + fixes

### 1. [Hero is generic and the weakest composed moment]
**Problem:** The hero — the single most important first impression — is a conventional
left-aligned text block on empty bone-paper with only a faint radial teal glow at
76%/42%. There is no signature visual, no tension, no asymmetry; it reads like any
SaaS landing hero rather than a "mind-blowing" opening.
**Why it weakens the design:** The user explicitly wants wow moments, yet the very
first screen is the least distinctive, and the large empty right third (where the
glow floats) is wasted negative space that reads as unbalanced, not intentional.
**Specific fix:** Compose the hero asymmetrically — anchor the headline and let the
teal glow sit *behind/around* it, or balance the dead right side with a signature
element (an oversized live stat pulled from the model, a cropped data motif, or a
vertical city-rank teaser that previews the dark band). Give the opening a repeatable
visual signature so it stops reading as boilerplate.

### 2. [The "dashboard" band under-delivers as a styled table, not a viz]
**Problem:** The dark Intelligence band is the page's only true light→dark contrast,
but its content is a ranked text list with 8px-tall segmented bars and a Fraunces
severity number — it reads as a leaderboard, not a dashboard.
**Why it weakens the design:** The dark band is the best shot at a wow beat, yet the
data viz is the thinnest, smallest element; the eye is pulled to the numeric
leaderboard instead of to insight, so the "dashboard" promise isn't visually met.
**Specific fix:** Make the data the protagonist of that band — give the bars real
scale (taller, or a ranked horizontal bar chart where the city is the axis and
severity is the scale), and increase the visualization's visual weight relative to
the surrounding chrome so the dark section feels like an instrument, not a list.

### 3. [The closing CTA is the quietest section despite being the conversion moment]
**Problem:** "Three ways in." is centered, tinted, uses the same 108px padding, carries
no accent, and shows three near-identical buttons where the primary path isn't
elevated. (The centered kicker's teal tick also sits left of the word, shifting its
visual centre right.)
**Why it weakens the design:** Hierarchy is inverted — the moment that should shout is
whispering, and the reader can't tell Fund / Build / Bring-us-in apart or see a clear
primary action.
**Specific fix:** Promote the CTA to the loudest beat — scale it up (larger type, more
vertical room), give it a distinct accent treatment (a teal/vermillion field or a
full-bleed tint break), and visually elevate the primary action above the two
secondary ones. For centered kickers, centre or suppress the tick so the label is
truly centred.

### 4. [Monotonous section rhythm — every section is weighted identically]
**Problem:** Every section opens with the same 108px vertical padding and a 1px hairline
top border (the hero is the only exception). The emotional core (4th Space), the proof
(Intelligence), and the CTA all get equal weight and the same opener.
**Why it weakens the design:** Uniform cadence reads as a stack of equal modules rather
than a composed narrative with crescendos and intimacy; no section feels more or less
important, so the page has no dramatic shape.
**Specific fix:** Vary rhythm by section role — give 4th Space a more intimate, narrower
measure and tighter pacing; give key moments larger scale and air; replace some
hairline openers with deliberate asymmetric intros or spacing jumps so the page breathes
in a designed, non-uniform way.

### 5. [The 4th Space emotional payload is buried]
**Problem:** The "It helps the area think: …" callouts — the emotional heart of the 4th
Space section — are small inline `<span class="shift">` lines nested inside long body
paragraphs.
**Why it weakens the design:** The most human, memorable lines are visually subordinate
to the explanatory copy, so the section lands as a spec sheet rather than an editorial
feature with feeling.
**Specific fix:** Pull those callouts into their own distinct rhythm — set them as larger
pull-quotes / voice lines with their own typographic treatment and whitespace — so the
section alternates explanation and emotion instead of burying the emotion.

### 6. [Two identical stat groups dilute hierarchy]
**Problem:** The hero shows three Fraunces figures (18 / 0.81 / 14.3M) and 4th Space shows
three more (60 / ~48 / £3.20) in the exact same style — big serif number + uppercase
label.
**Why it weakens the design:** Two groups that mean different things (scale-of-problem vs
impact-delivered) are visually indistinguishable, so a reader can't tell which numbers
are context and which are proof.
**Specific fix:** Differentiate the two groups — e.g., hero figures as quiet, small
context numerals and impact figures as larger, accented proof, or frame them with
different roles/labels so the "how big" vs "what we achieve" hierarchy is clear.

### 7. [Dead negative space on the hero's right side]
**Problem:** Hero text is left-aligned within the 1080px column while the teal radial glow
sits at 76%/42% (right side), leaving the right third as empty ivory with a faint
floating blob.
**Why it weakens the design:** The composition has no counterbalance — the glow implies
something should be there, but nothing is, so the right side reads as unfinished rather
than intentional negative space.
**Specific fix:** Either move the glow to sit behind/around the headline (so it enforces
the type) or place a real element on the right (a live stat, a vertical city-rank strip,
a data motif) that the glow can illuminate and that gives the hero a full-width,
intentional composition.

### 8. [Filter affordance does not match behaviour]
**Problem:** The Intelligence band says "Click any pressure to filter," but selecting a
dimension only dims the other segments and keeps the composite ranking — list order
never changes.
**Why it weakens the design:** The control implies a view change that doesn't happen; the
eye expects re-sorting by the chosen pressure and instead sees the same leaderboard with
muted colours, which reads as a broken or decorative control and erodes trust in the
"dashboard."
**Specific fix:** Make the filter behave as advertised — re-rank the list by the selected
dimension — or relabel the control as "highlight" / "focus" so the affordance matches
what the interaction actually does.

### 9. [Inconsistent text measure across the page]
**Problem:** The lede is capped at 560px, but the 4th Space row bodies run the full
~850px width of the 1fr column (no max-width), so line lengths are inconsistent.
**Why it weakens the design:** Lines well beyond the ~65-character ideal tire the eye and
turn the editorial copy into a wall, undercutting the "light editorial" intent and
making 4th Space feel denser than it should.
**Specific fix:** Constrain body copy to a consistent comfortable measure (~60–70ch /
~640–680px) everywhere, so the lede and the 4th Space bodies share the same readable
rhythm.

### 10. [No connective editorial system ties the page together]
**Problem:** Each section is a centred 1080px column opened by a kicker; there is no
running device (section numbers, a margin rail, a persistent thread) binding the page
into one designed editorial piece.
**Why it weakens the design:** Without a connective system the site reads as separate
stacked blocks rather than one composed argument — which is exactly what keeps it from
feeling "mind-blowing" rather than merely tidy.
**Specific fix:** Introduce a light editorial spine — numbered section markers (01 / 02 /
03), a left/right marginal note, or a persistent thin rail — so the reader always knows
where they are in the narrative and the whole reads as one art-directed document.

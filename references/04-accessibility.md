# Gate 4 - Accessibility (WCAG 2.2 Level AA)

Not optional and not charity - it's a legal exposure, an SEO factor, and roughly 1 in 4 adults. Automated tools catch ~30%; the rest is manual.

## Automated first pass
Run **axe DevTools**, **WAVE**, or Lighthouse's a11y audit on every template. Fix all violations, then do the manual work below.

## Keyboard (do this on every page)
- [ ] Tab through the entire page - everything interactive is reachable
- [ ] **Visible focus indicator** on every focusable element, with ≥3:1 contrast (never `outline: none` without a replacement)
- [ ] Tab order follows visual order
- [ ] No keyboard traps - you can always Tab back out
- [ ] Skip-to-content link present, and it works (Tab once from the top)
- [ ] Modals: focus moves in on open, is trapped while open, returns to the trigger on close, Esc closes
- [ ] Dropdowns/menus operable with Enter, Space, arrows, Esc
- [ ] Custom controls (sliders, toggles, carousels) usable without a mouse
- [ ] Nothing requires hover to reach or dismiss
- [ ] Hidden/offscreen elements aren't focusable (`display:none` or `inert`)

## Screen reader
Test with **VoiceOver** (macOS/iOS: ⌘F5) and ideally NVDA on Windows.
- [ ] Page has a unique, descriptive `<title>`
- [ ] `<html lang="en">` set correctly
- [ ] Landmarks used: `<header> <nav> <main> <footer>` - exactly one `<main>`
- [ ] Heading order is logical: one `<h1>`, no skipped levels; headings describe structure, not styling
- [ ] Every image has a meaningful `alt`; decorative images get `alt=""`
- [ ] Complex images (charts, infographics) have a longer text description nearby
- [ ] Icon-only buttons have accessible names (`aria-label` or visually-hidden text)
- [ ] Link text makes sense out of context ("View pricing," not "click here")
- [ ] Dynamic content changes are announced (`aria-live` for toasts, errors, cart updates)
- [ ] ARIA used correctly and sparingly - native HTML first; no `role` that contradicts the element
- [ ] Lists marked up as lists; tables use `<th>`, `scope`, and a `<caption>` where useful
- [ ] Nothing announces as "unlabeled button/link/frame"; iframes have `title`

## Color & contrast
- [ ] Body text ≥ **4.5:1**; large text (18.66px bold / 24px) ≥ **3:1**
- [ ] UI components, icons, borders, and focus rings ≥ **3:1**
- [ ] Check text over images/gradients at its worst point - this is the most-missed failure
- [ ] Color is never the only way information is conveyed (errors, status, charts, links in body copy)
- [ ] Links within body text are distinguishable without color alone (underline)
- [ ] Placeholder text meets contrast (and isn't doing a label's job)
- [ ] Check in dark mode too
- [ ] Disabled states: still legible enough to read

## Motion, media & timing
- [ ] `prefers-reduced-motion` respected
- [ ] Nothing flashes more than 3×/second
- [ ] Auto-playing carousels/video can be paused; no autoplay with sound
- [ ] Video has captions; audio has a transcript
- [ ] No content on a timer the user can't extend (session timeouts, alerts)

## Targets & input (WCAG 2.2 additions)
- [ ] Tap/click targets ≥ 24×24px minimum (44×44px recommended), with spacing
- [ ] Drag actions have a single-pointer alternative
- [ ] Focus is never fully hidden behind a sticky header/footer
- [ ] No cognitive test to log in that lacks an alternative (accessible authentication)
- [ ] Info the user already entered is not re-requested unnecessarily (redundant entry)
- [ ] Help mechanisms appear in a consistent place across pages

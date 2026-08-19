# Gate 3 — Responsive, Cross-Browser & Cross-Device

## Viewport matrix (test in this order if mobile-dominant)
| Width | Represents | Priority |
|---|---|---|
| 320px | iPhone SE / small Android | Check it doesn't break |
| **375px** | iPhone mini/standard | **Primary — test first** |
| 390–430px | iPhone 14–16 / Pro Max | Primary |
| 412px | Pixel / Galaxy | Primary |
| 768px | iPad portrait | Secondary |
| 1024px | iPad landscape / small laptop | Secondary |
| 1280px | Standard desktop | Primary desktop |
| 1440–1920px | Large desktop | Check for over-stretch |
| 2560px+ | Ultrawide | Content shouldn't span the full width |

## Layout integrity at every breakpoint
- [ ] **No horizontal scroll.** Anywhere. (Common culprits: fixed widths, `100vw` with a scrollbar, oversized images, long unbroken strings, negative margins, absolutely positioned decor)
- [ ] Nothing overlaps, clips, or overflows its container
- [ ] No text touching screen edges — consistent gutters
- [ ] Nothing important cut off at the fold; the primary CTA is reachable without hunting
- [ ] Images scale and keep aspect ratio; no squashing or unwanted cropping of faces/text
- [ ] Tables scroll or reflow on mobile rather than blowing out the page
- [ ] Grids reflow sensibly (no orphaned single item in a 3-col grid looking broken)
- [ ] Modals, menus, and sticky elements fit the small viewport with keyboard open
- [ ] Between breakpoints — drag the window slowly; awkward mid-range states are where sites break
- [ ] Landscape orientation on phone works (especially heroes with `100vh`)
- [ ] Safe-area insets respected on notched devices (`env(safe-area-inset-*)`)
- [ ] `100vh` on mobile doesn't jump with the browser chrome — prefer `dvh`/`svh`

## Typography & spacing
- [ ] Font sizes readable on mobile — body ≥ 16px; no accidental 11px legal text
- [ ] Line length ~45–75 characters on desktop
- [ ] Headings don't produce ugly single-word orphans (use `text-wrap: balance` on headings, `pretty` on body)
- [ ] Vertical rhythm and section spacing consistent across pages
- [ ] Buttons don't wrap their label awkwardly at any width

## Browsers
- [ ] **Safari (macOS + iOS)** — the one that breaks. Check flexbox gaps, `backdrop-filter`, date inputs, video, sticky, and 100vh
- [ ] Chrome (desktop + Android)
- [ ] Firefox
- [ ] Edge (if B2B/enterprise audience)
- [ ] Samsung Internet (meaningful Android share)
- [ ] In-app browsers: **Instagram, Facebook, TikTok, LinkedIn** — if traffic comes from social, test there; they break video, cookies, and downloads
- [ ] One older-version check if analytics show a meaningful tail

## Device & environment conditions
- [ ] Real device, not just devtools emulation — touch, scroll momentum, and fonts differ
- [ ] Dark mode: page respects or deliberately overrides `prefers-color-scheme`; no invisible text
- [ ] Browser zoom to 200% — layout must remain usable (WCAG requirement)
- [ ] Text-only zoom / large system font doesn't break the layout
- [ ] Slow 3G / throttled connection — does it still render usefully?
- [ ] Offline or flaky connection doesn't produce a blank white page
- [ ] `prefers-reduced-motion` honored — animations reduce or stop
- [ ] Retina/2x displays: images aren't blurry; logos ideally SVG
- [ ] Print stylesheet if the page is likely printed (menus, tickets, invoices, résumés)

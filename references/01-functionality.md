# Gate 1 — Functionality & Links

## Navigation
- [ ] Every nav item goes where its label promises — click each one, don't read the `href`
- [ ] Logo links to home from every page (and is not a dead link on home itself)
- [ ] Mobile menu: opens, closes, closes on selection, closes on outside tap / Esc
- [ ] Menu doesn't trap scroll; body scroll locks while open and unlocks after
- [ ] Dropdowns/megamenus work on **touch** (hover-only menus are broken on mobile)
- [ ] Sticky header doesn't cover content when jumping to an anchor (`scroll-margin-top`)
- [ ] Footer links all resolve — footers are where dead links go to hide
- [ ] Breadcrumbs match actual hierarchy
- [ ] Active/current page state is correct in nav
- [ ] Back button behaves after modals, filters, and tabs (no dead-end states)

## Links
- [ ] Zero broken internal links (scanner + manual spot-check)
- [ ] Zero broken external links — check each one loads and is still the intended page
- [ ] All anchor links (`#section`) resolve to an element that exists
- [ ] External links open in a new tab **only where intended**, and always with `rel="noopener noreferrer"`
- [ ] No `localhost`, `127.0.0.1`, staging domains, `file://`, or preview URLs in production
- [ ] `mailto:` and `tel:` links use the correct, current address/number and actually launch the app
- [ ] Links to PDFs/downloads work, and the file is the right (current) version
- [ ] No link text reading "click here" / bare URLs (a11y + SEO)
- [ ] Redirects resolve in one hop where possible; no redirect chains or loops

## Interactive elements
- [ ] Every button does something; no no-op buttons left in
- [ ] Accordions, tabs, carousels, modals, tooltips: open, close, and cycle correctly
- [ ] Carousels: swipeable on touch, arrows work, autoplay pausable, no infinite-loop jank
- [ ] Modals: close via X, Esc, and backdrop click; focus moves in and returns out
- [ ] Video/audio: plays, controls work, doesn't autoplay with sound, has a poster frame
- [ ] Embeds (maps, calendars, booking, YouTube, Spotify) load and are responsive
- [ ] Filters/search/sort return correct results, including the empty-result state
- [ ] Pagination / "load more" / infinite scroll works to the last item
- [ ] Copy-to-clipboard, share, and print actions do what they say
- [ ] Any counters, timers, or countdowns show correct values and time zone

## States & edge cases
- [ ] Loading states exist for anything async (no silent dead time)
- [ ] Empty states are designed, not blank
- [ ] Error states are handled and human-readable
- [ ] 404 page exists, is branded, and offers a route back (test a junk URL)
- [ ] 500/offline behavior doesn't show a raw stack trace
- [ ] Long content doesn't break layout (paste a 200-char string into headings/names)
- [ ] Behavior with JS disabled or slow — does critical content still render?
- [ ] Double-click / rapid-tap on submit doesn't double-fire

## Cross-page
- [ ] Every page in the sitemap is reachable from navigation or an internal link
- [ ] No orphan pages, no leftover test/draft pages published
- [ ] Consistent header/footer/nav across all pages
- [ ] URL structure is clean, lowercase, hyphenated, no query junk
- [ ] Trailing-slash behavior is consistent

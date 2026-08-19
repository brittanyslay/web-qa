# Gate 7 — SEO, Metadata & Social Sharing

## The launch-day catastrophe check (do this first, twice)
- [ ] **`robots.txt` does not disallow the site.** Visit `/robots.txt` on production.
- [ ] **No `<meta name="robots" content="noindex">` on production pages.** Staging blockers get shipped constantly.
- [ ] No `X-Robots-Tag: noindex` response header
- [ ] Staging/dev environment IS blocked from indexing (and password-protected if possible)
- [ ] Site is verified in Google Search Console; sitemap submitted

## Per-page metadata
- [ ] Unique `<title>` on every page, ~50–60 characters, keyword first, brand last
- [ ] Unique meta description, ~140–160 characters, written to earn the click (not keyword stuffing)
- [ ] Exactly one `<h1>` per page, and it matches the page's actual subject
- [ ] Heading hierarchy logical (h1 → h2 → h3, no skips)
- [ ] `<link rel="canonical">` on every page, self-referencing and absolute
- [ ] `<html lang>` set; `hreflang` if multilingual
- [ ] URLs are readable, lowercase, hyphenated, and stable

## Structured data
- [ ] Schema.org JSON-LD appropriate to the site: `Organization` / `LocalBusiness` / `Person`, plus `Event`, `Product`, `Article`, `FAQPage`, `BreadcrumbList` as relevant
- [ ] Validated in Google's Rich Results Test — zero errors
- [ ] `LocalBusiness` NAP (name, address, phone) matches Google Business Profile **exactly**
- [ ] No schema describing content that isn't visible on the page

## Social sharing (test with real scrapers)
- [ ] `og:title`, `og:description`, `og:image`, `og:url`, `og:type`, `og:site_name`
- [ ] `og:image` is absolute URL, ~1200×630, < 5 MB, and has text-safe margins
- [ ] `twitter:card` (`summary_large_image`), `twitter:title`, `twitter:description`, `twitter:image`
- [ ] Preview validated in **Facebook Sharing Debugger**, **LinkedIn Post Inspector**, and by pasting the link into iMessage/Slack/WhatsApp
- [ ] Re-scrape after any change — caches are sticky
- [ ] Each key page (home, services, events, blog posts) has its own share image where it matters

## Favicons & app icons
- [ ] `favicon.ico` (32×32) at root
- [ ] `apple-touch-icon.png` (180×180)
- [ ] SVG favicon and/or 192/512 PNGs
- [ ] `site.webmanifest` with correct name, colors, icons (if PWA-ish)
- [ ] `theme-color` meta
- [ ] Icon is legible at 16px — most logos aren't; use a mark

## Crawlability & indexing
- [ ] `sitemap.xml` present, current, lists only canonical 200-status URLs, referenced in `robots.txt`
- [ ] No orphan pages; important pages within 3 clicks of home
- [ ] Internal links use descriptive anchor text
- [ ] No accidental duplicate content (www + non-www, http + https, trailing-slash variants, paginated dupes)
- [ ] Old URLs 301-redirect to new equivalents after a redesign — **build the redirect map before launch and test every row**
- [ ] Custom 404 returns an actual 404 status (not a 200 "soft 404")
- [ ] Pagination and faceted URLs handled (canonical or noindex as appropriate)
- [ ] Image filenames and alt text are descriptive
- [ ] Page speed acceptable (gate 5) — it's a ranking factor
- [ ] HTTPS everywhere with valid cert (gate 9)

## Local & listings (if local business)
- [ ] Google Business Profile matches site NAP exactly
- [ ] Embedded map points at the right location
- [ ] Location/service-area pages exist for the real service area

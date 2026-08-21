# Gate 5 - Performance

Measure on **mobile, throttled, from a cold cache** - not on your fast laptop with everything warm.

## Targets
| Metric | Good | Needs work | Fail |
|---|---|---|---|
| **LCP** (largest contentful paint) | ≤ 2.5s | 2.5-4s | > 4s |
| **INP** (interaction to next paint) | ≤ 200ms | 200-500ms | > 500ms |
| **CLS** (cumulative layout shift) | ≤ 0.1 | 0.1-0.25 | > 0.25 |
| TTFB | ≤ 0.8s | 0.8-1.8s | > 1.8s |
| Total page weight | ≤ 1.5 MB | 1.5-3 MB | > 3 MB |
| Requests | ≤ 50 | 50-80 | > 80 |
| Lighthouse mobile perf | ≥ 90 | 70-89 | < 70 |

## Tools
- Lighthouse (Chrome devtools) - **mobile preset, throttled**, incognito, no extensions
- PageSpeed Insights - includes real-user (CrUX) field data if the site has traffic
- WebPageTest - filmstrip and waterfall for diagnosing *why*
- Network tab - sort by size; find the offender in 10 seconds

## Images (almost always the problem)
- [ ] No image larger than it displays - a 4000px hero rendered at 800px is a defect
- [ ] Modern formats: **WebP/AVIF** with fallback
- [ ] `srcset`/`sizes` or `<picture>` for responsive delivery
- [ ] Compressed - target < 200 KB for heroes, < 100 KB for content images
- [ ] `width` and `height` (or `aspect-ratio`) set on every image → prevents CLS
- [ ] `loading="lazy"` on below-fold images; **never** on the LCP image
- [ ] `fetchpriority="high"` on the LCP image
- [ ] SVG for logos and icons, minified
- [ ] No giant background images set in CSS without optimization
- [ ] Favicon set complete (see gate 7) and small

## Fonts
- [ ] Max 2 families, only the weights actually used
- [ ] Self-hosted or preconnected; `woff2` only
- [ ] `font-display: swap` (or `optional`) - no invisible text while loading
- [ ] `<link rel="preload">` the critical font
- [ ] Fallback stack metrically similar → no jarring reflow
- [ ] Subset if using a large character set

## Code & delivery
- [ ] CSS/JS minified and compressed (Brotli or gzip) - verify `content-encoding` header
- [ ] No unused CSS/JS frameworks loaded for one component
- [ ] Render-blocking resources minimized; non-critical JS `defer`/`async`
- [ ] No duplicate library loads (two jQuery versions, two analytics tags)
- [ ] Third-party scripts audited - each one justified; they're the usual INP killer
- [ ] Chat widgets, heatmaps, and A/B tools load late or on interaction
- [ ] Caching headers set on static assets (long `max-age` + fingerprinted filenames)
- [ ] CDN serving static assets
- [ ] HTTP/2 or /3 enabled
- [ ] No console errors or 404s in the network tab
- [ ] Animations use `transform`/`opacity` (compositor-friendly), not `top`/`left`/`width`

## Layout stability
- [ ] Reserve space for images, ads, embeds, and banners
- [ ] Late-loading fonts don't shift text
- [ ] Cookie banners/announcement bars don't push content after paint
- [ ] Test CLS by scrolling immediately on a slow connection

## Reality check
- [ ] Load the live site on a **real phone on cellular data**, cold. If it feels slow, it is - regardless of the score.

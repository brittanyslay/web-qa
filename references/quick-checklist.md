# The 20-Minute Pass

For small changes, tight deadlines, or a sanity check before a bigger QA. **Not a substitute for gates 1-11 on a real launch.**

## 5 min - automated
- [ ] `python3 scripts/qa-scan.py <site>` → zero blockers
- [ ] Lighthouse mobile on the top page → perf & a11y ≥ 90
- [ ] Browser console → zero errors, zero 404s

## 10 min - hands on a phone (375px)
- [ ] Homepage loads fast, looks right, no horizontal scroll
- [ ] Tap the **primary CTA** - the whole path, to the confirmation
- [ ] Submit the main form → confirm the email actually arrives
- [ ] Open the mobile menu, hit 3 pages, come back
- [ ] Tap phone / email / map links
- [ ] Read the homepage copy out loud - names, prices, dates correct

## 5 min - the launch-day killers
- [ ] `/robots.txt` doesn't block the site; no `noindex` in production source
- [ ] HTTPS works; www and non-www both land on the canonical URL
- [ ] Analytics real-time registers your visit
- [ ] Share the URL into Slack/iMessage → preview image and title look right
- [ ] Load a junk URL → branded 404
- [ ] Tab through the homepage once → focus is visible, nothing traps you

**Any failure here → stop and run the full gates.**

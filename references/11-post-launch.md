# Gate 11 - Post-Launch Verification

Launch isn't the finish line. This is where real traffic finds what you missed.

## First 15 minutes (before you tell anyone it's live)
- [ ] Load the production URL in a **private window** on a phone and a desktop
- [ ] Hard-refresh / clear cache - you're seeing the new build, not your cached copy
- [ ] Homepage renders correctly, images loaded, no console errors
- [ ] Click through the primary conversion path end to end and receive the confirmation email
- [ ] `robots.txt` and a page-source check for `noindex` (again - verify on production)
- [ ] HTTPS padlock on, all four URL variants resolving to the canonical
- [ ] Analytics real-time shows your visit
- [ ] Spot-check 3-5 key inner pages and the 404
- [ ] Ask one person on a different network/device to load it and tell you what they see

## First 24 hours
- [ ] Re-run Lighthouse on production (the live environment differs from local)
- [ ] Check analytics for traffic arriving and events firing
- [ ] Check for 404s in server logs / Search Console / analytics
- [ ] Confirm form submissions from real users are arriving (ask the client to confirm)
- [ ] Watch error monitoring for JS exceptions from real browsers
- [ ] Check uptime monitor has not alerted
- [ ] Social share preview one more time on the live URL
- [ ] Confirm the client has actually looked at it and signed off

## First week
- [ ] Search Console: indexing status, coverage errors, mobile usability, Core Web Vitals field data
- [ ] Verify pages are appearing in a `site:domain.com` search
- [ ] Review redirects for anything hitting 404 with real traffic
- [ ] Compare traffic against pre-launch baseline; investigate any drop > 20%
- [ ] Read session recordings / heatmaps for confusion points
- [ ] Check bounce/engagement on the top landing pages
- [ ] Collect and triage client and user feedback into a punch list
- [ ] Fix the MINOR items deferred at launch

## First month
- [ ] Ranking check on target terms vs. baseline
- [ ] Conversion rate against the goal set at scope
- [ ] Performance re-check under real traffic
- [ ] Security updates applied
- [ ] Backup restore verified
- [ ] Retrospective: what got caught late, and what checklist item would have caught it earlier? **Add it to this skill.**

## Ongoing cadence for a maintained site
| Frequency | Do |
|---|---|
| Weekly | Uptime, forms still delivering, error log |
| Monthly | Broken links, CMS/plugin/dependency updates, backups, analytics review |
| Quarterly | Full re-run of gates 1-9, content accuracy (prices, staff, hours), SSL/domain expiry |
| Annually | Design/content refresh review, accessibility re-audit, copyright year, credential rotation |

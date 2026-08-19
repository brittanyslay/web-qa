# Gate 10 — Deploy, DNS & Infrastructure

## Pre-deploy
- [ ] Working tree committed; build runs clean with no errors or warnings you haven't read
- [ ] Correct branch/environment deploying to the correct site (check the site ID!)
- [ ] Environment variables set in the host, not hardcoded
- [ ] Build output contains what you expect (no source files, no `.env`, no CSVs, no `node_modules`)
- [ ] Previous version snapshotted for rollback
- [ ] Deploy during a low-traffic window if the site is live and busy

## Domain & DNS
- [ ] Domain registered to the **client**, with them as owner/admin — and it isn't expiring soon
- [ ] Auto-renew on; registrar contact email is monitored
- [ ] Nameservers pointed correctly, propagation complete (check from more than one network)
- [ ] A/AAAA/CNAME records correct
- [ ] **One canonical host**: www and non-www both resolve, but one 301s to the other
- [ ] `http://` and `https://` for both variants all land on the canonical HTTPS URL (test all four)
- [ ] Old/legacy domains redirect to the new one
- [ ] Subdomains resolve (blog, shop, app) and carry valid certs
- [ ] DNS TTLs lowered before a migration, restored after

## Email deliverability (owned by the site, and always forgotten)
- [ ] **SPF** record present and includes every sender (host, form service, ESP, CRM)
- [ ] **DKIM** configured and passing
- [ ] **DMARC** record published (start at `p=none` and monitor)
- [ ] MX records intact — a DNS change must not break the client's email
- [ ] Transactional email (form notifications, receipts) tested to Gmail, Outlook, and iCloud; checked in spam
- [ ] From/reply-to addresses are real, monitored, and on the client's domain

## Hosting
- [ ] Hosting plan sized for expected traffic (especially for a launch push or ad campaign)
- [ ] CDN enabled and caching correctly; cache purged after deploy
- [ ] Cache rules don't serve stale HTML after a content update
- [ ] Compression (Brotli/gzip) on
- [ ] Uptime monitoring + SSL-expiry monitoring with alerts
- [ ] Server logs accessible for debugging
- [ ] Auto-scaling or at least a plan for a traffic spike

## Migration-specific (redesign or replatform)
- [ ] Full crawl of the **old** site captured (URLs, titles, traffic by page) before anything changes
- [ ] Redirect map built from that crawl: every old URL → best new equivalent (not all to home)
- [ ] Every redirect tested post-launch, in bulk
- [ ] Top-traffic and top-backlink pages preserved or redirected with care
- [ ] Old sitemap kept temporarily so crawlers find the redirects
- [ ] Search Console: change-of-address if the domain changed; new sitemap submitted
- [ ] Content parity check — nothing important dropped in the move
- [ ] Analytics annotated with the launch date so the traffic change is explainable

## Handoff
- [ ] Client owns: domain, hosting, CMS admin, analytics, and email accounts
- [ ] Credentials transferred securely (password manager share, never plaintext email)
- [ ] Documentation: how to edit content, who to contact, what's on which platform, renewal dates
- [ ] Training session or a short screen recording for the client's team
- [ ] Maintenance expectations set in writing (what's included, what's billable)

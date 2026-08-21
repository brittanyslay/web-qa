# Gate 8 - Analytics, Tracking & Consent

**Launching without working analytics means launching blind for however long it takes to notice.** Verify with real data, in real time, before go-live.

## Installation
- [ ] Analytics (GA4 or alternative) installed on **every** page, once - not twice
- [ ] Real-time report shows your own test visit
- [ ] Correct property/stream ID - not the agency's, not a previous client's, not the staging property
- [ ] Tag Manager container published (not left in preview/draft)
- [ ] No duplicate tags firing (check with Tag Assistant / GA debug view)
- [ ] Internal traffic filtered (your IP, the client's office) - but **verify the filter isn't excluding real users**
- [ ] Data retention setting configured
- [ ] Time zone and currency set correctly

## Events & conversions
- [ ] Key events defined and firing: form submits, phone clicks, email clicks, CTA clicks, purchases, downloads, video plays, outbound clicks, scroll depth
- [ ] Each conversion marked as a conversion/key event in the platform
- [ ] E-commerce/ticketing: purchase event fires **once** with correct value, currency, and item data
- [ ] Thank-you page tracked and not reachable/countable without a real submit
- [ ] Cross-domain tracking configured if checkout is on another domain (Stripe, Eventbrite, Shopify)
- [ ] UTM handling doesn't break on the site's redirects
- [ ] Ad platform pixels (Meta, Google Ads, LinkedIn, Reddit, TikTok) installed and verified in each platform's own diagnostic tool
- [ ] Conversion API / server-side tracking configured if used
- [ ] Call tracking numbers correct and swapping properly, if used

## Other tooling
- [ ] Search Console verified and linked to analytics
- [ ] Bing Webmaster Tools (cheap, occasionally useful)
- [ ] Heatmap/session recording tool configured with PII masking on form fields
- [ ] Error monitoring (Sentry or equivalent) on JS-heavy sites
- [ ] Uptime monitoring configured with alerts to a real inbox/phone
- [ ] Email platform integration verified end to end (signup → list → welcome automation)

## Consent & privacy compliance
- [ ] Consent banner appears for regions that require it, before non-essential tags fire
- [ ] Rejecting cookies **actually blocks** the tags - verify in the network tab, don't trust the plugin
- [ ] Consent Mode / equivalent configured so analytics degrades gracefully
- [ ] Cookie policy lists the cookies actually set
- [ ] Preference center lets a user change their mind
- [ ] No PII in analytics URLs, event parameters, or page titles (emails, names, order details)
- [ ] IP anonymization where required
- [ ] Data Processing Agreement in place with processors, where the client's obligations require it

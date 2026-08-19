# Gate 9 — Security & Privacy

## HTTPS & certificates
- [ ] Valid TLS certificate, not expired, matching the domain **and** the www variant
- [ ] Auto-renewal configured (and you know when it expires)
- [ ] HTTP redirects to HTTPS with a 301 — test `http://` explicitly
- [ ] **No mixed content** — every asset over HTTPS (check console warnings)
- [ ] HSTS header set (start with a short max-age before preloading)

## Secrets & exposure — the career-ending category
- [ ] **No API keys, tokens, passwords, or credentials in client-side code, HTML comments, or the JS bundle** — grep the built output
- [ ] No secrets committed to the repo, including in history
- [ ] `.env`, `.git`, `config.php`, backups, and `.DS_Store` not publicly reachable — try fetching them
- [ ] No directory listing enabled
- [ ] Source maps not exposed in production (or intentionally so)
- [ ] Admin/CMS login isn't at a guessable default path where that matters; 2FA enabled
- [ ] Default/demo accounts removed; strong unique admin passwords
- [ ] No internal notes, TODOs, or client complaints left in comments
- [ ] Staging site password-protected and noindexed
- [ ] Test/dummy data removed (fake orders, test users, "asdf" submissions)

## Headers & hardening
| Header | Value |
|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` / `frame-ancestors` | `SAMEORIGIN` / CSP directive |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Content-Security-Policy` | Scoped to what the site actually loads |
| `Permissions-Policy` | Deny camera/mic/geo unless used |

- [ ] Verify with securityheaders.com or `curl -I`
- [ ] CSP doesn't break analytics/fonts/embeds — test after adding

## Application security
- [ ] Form inputs sanitized/escaped server-side (never trust client validation)
- [ ] Parameterized queries — no string-concatenated SQL
- [ ] File uploads: type and size restricted, stored outside the web root, renamed
- [ ] Rate limiting on forms, login, and API endpoints
- [ ] CSRF protection on state-changing requests
- [ ] Authentication: session timeout, secure + httpOnly + SameSite cookies, safe password reset flow
- [ ] Authorization checked server-side — you can't reach another user's data by changing an ID in the URL
- [ ] Error messages don't leak stack traces, paths, or software versions
- [ ] CMS, plugins, themes, and dependencies updated; `npm audit` / equivalent clean of criticals
- [ ] Unused plugins and themes deleted, not just deactivated
- [ ] Third-party scripts come from sources you trust; use SRI on CDN assets
- [ ] Web application firewall / bot protection where warranted

## Privacy
- [ ] Only collecting data you have a reason and a lawful basis to collect
- [ ] Personal data encrypted in transit and at rest
- [ ] Retention and deletion policy exists; a deletion request can actually be honored
- [ ] Client's and users' personal contact details not published beyond what's intended
- [ ] Embedded third parties (YouTube, maps, fonts) disclosed — use privacy-enhanced modes where available
- [ ] Email addresses on the page obfuscated or behind a form if scraping is a concern

## Backups & recovery
- [ ] Automated backups running, with a known restore path
- [ ] A restore has actually been tested at least once
- [ ] Pre-launch snapshot taken before go-live
- [ ] Code in version control with the current production state tagged
- [ ] Rollback plan written down: what command, who runs it, how long it takes

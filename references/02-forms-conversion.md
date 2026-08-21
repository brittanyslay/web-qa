# Gate 2 - Forms & Conversion Paths

**The rule: submit every form for real, from a real device, and confirm the message lands.** A form that looks fine and goes nowhere is the most expensive bug in web work.

## Submission
- [ ] Submit each form with valid data - confirm delivery to the **actual** inbox/CRM/database
- [ ] Check the spam folder; if it landed there, fix SPF/DKIM/DMARC (see gate 10)
- [ ] Confirm notification goes to **all** intended recipients (test each address)
- [ ] Auto-responder to the user fires, is branded, and has correct reply-to
- [ ] Success state is obvious - message, redirect, or thank-you page (not a silent reset)
- [ ] Thank-you page is reachable only after submit, and fires the conversion event
- [ ] Failure state tells the user what to do next and doesn't lose their input
- [ ] Double-submit is prevented (disable button / idempotency)
- [ ] Data arrives complete and correctly mapped - every field, no truncation, no swapped columns

## Validation
- [ ] Required fields enforced; optional fields genuinely optional
- [ ] Email, phone, ZIP, URL, date formats validated - but not so strictly they reject valid input (`+`, international numbers, apostrophes in names, long TLDs)
- [ ] Errors appear inline, next to the field, in plain language - not one generic banner
- [ ] Errors are announced to screen readers (`aria-live`, `aria-invalid`, `aria-describedby`)
- [ ] Error color is not the only signal (icon or text too)
- [ ] Validation fires at a sensible time (on blur/submit, not on first keystroke)
- [ ] Character limits shown before they're hit

## Usability
- [ ] Every input has a visible, persistent `<label>` - placeholder-as-label is a defect
- [ ] Correct `type` and `inputmode` so mobile shows the right keyboard (`email`, `tel`, `numeric`)
- [ ] `autocomplete` attributes set (`name`, `email`, `tel`, `street-address`, `postal-code`)
- [ ] Tab order is logical; Enter submits
- [ ] Tap targets ≥ 44×44px; fields don't zoom on focus in iOS (font-size ≥ 16px)
- [ ] Form fits and functions at 375px with the keyboard open
- [ ] Only asks for what's actually needed - every extra field costs conversions
- [ ] Multi-step forms show progress and preserve data on back/refresh

## Anti-spam & compliance
- [ ] Spam protection active (honeypot / captcha alternative) - and it does **not** block real users
- [ ] Never use a CAPTCHA that blocks screen reader or keyboard users without an alternative
- [ ] Consent checkbox for marketing where required, unchecked by default
- [ ] Privacy policy linked at the point of collection
- [ ] GDPR/CCPA: lawful basis, data retention, and deletion path if collecting from those regions
- [ ] Form data transmitted over HTTPS only

## The whole conversion path
- [ ] Walk the **complete** primary journey on a real phone: ad/search → landing → CTA → form → confirmation → email received
- [ ] Repeat for each secondary path (newsletter, booking, ticket purchase, download, contact)
- [ ] E-commerce/ticketing: add to cart, quantity change, remove, promo code, tax/shipping, checkout, payment, receipt, confirmation email, and the post-purchase page
- [ ] Test a **declined** payment and a mid-checkout abandon
- [ ] Third-party checkout (Stripe/Eventbrite/Shopify) returns to the right place and fires the right event
- [ ] Phone/email/booking links work from the device they'll be used on

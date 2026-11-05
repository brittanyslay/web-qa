# Changelog

## v1.1.0 - 2026-11-05

New checks and hardening, plus a tighter operating contract for the skill.

- **Duplicate-content SEO.** The scanner now flags identical `<title>` tags (major) and identical meta descriptions (minor) reused across pages - a ranking problem no single page reveals. It only fires across two or more pages and ignores blank fields, so a site of pages that each leave a field empty is never flagged.
- **Missing `<meta charset>`** is caught (minor), covering both the modern and legacy `http-equiv` forms.
- **Scanner hardening.** Unexpected runtime errors now exit `2` with a one-line message instead of a traceback, keeping the documented 0/1/2 exit-code contract. Responses are read with a hard byte cap so a runaway body cannot exhaust memory. `--max-pages` and the new `--timeout` are validated, and a bad `.qaignore` read no longer aborts the scan.
- **New `--timeout` flag** for slower hosts in URL mode (default 15s).
- **Skill operating contract.** SKILL.md now states plainly that the skill is intake-first and runs the scan itself, then self-critiques and returns a graded go / no-go report rather than raw scanner output.
- Test suite grew from 36 to 47, covering every new check and the clean-exit behaviour on bad input.

## v1.0.2 - 2026-08-20

Pulled the README preview image for now while all the public repos' preview images get reconsidered together. The image file is still in the repo, just not linked from the README.


## v1.0.1 - 2026-08-20

Replaced the README preview image. It was a hand-illustrated mockup (a generic gradient top bar and squircle icon over invented scan results) that didn't correspond to a real run of the scanner. Swapped for an actual terminal screenshot of `python3 scripts/qa-scan.py examples/demo-site` against the repo's own demo-site fixture - real output, not a mockup.

## v1.0.0 - 2026-08-19

Initial release: the 11-gate pre-launch QA process as a Claude skill, plus `qa-scan.py`, a zero-dependency scanner covering functionality, security, SEO, accessibility, performance, and analytics/tag checks.

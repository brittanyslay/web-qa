#!/usr/bin/env python3
"""
qa-scan.py — mechanical pre-launch scanner for static sites and live URLs.

Catches the ~40% of QA findings a script can see. Everything else is in the
gate checklists (references/01..11). A clean scan is NOT a passed QA.

Usage:
    python3 qa-scan.py <dir>                 # scan a local site directory
    python3 qa-scan.py <https://url>         # crawl a live site (same origin)
    python3 qa-scan.py <dir> --json          # machine-readable output
    python3 qa-scan.py <url> --max-pages 40  # crawl depth cap (default 25)

Exit codes: 0 = no blockers, 1 = blockers found, 2 = usage/runtime error.
Stdlib only. No installs.
"""

# Author: Brittany Slay (https://brittanyslay.com) · Noncommercial use only (PolyForm NC 1.0.0) · Required Notice: Copyright Brittany Slay

import sys, os, re, json, argparse
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl

BLOCKER, MAJOR, MINOR, NOTE = "BLOCKER", "MAJOR", "MINOR", "NOTE"
ORDER = {BLOCKER: 0, MAJOR: 1, MINOR: 2, NOTE: 3}
ICON = {BLOCKER: "[BLOCKER]", MAJOR: "[MAJOR]  ", MINOR: "[MINOR]  ", NOTE: "[NOTE]   "}

SKIP_DIRS = {"node_modules", ".git", ".next", "dist-cache", "__pycache__",
             ".venv", "venv", ".cache", "vendor", ".netlify", ".vercel"}

IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg", ".ico"}

def robots_blocks_everything(txt):
    """True only if the wildcard (or Googlebot) group disallows the whole site.
    A `Disallow: /` under GPTBot/CCBot/etc. is an intentional AI-crawler block,
    not a launch defect."""
    groups, agents, cur = [], [], None
    for raw in txt.splitlines():
        line = raw.split("#")[0].strip()
        if not line or ":" not in line:
            continue
        field, _, val = line.partition(":")
        field, val = field.strip().lower(), val.strip()
        if field == "user-agent":
            if cur is not None:
                groups.append((agents, cur)); agents, cur = [], None
            agents.append(val.lower())
        elif field in ("allow", "disallow"):
            if cur is None:
                cur = []
            cur.append((field, val))
    if cur is not None:
        groups.append((agents, cur))
    for agents, rules in groups:
        if not any(a in ("*", "googlebot") for a in agents):
            continue
        if any(f == "allow" and v in ("/", "") for f, v in rules):
            continue
        if any(f == "disallow" and v == "/" for f, v in rules):
            return True
    return False


SECRET_PATTERNS = [
    (r"sk_live_[A-Za-z0-9]{10,}",                      "Stripe live secret key"),
    (r"AKIA[0-9A-Z]{16}",                              "AWS access key ID"),
    (r"nfp_[A-Za-z0-9]{20,}",                          "Netlify personal access token"),
    (r"gh[pousr]_[A-Za-z0-9]{30,}",                    "GitHub token"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}",                  "Slack token"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY",    "Private key block"),
    (r"(?i)(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*[\"'][^\"'\s]{16,}[\"']",
                                                        "Possible hardcoded credential"),
]
# (pattern, description, severity) — patterns must be specific enough not to fire
# on legitimate prose. "your company" appears in real copy; "Your Company Here" does not.
PLACEHOLDER_PATTERNS = [
    (r"(?i)lorem ipsum|dolor sit amet",            "Lorem ipsum placeholder text", BLOCKER),
    (r"(?i)your (company|business|brand|logo|name|text|headline) here",
                                                    "Template placeholder copy", BLOCKER),
    (r"\[(?:your|insert|add|company|client)[^\]]{2,30}\]",
                                                    "Unfilled template token", BLOCKER),
    (r"\{\{[^}]{1,40}\}\}",                        "Unrendered template variable", BLOCKER),
    (r"(?i)placeholder (text|image|content|copy)",  "Explicit placeholder content", BLOCKER),
    (r"(?i)insert (text|copy|image|name) here",     "Template placeholder copy", BLOCKER),
    (r"(?i)\b(TODO|FIXME)\b",                      "TODO/FIXME visible in page text", MAJOR),
    (r"(?i)\bTBD\b",                               "TBD placeholder in page text", MAJOR),
    (r"(?i)^\s*test (page|post|event|product)\b",  "Possible test content published", MAJOR),
]
VAGUE_LINK_TEXT = {"click here", "here", "read more", "more", "link", "this",
                   "learn more", "click", "download"}

BAD_HOST_PATTERNS = [r"localhost", r"127\.0\.0\.1", r"0\.0\.0\.0", r"\.local\b",
                     r"staging\.", r"\.ngrok\.", r"file://", r"deploy-preview",
                     r"--[a-z0-9]+\.netlify\.app", r"\.vercel\.app/_"]


class Finding:
    def __init__(self, sev, gate, page, msg, detail=""):
        self.sev, self.gate, self.page, self.msg, self.detail = sev, gate, page, msg, detail

    def as_dict(self):
        return {"severity": self.sev, "gate": self.gate, "page": self.page,
                "issue": self.msg, "detail": self.detail}


class Parsed(HTMLParser):
    """Collects everything the checks need in one pass."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self._title_seen = False
        self.metas = []           # list of dicts
        self.links_rel = []       # <link> tags
        self.anchors = []         # (href, text, attrs)
        self._a_stack = []
        self.images = []          # attrs dicts
        self.headings = []        # (level, text)
        self._h_stack = []
        self.ids = []
        self.inputs = []          # attrs dicts for input/select/textarea
        self.labels = []          # attrs dicts
        self.label_wrapped = []   # names/ids of controls inside a <label>
        self._label_depth = 0
        self.buttons = []         # (attrs, text)
        self._btn_stack = []
        self.html_attrs = {}
        self.scripts = []
        self.stylesheets = []
        self.iframes = []
        self.forms = []
        self.text_chunks = []
        self.has_main = 0
        self.has_h1_in_main = False
        self._skip_text = 0
        self.video_audio = []

    # ---- helpers
    def _d(self, attrs):
        return {k.lower(): (v if v is not None else "") for k, v in attrs}

    def handle_starttag(self, tag, attrs):
        a = self._d(attrs)
        if "id" in a and a["id"]:
            self.ids.append(a["id"])
        if tag == "html":
            self.html_attrs = a
        elif tag == "title":
            if not self._title_seen:
                self._in_title = True
                self._title_seen = True
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.links_rel.append(a)
        elif tag == "a":
            self.anchors.append({"attrs": a, "text": ""})
            self._a_stack.append(len(self.anchors) - 1)
        elif tag == "img":
            self.images.append(a)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append([int(tag[1]), ""])
            self._h_stack.append(len(self.headings) - 1)
        elif tag in ("input", "select", "textarea"):
            self.inputs.append(a)
            if self._label_depth > 0:
                self.label_wrapped.append(a.get("id", "") or a.get("name", "") or "*wrapped*")
                a["_wrapped_label"] = "1"
        elif tag == "label":
            self.labels.append(a)
            self._label_depth += 1
        elif tag == "button":
            self.buttons.append({"attrs": a, "text": ""})
            self._btn_stack.append(len(self.buttons) - 1)
        elif tag == "script":
            self.scripts.append(a)
            self._skip_text += 1
        elif tag == "style":
            self._skip_text += 1
        elif tag == "iframe":
            self.iframes.append(a)
        elif tag == "form":
            self.forms.append(a)
        elif tag == "main":
            self.has_main += 1
        elif tag in ("video", "audio"):
            self.video_audio.append(a)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in ("a", "button", "label", "script", "style"):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "a" and self._a_stack:
            self._a_stack.pop()
        elif tag == "button" and self._btn_stack:
            self._btn_stack.pop()
        elif tag == "label" and self._label_depth > 0:
            self._label_depth -= 1
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._h_stack:
            self._h_stack.pop()
        elif tag in ("script", "style") and self._skip_text > 0:
            self._skip_text -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data
        if self._skip_text:
            return
        s = data.strip()
        if s:
            self.text_chunks.append(s)
        for i in self._a_stack:
            self.anchors[i]["text"] += data
        for i in self._btn_stack:
            self.buttons[i]["text"] += data
        for i in self._h_stack:
            self.headings[i][1] += data


class Page:
    def __init__(self, key, html, size=0, source_path=None, base_url=None):
        self.key = key
        self.html = html
        self.size = size or len(html.encode("utf-8", "ignore"))
        self.path = source_path
        self.base_url = base_url
        self.p = Parsed()
        try:
            self.p.feed(html)
        except Exception:
            pass

    def meta(self, name=None, prop=None):
        for m in self.p.metas:
            if name and m.get("name", "").lower() == name:
                return m.get("content", "")
            if prop and m.get("property", "").lower() == prop:
                return m.get("content", "")
        return None


# ------------------------------------------------------------------ checks
def check_page(pg, F, site):
    page = pg.key
    P = pg.p
    add = lambda s, g, m, d="": F.append(Finding(s, g, page, m, d))

    # ---- 7. head / metadata
    title = (P.title or "").strip()
    if not title:
        add(BLOCKER, "SEO", "Missing <title>")
    elif len(title) > 65:
        add(MINOR, "SEO", f"Title too long ({len(title)} chars, aim 50-60)", title[:80])
    elif len(title) < 15:
        add(MINOR, "SEO", f"Title very short ({len(title)} chars)", title)

    desc = pg.meta(name="description")
    if desc is None:
        add(MAJOR, "SEO", "Missing meta description")
    elif not desc.strip():
        add(MAJOR, "SEO", "Empty meta description")
    elif not (120 <= len(desc) <= 165):
        add(MINOR, "SEO", f"Meta description length {len(desc)} (aim 140-160)")

    robots = (pg.meta(name="robots") or "")
    if "noindex" in robots.lower():
        intentional = re.search(r"(^|/)(404|500|thank[-_]?you|thanks|search|preview)",
                                page, re.I)
        if intentional:
            add(NOTE, "SEO", "noindex present (expected on this page type)", f"{page}: {robots}")
        else:
            add(BLOCKER, "SEO", "Page is set to NOINDEX — will not appear in search", robots)

    if not pg.meta(name="viewport"):
        add(BLOCKER, "Responsive", "Missing viewport meta — site will not render correctly on mobile")
    else:
        vp = pg.meta(name="viewport")
        if "user-scalable=no" in vp.replace(" ", "") or "maximum-scale=1" in vp.replace(" ", ""):
            add(MAJOR, "A11y", "Viewport blocks zoom (WCAG 1.4.4 failure)", vp)

    lang = P.html_attrs.get("lang", "")
    if not lang:
        add(MAJOR, "A11y", "Missing lang attribute on <html>")

    rels = [l.get("rel", "").lower() for l in P.links_rel]
    if not any("canonical" in r for r in rels):
        add(MINOR, "SEO", "No canonical link")
    if not any("icon" in r for r in rels) and not site.get("has_favicon_file"):
        add(MINOR, "SEO", "No favicon declared")
    if not any("apple-touch-icon" in r for r in rels):
        add(NOTE, "SEO", "No apple-touch-icon (iOS home screen)")

    # Open Graph / Twitter
    og = {k: pg.meta(prop=f"og:{k}") for k in ("title", "description", "image", "url")}
    missing_og = [k for k, v in og.items() if not v]
    if len(missing_og) == 4:
        add(MAJOR, "SEO", "No Open Graph tags — link shares will look broken")
    elif missing_og:
        add(MINOR, "SEO", f"Incomplete Open Graph: missing {', '.join(missing_og)}")
    if og.get("image") and not og["image"].startswith(("http://", "https://")):
        add(MAJOR, "SEO", "og:image is not an absolute URL — most platforms will ignore it", og["image"])
    if not pg.meta(name="twitter:card"):
        add(MINOR, "SEO", "No twitter:card meta")

    # ---- 4. headings
    h1s = [h for h in P.headings if h[0] == 1]
    if len(h1s) == 0:
        add(MAJOR, "A11y/SEO", "No <h1> on page")
    elif len(h1s) > 1:
        add(MINOR, "A11y/SEO", f"{len(h1s)} <h1> elements (should be 1)",
            " | ".join(h[1].strip()[:40] for h in h1s[:4]))
    prev = 0
    for lvl, txt in P.headings:
        if prev and lvl > prev + 1:
            add(MINOR, "A11y", f"Heading level skipped (h{prev} -> h{lvl})", txt.strip()[:60])
        prev = lvl
    for lvl, txt in P.headings:
        if not txt.strip():
            add(MINOR, "A11y", f"Empty h{lvl} element")

    if P.has_main == 0:
        add(MINOR, "A11y", "No <main> landmark")
    elif P.has_main > 1:
        add(MINOR, "A11y", f"{P.has_main} <main> elements (should be 1)")

    # ---- duplicate IDs
    seen, dupes = set(), set()
    for i in P.ids:
        if i in seen:
            dupes.add(i)
        seen.add(i)
    if dupes:
        add(MAJOR, "Functionality", f"Duplicate id attributes ({len(dupes)}) — breaks anchors, labels & JS",
            ", ".join(sorted(dupes)[:8]))

    # ---- images
    for img in P.images:
        src = img.get("src", "") or img.get("data-src", "")
        label = src.split("/")[-1][:50] or "(no src)"
        if "alt" not in img:
            add(MAJOR, "A11y", "Image missing alt attribute", label)
        elif img["alt"].strip() and re.match(r"^(image|img|photo|picture|dsc|screen ?shot|untitled)[\s_\-0-9.]*$",
                                             img["alt"].strip(), re.I):
            add(MINOR, "A11y", "Unhelpful alt text", f'{label} -> alt="{img["alt"][:40]}"')
        if not src:
            add(MAJOR, "Functionality", "Image with no src", str(img)[:60])
        if ("width" not in img or "height" not in img) and "style" not in img and \
           not src.lower().endswith(".svg"):
            add(MINOR, "Performance", "Image without width/height — causes layout shift (CLS)", label)
        if "loading" not in img:
            add(NOTE, "Performance", "Consider loading=\"lazy\" on below-fold image", label)

    # ---- links
    for a in P.anchors:
        at = a["attrs"]
        href = (at.get("href") or "").strip()
        text = " ".join(a["text"].split())
        acc = text or at.get("aria-label", "") or at.get("title", "")
        if not href and "name" not in at and "id" not in at:
            add(MINOR, "Functionality", "Anchor with no href", text[:50])
        if href.startswith("javascript:") and href != "javascript:void(0)":
            add(MINOR, "Functionality", "javascript: href", href[:60])
        if href in ("#", ""):
            if text:
                add(MINOR, "Functionality", "Placeholder link (href=\"#\") — goes nowhere", text[:50])
        if not acc.strip() and not P_img_inside(a):
            add(MAJOR, "A11y", "Link with no accessible text", href[:60])
        if text.lower().strip(" .!»>→") in VAGUE_LINK_TEXT:
            add(MINOR, "A11y/SEO", f'Vague link text: "{text.strip()}"', href[:50])
        if at.get("target") == "_blank":
            rel = at.get("rel", "").lower()
            if "noopener" not in rel:
                add(MAJOR, "Security", "target=\"_blank\" without rel=\"noopener\"", href[:60])
        if href.startswith("http://") and "localhost" not in href and "127.0.0.1" not in href:
            add(MAJOR, "Security", "Insecure http:// link", href[:70])
        for pat in BAD_HOST_PATTERNS:
            if re.search(pat, href, re.I):
                add(BLOCKER, "Deploy", "Dev/staging/local URL in output", href[:70])
                break
        if href.startswith("mailto:"):
            add(NOTE, "Privacy", "Exposed email address (scraper target)", href[:60])

    # ---- forms & inputs
    label_for = {l.get("for", "") for l in P.labels if l.get("for")}
    for inp in P.inputs:
        t = (inp.get("type") or "text").lower()
        if t in ("hidden", "submit", "button", "reset", "image"):
            continue
        named = inp.get("id") or inp.get("name") or "(unnamed field)"
        has_label = (inp.get("id") and inp["id"] in label_for) or \
                    inp.get("aria-label") or inp.get("aria-labelledby") or \
                    inp.get("_wrapped_label")
        if not has_label:
            add(MAJOR, "A11y/Forms", "Form field with no associated label", named)
        if not inp.get("id") and not inp.get("aria-label"):
            add(MINOR, "Forms", "Field has no id (cannot be labelled)", named)
        if t == "email" and not inp.get("autocomplete"):
            add(NOTE, "Forms", "Email field without autocomplete attribute", named)
        if t in ("text", "email", "tel", "search", "password", "number") and inp.get("placeholder") \
           and not has_label:
            add(MAJOR, "A11y/Forms", "Placeholder used as the only label", named)
    for f in P.forms:
        if not f.get("action") and not any(s.get("src", "") for s in P.scripts):
            add(MAJOR, "Forms", "Form with no action and no JS handler — submissions go nowhere")
        if (f.get("action") or "").startswith("http://"):
            add(BLOCKER, "Security", "Form posts over insecure http://", f.get("action", "")[:60])

    for b in P.buttons:
        acc = " ".join(b["text"].split()) or b["attrs"].get("aria-label", "") or b["attrs"].get("title", "")
        if not acc.strip():
            add(MAJOR, "A11y", "Button with no accessible name", str(b["attrs"])[:60])

    for f in P.iframes:
        if not f.get("title"):
            add(MINOR, "A11y", "iframe without title attribute", (f.get("src", "") or "")[:60])
        if (f.get("src") or "").startswith("http://"):
            add(MAJOR, "Security", "iframe loaded over http:// (mixed content)", f.get("src", "")[:60])

    for v in P.video_audio:
        if "autoplay" in v and "muted" not in v:
            add(MAJOR, "A11y", "Media autoplays with sound")
        if "controls" not in v and "autoplay" not in v:
            add(MINOR, "A11y", "Media without controls")

    # ---- content scan
    body_text = " ".join(P.text_chunks)
    for pat, why, sev in PLACEHOLDER_PATTERNS:
        m = re.search(pat, body_text)
        if m:
            ctx = body_text[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")
            add(sev, "Content", why, "…" + ctx.strip()[:100])
    for pat, why in SECRET_PATTERNS:
        m = re.search(pat, pg.html)
        if m:
            add(BLOCKER, "Security", f"{why} appears in page source", m.group(0)[:24] + "…")
    if any(re.search(r"(?i)todo|fixme|hack\b|broken|client (hates|wants)", c)
           for c in re.findall(r"(?s)<!--.*?-->", pg.html)):
        add(MINOR, "Content", "Internal note left in an HTML comment")

    # mixed content in src attributes
    for m in re.finditer(r'(?:src|href)=["\']http://([^"\']+)', pg.html):
        host = m.group(1).split("/")[0]
        if host not in ("www.w3.org", "schema.org", "localhost"):
            add(MAJOR, "Security", "Mixed content: asset loaded over http://", host)
            break

    # page weight (local only)
    if pg.size > 300_000:
        add(MINOR, "Performance", f"HTML document is {pg.size/1024:.0f} KB (large)")


def P_img_inside(a):
    """Crude: link text empty but it probably wraps an image/icon."""
    return "img" in a["text"].lower() or bool(a["attrs"].get("class"))


# ------------------------------------------------------------------ local mode
def resolve_local(root, page_path, href):
    """Return (abs_path_or_None, kind) for an internal href."""
    href, _frag = urldefrag(href)
    if not href:
        return None, "self"
    if href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#")) \
       or href.startswith("//"):
        return None, "external"
    href = href.split("?", 1)[0]          # drop query string (cache-busters etc.)
    if not href:
        return None, "self"
    base = root if href.startswith("/") else os.path.dirname(page_path)
    target = os.path.normpath(os.path.join(base, href.lstrip("/")))
    if os.path.isdir(target):
        for idx in ("index.html", "index.htm"):
            if os.path.exists(os.path.join(target, idx)):
                return os.path.join(target, idx), "file"
    if os.path.exists(target):
        return target, "file"
    for ext in (".html", ".htm"):
        if os.path.exists(target + ext):
            return target + ext, "file"
    return target, "missing"


def scan_local(root, F, site):
    pages, html_files = {}, []
    import fnmatch
    ignore = site.get("ignore", [])

    def ignored(relpath):
        return any(fnmatch.fnmatch(relpath, g) or fnmatch.fnmatch(os.path.basename(relpath), g)
                   or relpath.startswith(g.rstrip("/*") + "/") for g in ignore)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
                       and not ignored(os.path.relpath(os.path.join(dirpath, d), root))]
        for fn in filenames:
            if fn.lower().endswith((".html", ".htm")):
                fp = os.path.join(dirpath, fn)
                if not ignored(os.path.relpath(fp, root)):
                    html_files.append(fp)
    if not html_files:
        print(f"No HTML files found in {root}", file=sys.stderr)
        sys.exit(2)

    site["has_favicon_file"] = any(os.path.exists(os.path.join(root, f))
                                   for f in ("favicon.ico", "favicon.svg", "favicon.png"))

    for fp in sorted(html_files):
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                html = fh.read()
        except Exception as e:
            F.append(Finding(MAJOR, "Functionality", os.path.relpath(fp, root),
                             f"Could not read file: {e}"))
            continue
        rel = os.path.relpath(fp, root)
        pages[fp] = Page(rel, html, os.path.getsize(fp), source_path=fp)

    for fp, pg in pages.items():
        check_page(pg, F, site)
        # internal link resolution
        for a in pg.p.anchors:
            href = (a["attrs"].get("href") or "").strip()
            if not href:
                continue
            frag = urlparse(href).fragment
            target, kind = resolve_local(root, fp, href)
            if kind == "missing":
                F.append(Finding(BLOCKER, "Functionality", pg.key,
                                 "Broken internal link — target does not exist", href[:70]))
            elif kind == "self" and frag:
                if frag not in pg.p.ids and frag not in [x.get("name", "") for x in
                                                         [an["attrs"] for an in pg.p.anchors]]:
                    F.append(Finding(MAJOR, "Functionality", pg.key,
                                     "Anchor link points to an id that does not exist", "#" + frag))
            elif kind == "file" and frag and target in pages:
                if frag not in pages[target].p.ids:
                    F.append(Finding(MINOR, "Functionality", pg.key,
                                     "Cross-page anchor target not found", href[:70]))
        # asset existence + weight
        page_weight = pg.size
        assets = [(i.get("src", ""), "image") for i in pg.p.images] + \
                 [(s.get("src", ""), "script") for s in pg.p.scripts] + \
                 [(l.get("href", ""), "style") for l in pg.p.links_rel
                  if "stylesheet" in (l.get("rel", "").lower())]
        for src, kind in assets:
            if not src or src.startswith(("http://", "https://", "data:", "//")):
                continue
            tgt, k = resolve_local(root, fp, src)
            if k == "missing":
                sev = BLOCKER  # a missing image, script, or stylesheet all 404
                F.append(Finding(sev, "Functionality", pg.key,
                                 f"Missing {kind} file — will 404", src[:70]))
                continue
            if tgt and os.path.exists(tgt) and os.path.isfile(tgt):
                sz = os.path.getsize(tgt)
                page_weight += sz
                name = os.path.basename(tgt)
                if kind == "image" and os.path.splitext(tgt)[1].lower() in IMG_EXT:
                    if sz > 1_000_000:
                        F.append(Finding(BLOCKER, "Performance", pg.key,
                                         f"Image is {sz/1_048_576:.1f} MB — will destroy mobile load time", name))
                    elif sz > 400_000:
                        F.append(Finding(MAJOR, "Performance", pg.key,
                                         f"Image is {sz/1024:.0f} KB (target <200 KB)", name))
                    elif sz > 200_000:
                        F.append(Finding(MINOR, "Performance", pg.key,
                                         f"Image is {sz/1024:.0f} KB (target <200 KB)", name))
                    if os.path.splitext(tgt)[1].lower() in (".png", ".jpg", ".jpeg") and sz > 150_000:
                        F.append(Finding(NOTE, "Performance", pg.key,
                                         "Consider WebP/AVIF for this image", name))
                if kind in ("script", "style") and sz > 500_000:
                    F.append(Finding(MAJOR, "Performance", pg.key,
                                     f"{kind} bundle is {sz/1024:.0f} KB", name))
        if page_weight > 3_000_000:
            F.append(Finding(MAJOR, "Performance", pg.key,
                             f"Total page weight ~{page_weight/1_048_576:.1f} MB (target <1.5 MB)"))
        elif page_weight > 1_500_000:
            F.append(Finding(MINOR, "Performance", pg.key,
                             f"Total page weight ~{page_weight/1_048_576:.1f} MB (target <1.5 MB)"))

    # site-level files
    site_page = "(site)"
    for f, sev, why in (("robots.txt", MINOR, "No robots.txt"),
                        ("sitemap.xml", MINOR, "No sitemap.xml"),
                        ("404.html", MINOR, "No custom 404 page")):
        if not os.path.exists(os.path.join(root, f)):
            F.append(Finding(sev, "SEO", site_page, why))
    rp = os.path.join(root, "robots.txt")
    if os.path.exists(rp):
        txt = open(rp, encoding="utf-8", errors="replace").read()
        if robots_blocks_everything(txt):
            F.append(Finding(BLOCKER, "SEO", "robots.txt",
                             "robots.txt blocks the entire site from search engines"))
        if "sitemap:" not in txt.lower():
            F.append(Finding(NOTE, "SEO", "robots.txt", "robots.txt does not reference a sitemap"))
    # stray files that must never reach production.
    # A source repo legitimately contains .git and .DS_Store; a BUILD OUTPUT directory
    # does not. Grade accordingly instead of crying wolf on every working copy.
    is_source_repo = os.path.isdir(os.path.join(root, ".git"))
    for bad in (".env", ".env.local", ".env.production", ".DS_Store",
                "config.php.bak", "backup.zip", "db.sql", ".git/config",
                ".htpasswd", "id_rsa"):
        if os.path.exists(os.path.join(root, bad)):
            secret_ish = bad.startswith(".env") or bad in (".htpasswd", "id_rsa",
                                                           "db.sql", "backup.zip")
            if secret_ish:
                F.append(Finding(BLOCKER, "Security", site_page,
                                 f"{bad} is in the scanned directory — it must never be deployed"))
            elif is_source_repo:
                F.append(Finding(MAJOR, "Security", site_page,
                                 f"{bad} present — this looks like a source repo, so confirm your "
                                 f"deploy step excludes it"))
            else:
                F.append(Finding(BLOCKER, "Security", site_page,
                                 f"{bad} present in the build output — do not deploy it"))
    return len(pages)


# ------------------------------------------------------------------ URL mode
_SSL_CTX = None
_SSL_UNVERIFIED = False


def ssl_context(F=None):
    """Build a verifying context. If the local trust store is broken (common with
    python.org builds on macOS), fall back to unverified and SAY SO — never report
    a local cert-store problem as a site defect."""
    global _SSL_CTX, _SSL_UNVERIFIED
    if _SSL_CTX is not None:
        return _SSL_CTX
    try:
        import certifi
        _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        _SSL_CTX = ssl.create_default_context()
    # probe a known-good host to tell "broken local trust store" from "bad site cert"
    try:
        urlopen(Request("https://www.google.com", method="HEAD",
                        headers={"User-Agent": "qa-scan/1.0"}), timeout=10, context=_SSL_CTX)
    except ssl.SSLCertVerificationError:
        _SSL_CTX = ssl._create_unverified_context()
        _SSL_UNVERIFIED = True
        if F is not None:
            F.append(Finding(NOTE, "Environment", "(scanner)",
                             "Local Python trust store cannot verify certificates — TLS validation "
                             "was SKIPPED by the scanner. Verify the cert manually: "
                             "openssl s_client -connect HOST:443 | openssl x509 -noout -dates"))
    except Exception:
        pass
    return _SSL_CTX


def fetch(url, timeout=15, method="GET"):
    req = Request(url, method=method, headers={
        "User-Agent": "Mozilla/5.0 (compatible; qa-scan/1.0; +pre-launch QA)",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Encoding": "gzip",
    })
    with urlopen(req, timeout=timeout, context=ssl_context()) as r:
        body = r.read() if method == "GET" else b""
        if body and r.headers.get("Content-Encoding", "").lower() == "gzip":
            import gzip
            try:
                body = gzip.decompress(body)
            except Exception:
                pass
        return r.status, dict(r.headers), body


NON_HTML_EXT = (".pdf", ".zip", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                ".csv", ".json", ".xml", ".rss", ".jpg", ".jpeg", ".png", ".gif",
                ".webp", ".avif", ".svg", ".ico", ".mp4", ".mp3", ".mov", ".webm",
                ".woff", ".woff2", ".ttf", ".dmg", ".pkg", ".txt")


def scan_url(start, F, site, max_pages=25):
    ssl_context(F)
    origin = "{0.scheme}://{0.netloc}".format(urlparse(start))
    queue, seen, count = [start], set(), 0
    checked_links = {}

    try:
        st, hdrs, _ = fetch(origin, method="GET")
        h = {k.lower(): v for k, v in hdrs.items()}
        for name, sev, why in (
            ("strict-transport-security", MINOR, "No HSTS header"),
            ("x-content-type-options", MINOR, "No X-Content-Type-Options: nosniff"),
            ("referrer-policy", MINOR, "No Referrer-Policy header"),
            ("content-security-policy", MINOR, "No Content-Security-Policy header"),
        ):
            if name not in h:
                F.append(Finding(sev, "Security", "(site)", why))
        if "x-robots-tag" in h and "noindex" in h["x-robots-tag"].lower():
            F.append(Finding(BLOCKER, "SEO", "(site)", "X-Robots-Tag header sets noindex"))
        if "content-encoding" not in h:
            F.append(Finding(MINOR, "Performance", "(site)", "No compression (gzip/br) on the HTML response"))
    except Exception as e:
        F.append(Finding(MAJOR, "Deploy", "(site)", f"Could not fetch origin: {e}"))

    for f, sev in (("/robots.txt", MINOR), ("/sitemap.xml", MINOR)):
        try:
            st, _, body = fetch(origin + f)
            if st != 200:
                F.append(Finding(sev, "SEO", "(site)", f"{f} returns {st}"))
            elif f == "/robots.txt" and robots_blocks_everything(body.decode("utf-8", "replace")):
                F.append(Finding(BLOCKER, "SEO", "robots.txt", "robots.txt blocks the entire site"))
        except Exception:
            F.append(Finding(sev, "SEO", "(site)", f"{f} not reachable"))
    try:
        st, _, _ = fetch(origin + "/this-url-should-not-exist-qa-check")
        F.append(Finding(MAJOR, "SEO", "(site)", f"Unknown URL returns {st}, not 404 (soft 404)"))
    except HTTPError as e:
        if e.code != 404:
            F.append(Finding(MINOR, "SEO", "(site)", f"Unknown URL returns {e.code}, expected 404"))
    except Exception:
        pass

    while queue and count < max_pages:
        url = queue.pop(0)
        url, _ = urldefrag(url)
        if url in seen:
            continue
        seen.add(url)
        try:
            st, hdrs, body = fetch(url)
        except HTTPError as e:
            F.append(Finding(BLOCKER, "Functionality", url, f"Page returns HTTP {e.code}"))
            continue
        except Exception as e:
            F.append(Finding(BLOCKER, "Functionality", url, f"Page failed to load: {e}"))
            continue
        ctype = ({k.lower(): v for k, v in hdrs.items()}).get("content-type", "").lower()
        if "html" not in ctype:
            continue          # PDFs, images, feeds: presence verified, not HTML-checked
        count += 1
        html = body.decode("utf-8", "replace")
        pg = Page(urlparse(url).path or "/", html, len(body), base_url=url)
        check_page(pg, F, site)

        for a in pg.p.anchors:
            href = (a["attrs"].get("href") or "").strip()
            if not href or href.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
                continue
            absu, _ = urldefrag(urljoin(url, href))
            if absu.startswith(origin) and not absu.lower().split("?")[0].endswith(NON_HTML_EXT):
                if absu not in seen and absu not in queue and count + len(queue) < max_pages * 2:
                    queue.append(absu)
            if absu in checked_links:
                continue
            checked_links[absu] = True
            if len(checked_links) > 200:
                continue
            internal = absu.startswith(origin)
            code = None
            try:
                fetch(absu, timeout=10, method="HEAD")
            except HTTPError as e:
                code = e.code
                if code in (403, 405, 429, 501, 999):   # HEAD refused / bot-blocked
                    try:
                        fetch(absu, timeout=12, method="GET")
                        code = None
                    except HTTPError as e2:
                        code = e2.code
                    except Exception:
                        code = None
                if code is not None:
                    if code in (403, 429, 999) and not internal:
                        F.append(Finding(NOTE, "Functionality", pg.key,
                                         f"External link returned {code} to the scanner "
                                         f"(likely bot protection) — verify by hand", absu[:80]))
                    else:
                        F.append(Finding(BLOCKER if internal else MAJOR, "Functionality", pg.key,
                                         f"Broken link — HTTP {code}", absu[:80]))
            except Exception:
                F.append(Finding(MINOR, "Functionality", pg.key,
                                 "Link could not be verified (timeout/DNS)", absu[:80]))
    return count


# ------------------------------------------------------------------ report
def report(F, pages, target, as_json):
    seen_j, uj = set(), []
    for f in F:
        k = (f.sev, f.gate, f.page, f.msg, f.detail)
        if k not in seen_j:
            seen_j.add(k); uj.append(f)
    F[:] = uj
    if as_json:
        print(json.dumps({"target": target, "pages_scanned": pages,
                          "findings": [f.as_dict() for f in F]}, indent=2))
        return 1 if any(f.sev == BLOCKER for f in F) else 0

    seen_f, uniq = set(), []
    for f in F:
        k = (f.sev, f.gate, f.page, f.msg, f.detail)
        if k not in seen_f:
            seen_f.add(k); uniq.append(f)
    F[:] = uniq
    counts = {s: sum(1 for f in F if f.sev == s) for s in (BLOCKER, MAJOR, MINOR, NOTE)}
    W = 78
    print("=" * W)
    print(f" QA SCAN — {target}")
    print(f" {pages} page(s) scanned · "
          f"{counts[BLOCKER]} blocker · {counts[MAJOR]} major · "
          f"{counts[MINOR]} minor · {counts[NOTE]} note")
    print("=" * W)

    F.sort(key=lambda f: (ORDER[f.sev], f.gate, f.page, f.msg))
    # collapse identical issues repeated across pages
    grouped = {}
    for f in F:
        k = (f.sev, f.gate, f.msg)
        grouped.setdefault(k, []).append(f)

    last_sev = None
    for (sev, gate, msg), items in sorted(grouped.items(), key=lambda kv: (ORDER[kv[0][0]], kv[0][1])):
        if sev != last_sev:
            print(f"\n--- {sev} " + "-" * (W - len(sev) - 5))
            last_sev = sev
        pages_hit = sorted({i.page for i in items})
        loc = pages_hit[0] if len(pages_hit) == 1 else f"{len(pages_hit)} pages"
        print(f"{ICON[sev]} {gate:<16} {msg}")
        print(f"{'':11}{'':<16} in: {loc}"
              + (f"  ({', '.join(pages_hit[:4])}{'…' if len(pages_hit) > 4 else ''})"
                 if len(pages_hit) > 1 else ""))
        details = [i.detail for i in items if i.detail][:3]
        for d in details:
            print(f"{'':11}{'':<16}   · {d}")
        if len([i for i in items if i.detail]) > 3:
            print(f"{'':11}{'':<16}   · …and {len([i for i in items if i.detail]) - 3} more")

    print("\n" + "=" * W)
    if counts[BLOCKER]:
        print(" RESULT: DO NOT LAUNCH — blockers open.")
    elif counts[MAJOR]:
        print(" RESULT: Fix majors before launch.")
    else:
        print(" RESULT: Clean automated scan.")
    print(" This scan is ~40% of QA. Run the manual gates in references/01-11.")
    print("=" * W)
    return 1 if counts[BLOCKER] else 0


def main():
    ap = argparse.ArgumentParser(description="Mechanical pre-launch QA scanner")
    ap.add_argument("target", help="local site directory or https:// URL")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--max-pages", type=int, default=25, help="crawl cap for URL mode")
    ap.add_argument("--ignore", action="append", default=[], metavar="GLOB",
                    help="skip paths matching this glob (repeatable). A .qaignore file "
                         "in the site root is also read, one glob per line.")
    args = ap.parse_args()

    F, site = [], {}
    site["ignore"] = list(args.ignore)
    t = args.target
    if t.startswith(("http://", "https://")):
        pages = scan_url(t, F, site, args.max_pages)
    else:
        root = os.path.abspath(os.path.expanduser(t))
        if not os.path.isdir(root):
            print(f"Not a directory or URL: {t}", file=sys.stderr)
            sys.exit(2)
        qi = os.path.join(root, ".qaignore")
        if os.path.exists(qi):
            site["ignore"] += [l.strip() for l in open(qi)
                               if l.strip() and not l.startswith("#")]
        pages = scan_local(root, F, site)
    sys.exit(report(F, pages, t, args.json))


if __name__ == "__main__":
    main()

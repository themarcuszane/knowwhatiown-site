#!/usr/bin/env python3
"""Static QA for the site in ./site. Standard library only; exits non-zero on any failure.

Run: python3 tests/qa.py [site_dir]
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

SITE = Path(sys.argv[1] if len(sys.argv) > 1 else "site").resolve()
ORIGIN = "https://knowwhatiown.com"
PAGES = ["index.html", "support.html", "privacy.html", "404.html"]
REQUIRED_FILES = PAGES + ["robots.txt", "sitemap.xml", ".nojekyll"]
INDEXED = ["index.html", "support.html", "privacy.html"]
ALLOWED_EXTERNAL = {"teamdrybox.com", "www.sitemaps.org", "knowwhatiown.com"}
PRIVACY_SECTIONS = [
    "Inventory Data", "Photos", "Maintenance Reminders", "Purchases", "Exports and Backups",
    "Device Backups", "Support Messages", "Retention and Deletion", "This Website", "Children", "Changes",
]
BUDGET_BYTES = {"html": 40_000, "css": 40_000, "image": 200_000, "font": 30_000}

failures = []


def fail(msg):
    failures.append(msg)
    print(f"FAIL  {msg}")


def ok(msg):
    print(f"ok    {msg}")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags, self.ids, self.hrefs, self.srcs = [], [], [], []
        self.meta, self.links, self.imgs_no_alt, self.h = {}, [], [], []
        self.title, self._in_title, self.lang = "", False, None
        self._stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if tag == "html":
            self.lang = a.get("lang")
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
        if tag in ("img", "script", "source") and "src" in a:
            self.srcs.append(a["src"])
        if tag == "link" and "href" in a:
            self.links.append((a.get("rel", ""), a["href"]))
        if tag == "img" and a.get("alt") is None:
            self.imgs_no_alt.append(a.get("src", "?"))
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        if tag == "title":
            self._in_title = True
        if re.fullmatch(r"h[1-6]", tag):
            self.h.append(int(tag[1]))
        if tag not in {"meta", "link", "img", "br", "hr", "input", "source"}:
            self._stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self._stack:
            while self._stack and self._stack[-1] != tag:
                self._stack.pop()
                self.unclosed = getattr(self, "unclosed", 0) + 1
            if self._stack:
                self._stack.pop()

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def resolve(base_file: Path, ref: str):
    """Map an internal reference to a file under SITE, or None if external/non-file."""
    u = urlparse(ref)
    if u.scheme in ("mailto", "tel", "data", "javascript"):
        return None
    if u.scheme in ("http", "https"):
        if u.netloc != "knowwhatiown.com":
            return None
        path = u.path
    else:
        path = u.path
    if path == "":
        return base_file
    target = SITE / path.lstrip("/") if path.startswith("/") else (base_file.parent / path)
    target = Path(unquote(str(target)))
    if target.is_dir():
        target = target / "index.html"
    return target.resolve()


# 1. required files
for f in REQUIRED_FILES:
    (ok if (SITE / f).exists() else fail)(f"required file present: {f}")

parsed = {}
for name in PAGES:
    p = SITE / name
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    pg = Page()
    pg.feed(text)
    parsed[name] = (pg, text)

for name, (pg, text) in parsed.items():
    where = f"[{name}]"
    if not text.lower().startswith("<!doctype html"):
        fail(f"{where} missing doctype")
    if pg.lang != "en":
        fail(f"{where} <html lang> should be 'en', got {pg.lang!r}")
    if not pg.title.strip():
        fail(f"{where} empty <title>")
    if not pg.meta.get("description"):
        fail(f"{where} missing meta description")
    if not pg.meta.get("viewport"):
        fail(f"{where} missing viewport meta")
    if pg.h.count(1) != 1:
        fail(f"{where} expected exactly one <h1>, found {pg.h.count(1)}")
    for prev, cur in zip(pg.h, pg.h[1:]):
        if cur - prev > 1:
            fail(f"{where} heading level jumps h{prev} -> h{cur}")
            break
    if len(pg.ids) != len(set(pg.ids)):
        dup = {i for i in pg.ids if pg.ids.count(i) > 1}
        fail(f"{where} duplicate ids: {sorted(dup)}")
    if pg.imgs_no_alt:
        fail(f"{where} images without alt attribute: {pg.imgs_no_alt}")
    if getattr(pg, "unclosed", 0):
        fail(f"{where} {pg.unclosed} unclosed/mismatched tags")
    if "script" in pg.tags:
        fail(f"{where} contains <script>; the site is script-free by policy")
    if re.search(r"(?i)\b(gtag|analytics|googletagmanager|fbq|hotjar|cookie)\b", re.sub(r"(?s)<p[^>]*>.*?</p>", "", text)):
        fail(f"{where} references a tracking/cookie keyword outside prose")
    if name in INDEXED:
        canon = [h for r, h in pg.links if r == "canonical"]
        want = ORIGIN + ("/" if name == "index.html" else f"/{name}")
        if canon != [want]:
            fail(f"{where} canonical should be {want}, got {canon}")
        for key in ("og:title", "og:description", "og:image", "og:url"):
            if not pg.meta.get(key):
                fail(f"{where} missing {key}")
        if not pg.meta.get("og:image", "").startswith(ORIGIN + "/"):
            fail(f"{where} og:image must be an absolute {ORIGIN} URL")
    if name == "404.html" and "noindex" not in pg.meta.get("robots", ""):
        fail(f"{where} 404 page should be noindex")

    # links / assets / fragments
    for ref in pg.hrefs + pg.srcs + [h for _, h in pg.links]:
        u = urlparse(ref)
        if u.scheme in ("http", "https") and u.netloc not in ALLOWED_EXTERNAL:
            fail(f"{where} external reference not allowed: {ref}")
            continue
        target = resolve(SITE / name, ref)
        if target is None:
            continue
        if not target.exists():
            fail(f"{where} broken reference: {ref}")
            continue
        if u.fragment and target.suffix == ".html":
            tgt = parsed.get(target.name)
            if tgt and u.fragment not in tgt[0].ids:
                fail(f"{where} missing fragment target: {ref}")
    ok(f"{where} structure, metadata, links")

# 2. CSS: no external fetches
css = SITE / "assets" / "styles.css"
if css.exists():
    ctext = css.read_text(encoding="utf-8")
    ext = re.findall(r"url\(\s*['\"]?(https?:)?//", ctext) + re.findall(r"@import", ctext)
    (fail if ext else ok)("styles.css makes no external requests" if not ext else "styles.css loads external resources")
    for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)", ctext):
        ref = m.group(1)
        if ref.startswith(("data:", "http")):
            continue
        t = (css.parent / ref).resolve()
        if not t.exists():
            fail(f"styles.css broken url(): {ref}")

# 3. sitemap and robots
sm = (SITE / "sitemap.xml").read_text(encoding="utf-8") if (SITE / "sitemap.xml").exists() else ""
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
want = {ORIGIN + "/", ORIGIN + "/support.html", ORIGIN + "/privacy.html"}
(ok if set(locs) == want else fail)(f"sitemap lists exactly the 3 public pages ({sorted(locs)})")
robots = (SITE / "robots.txt").read_text(encoding="utf-8") if (SITE / "robots.txt").exists() else ""
(ok if f"Sitemap: {ORIGIN}/sitemap.xml" in robots else fail)("robots.txt points at the sitemap")

# 4. privacy policy must keep its required sections and a current date
if "privacy.html" in parsed:
    ptxt = re.sub(r"<[^>]+>", " ", parsed["privacy.html"][1])
    for sec in PRIVACY_SECTIONS:
        if sec not in ptxt:
            fail(f"privacy.html missing required section: {sec}")
    if not re.search(r"Last updated: \w+ \d{1,2}, 20\d\d", ptxt):
        fail("privacy.html missing 'Last updated' line")
    if "admin@teamdrybox.com" not in ptxt:
        fail("privacy.html missing contact address")
    ok("privacy.html required sections present")
if "support.html" in parsed:
    stxt = re.sub(r"<[^>]+>", " ", parsed["support.html"][1])
    for needle in ("admin@teamdrybox.com", "Restore Purchase", "Export Backup"):
        if needle not in stxt:
            fail(f"support.html missing: {needle}")

# 5. brand hygiene: stale or wrong names must not appear in public pages
for name, (pg, text) in parsed.items():
    for bad in ("Zavro", "careeros", "Lorem ipsum", "TODO", "REPLACE_ME"):
        if bad in text:
            fail(f"[{name}] contains disallowed text: {bad}")
    if "Coming soon" in text and name == "index.html":
        if "<!-- REPLACE with the official" not in text:
            fail("[index.html] 'Coming soon' button lacks the REPLACE marker for launch day")

# 6. size budgets
for f in SITE.rglob("*"):
    if not f.is_file():
        continue
    kind = {".html": "html", ".css": "css", ".woff2": "font", ".jpg": "image", ".png": "image"}.get(f.suffix)
    if kind and f.stat().st_size > BUDGET_BYTES[kind]:
        fail(f"{f.relative_to(SITE)} is {f.stat().st_size} bytes (budget {BUDGET_BYTES[kind]})")
ok("size budgets checked")

print()
if failures:
    print(f"{len(failures)} failure(s)")
    sys.exit(1)
print("QA passed")

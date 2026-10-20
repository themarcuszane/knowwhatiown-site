# QA

## Automated (run on every PR and push)
`python3 tests/qa.py site` checks: required files, valid structure (doctype, lang, one h1, heading
order, unique ids, alt text, balanced tags), every internal link, asset and `#fragment`, canonical and
Open Graph tags, no `<script>`, no external requests (HTML and CSS), sitemap and robots, required
privacy-policy sections and date line, brand hygiene (no stale product names or placeholders),
size budgets, and the launch-day REPLACE marker.

## Live smoke (after deploy, and weekly)
`tests/smoke.sh [base_url]` checks the real domain: 200 for every page and asset, branded 404, HTTP->HTTPS
and www->apex redirects, no cookies, no scripts, no third-party references, content markers,
DNS pointing at GitHub Pages, and at least 14 days of certificate validity. Read-only.

## Manual (before the App Store submission, and after any visual change)
- [ ] Open the three URLs in Safari on iPhone and on a Mac: layout, fonts, images load.
- [ ] Light and dark appearance both readable; no horizontal scroll at 320 px width.
- [ ] Keyboard only: skip link works, focus is visible, FAQ items open and close.
- [ ] Support and privacy text matches the shipped app build (photos, reminders, export, backups,
      purchase and restore wording).
- [ ] Contact address `admin@teamdrybox.com` receives mail (send a test).
- [ ] Share a link in Messages: preview card shows the title, description and image.
- [ ] The URLs entered in App Store Connect match exactly: `/support.html`, `/privacy.html`, `/`.

## Known limits
- The 404 page uses root-relative links, so it looks unstyled at a non-root URL.
- Subsetted fonts drop kerning. The OFL licence texts for the bundled fonts should be added under
  `site/assets/fonts/` before launch (IBM Plex has a Reserved Font Name).

# Architecture

## What this is
A three-page static site (landing, support, privacy) plus a 404 page, robots.txt and sitemap.
Fonts, images and CSS are self-hosted under `site/assets/`. Nothing is fetched from another origin,
so the privacy policy's "no third-party requests" statement is true by construction and enforced by
`tests/qa.py` and `tests/smoke.sh`.

## Hosting
- GitHub Pages, deployed by GitHub Actions (`.github/workflows/site.yml`) from the `site/` folder.
- Repository: `themarcuszane/knowwhatiown-site` (public, because Pages on the free plan requires it).
  It contains only the website. The app's source code is in a different, private repository.
- Pages settings: build type "GitHub Actions", custom domain `knowwhatiown.com`, Enforce HTTPS on.
  With Actions deployment a `CNAME` file in the repo is not used; the custom domain lives in settings.

## DNS (registrar and DNS host: GoDaddy)
| Name | Type | Value |
| --- | --- | --- |
| `@` | A | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 |
| `www` | CNAME | knowwhatiown.com. (GitHub redirects www to the apex) |

No MX or TXT records exist, so there is no email on this domain. Support mail goes to
admin@teamdrybox.com (hosted on the teamdrybox.com domain, not this one).

### Rollback values (GoDaddy "Launching Soon" placeholder, as of 2026-10-19)
`@ A 76.223.105.230` and `@ A 13.248.243.5`; `www CNAME knowwhatiown.com.`.
Restoring these takes the site offline (the placeholder returns 404 for the support and privacy URLs),
so only do it if GitHub Pages itself is the problem and you have an alternative host ready.

## Who can break it, and how
- Domain expiry: check the registrar; set a calendar reminder at least 60 days before.
- GitHub Pages certificate: renews automatically. `tests/smoke.sh` fails if it has under 14 days left.
- Someone changing GoDaddy DNS: weekly smoke test checks the apex still points at GitHub Pages.
- A bad merge: CI runs QA before deploy, and the live smoke test after.

## Why not Vercel or Cloudflare
Free, no commercial-use restriction, nothing extra to maintain for three static pages.
Vercel's free Hobby plan is for non-commercial use, and this site markets a paid app.

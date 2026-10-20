# knowwhatiown-site

Public website for **Know What I Own**, an iPhone home-inventory app by Team Drybox LLC.
Live at <https://knowwhatiown.com>. Static HTML/CSS only: no build step, no scripts, no cookies,
no analytics, no third-party requests.

The App Store listing depends on these URLs staying live:

| Use | URL |
| --- | --- |
| Marketing | https://knowwhatiown.com/ |
| Support | https://knowwhatiown.com/support.html |
| Privacy Policy | https://knowwhatiown.com/privacy.html |

## Layout

```
site/        everything that is published (this folder is the Pages artifact)
docs/        architecture, release process, QA checklist
tests/       qa.py (static checks), smoke.sh (live checks)
.github/     CI: QA on every PR, deploy + live smoke test on main, weekly smoke
```

## Change the site

1. Branch, edit files under `site/`.
2. `python3 tests/qa.py site` must pass.
3. Preview: `python3 -m http.server 8765 --directory site`, then open http://localhost:8765.
4. Open a PR. CI runs QA. Merging to `main` deploys, then runs the live smoke test.

Details and rollback are in [docs/RELEASE.md](docs/RELEASE.md). Hosting and DNS are in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). The manual checks QA cannot do are in
[docs/QA.md](docs/QA.md).

## Source of truth for policy text

The privacy and support pages describe what the app actually does. If app behaviour changes
(networking, analytics, new data types, new permissions), update `site/privacy.html` and the
App Store privacy answers in the same release. The app's source lives in a private repository.

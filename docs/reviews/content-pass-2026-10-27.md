# Content review — October 27, 2026

This patch follows the owner's review of Know What I Own's website. Branch
`codex/support-content-2026-10-27`, based on main `53631eb`. No publication or
App Store configuration change is included.

## Fixed or cleared

- Added /favicon.ico using the existing 32px PNG artwork, unchanged, in a standard
  ICO container. All four HTML pages advertise the ICO fallback and retain their
  existing PNG/Apple icons. No new third-party requests, scripts or cookies.
- Support already says “Last updated: October 19, 2026” at the bottom. The review
  missed that line. It remains unchanged: there was no support-policy rewrite.
- admin@teamdrybox.com is consistent across this product's support/privacy pages.
  The company uses marcus@teamdrybox.com for company inquiries; RoleBop has its
  own support address. No mailbox replacement was invented or created.
- App Store support and privacy URLs remain exactly /support.html and
  /privacy.html. “Coming soon” remains; no claim of App Store approval was added.

## App claims — source evidence and limits

Read-only inspection of the private native working copy found the free limits
of one property / 25 items, a check before adding items, a Restore Purchase path
using Apple's sync/verified entitlement flow, Apple-framework imports, and a
privacy manifest declaring no tracking/collected data. No analytics/advertising
SDK or package reference was found in the inspected source/configuration.

This supports the current wording but does NOT certify the actual distributed
binary, runtime purchase/restore behavior, refund transitions, item-limit UI or
App Store privacy answers. The working copy contains unrelated edits; it was not
modified, built, submitted or uploaded by this website pass. Owner-assisted
purchase/restore and final built-app/Privacy-label verification remain release
checks. No credentials or private app source were copied into this public repo.

## Source and hosting

The current source of truth is this repository's site/ directory. GitHub Pages
publishes that directory through .github/workflows/site.yml. Its registered
custom domain is knowwhatiown.com; the Pages configuration was read only.
The older private app web/ directory matches the pre-patch HTML files but is not
the deployed artifact. Future copies from that older mirror must preserve this
favicon addition; do not overwrite the public site wholesale from stale sources.
The lab's site/ folder is unrelated and was not changed.

## Verification — local, not CI

- python3 -I tests/qa.py site passes (HTML structure, metadata, local assets,
  navigation, sitemap, privacy sections, size budgets and no external requests).
- /favicon.ico serves HTTP 200 as image/x-icon on the local static server.
- Chromium at 1440, 390 and 320px: support date remains present, no horizontal
  overflow, fallback icon available. Phone light/dark screenshots inspected.
- No scripts, dependencies or copy-only test cases were added. No app account or
  purchase was created. All native app and App Store checks above remain pending.
- Existing public smoke/production tests were not run; no deployment command,
  domain/provider setting, DNS record, merge or App Store record was changed.

Rollback: revert the content commit; no data changes. Existing source/privacy
claims remain subject to final app-build and owner review.

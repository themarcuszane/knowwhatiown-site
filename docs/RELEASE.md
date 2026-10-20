# Release process

## Normal change
1. Branch from `main`, edit `site/`.
2. `python3 tests/qa.py site` locally. Preview with `python3 -m http.server 8765 --directory site`.
3. PR to `main`; CI runs QA. Merge.
4. Merge triggers deploy, then `tests/smoke.sh` against the live domain. A red smoke job means the
   live site is not healthy: look at it immediately.

## Policy text changes (privacy.html, support.html)
- Verify each claim against the app's behaviour before merging. Never describe a feature the app lacks.
- Update the "Last updated" line and, for privacy, the "effective" date in the same PR.
- If the change affects what data the app handles, the App Store Connect "App Privacy" answers
  must change in the same release.

## Launch day (when the app is approved)
1. Replace the disabled "Coming soon" button in `site/index.html` (look for the `<!-- REPLACE ... -->`
   comment) with the official App Store badge and link. QA will start failing on the marker until the
   comment is removed; that is intentional, so update the check in `tests/qa.py` in the same PR.
2. Replace the three screenshots in `site/assets/shots/` and `site/assets/og.jpg` with final ones
   (same filenames; keep under the size budgets in `tests/qa.py`).

## Rollback
- Revert the merge commit on `main` (`git revert -m 1 <sha>`) and push; CI redeploys the previous
  version in about a minute.
- Or re-run the "site" workflow on an older commit via Actions -> Run workflow.
- DNS rollback is a last resort; see docs/ARCHITECTURE.md.

## Manual checks after a deploy
See docs/QA.md.

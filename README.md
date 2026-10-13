# Panipani — Canva-based Instagram Reels automation

**Operational status (2026-10-13 JST): QUALITY APPROVAL / FINAL LIVE TEST PENDING.**

- Public Instagram Reel publishing: **OFF**. There is no active schedule in the production workflow, and its publish job has a fail-closed `if: ${{ false }}`.
- Canva Connect OAuth: **LIVE VERIFIED**. The first official API autofill -> MP4 test succeeded in [Actions run #2](https://github.com/o9o84441100-droid/panipani-instagram-auto/actions/runs/38343291608).
- Three existing Canva designs have auto-fill fields `HOOK`, `SITUATION`, `PROMPT`, `CAUTION`, `CTA`.
- Original live-test video visually revealed title overlay and overlong CTA. All three Canva source designs have corrective edits staged in unsaved Canva transactions; **preview + explicit user approval are required before permanent save**.
- `canva_copy.py` provides human-reviewed microcopy for all **86** topics; long prompts remain complete in captions and no longer overflow fixed-size Canva visuals. Unit tests enforce character bounds.
- The nonpublishing [Canva live export test workflow](.github/workflows/canva-live-export-test.yml) can run **all three templates in one manual test** and save three Canva MP4 videos as private GitHub Actions artifacts.
- The template preview, final live test, first real Canva-originated Instagram post, and return to automatic 5/day scheduling are **not complete yet**. Do not represent the system as 100% complete.

## Approved source assets and official access

- Canva originals: `DAHX1n4SSpU`, `DAHX1rftBb4` (two pages), `DAHX1vFRj1g`.
- GitHub repository variable: `CANVA_TEMPLATE_IDS` includes those three IDs.
- Four secret names (never reveal values): `CANVA_CLIENT_ID`, `CANVA_CLIENT_SECRET`, `CANVA_REFRESH_TOKEN`, `CANVA_TOKEN_KEY`.
- A single-use Canva refresh token is rotated and the next refresh token is encrypted and persisted in `state/canva/refresh_token.enc`. OAuth workflows MUST use concurrency group `panipani-canva-oauth` and checkout with full history.
- Every visual is exported by the **official Canva Connect API**, never simulated in Pillow or through an imitation Canva layout. `publisher.py` requires a matching Canva provenance manifest and MP4 SHA-256.
- The last successful Canva live test generated a Canva MP4, but did **not** publish that Canva video to Instagram.

## Next safe release sequence

1. Inspect the **four pages of the three Canva draft templates** and get user approval. Commit only after approval.
2. Run [Canva live export TEST](.github/workflows/canva-live-export-test.yml) → `Run workflow` → `template = all`.
3. Inspect downloaded video artifact for all three designs: text overlapping, letter clipping, CTA safe zone, Japanese typography, original visual quality, H.264/AAC, and at least 3 seconds of duration.
4. Only after success, run a read-only Instagram API account check and a single carefully supervised Canva-source public post.
5. Verify public Instagram permalink, the publication ledger and duplicate checks. Explicitly approve restoring the five original daily triggers.

## Planned five daily Japan-time slots (CURRENTLY INACTIVE)

| JST | UTC trigger |
|---|---|
| 08:05 | 23:05 previous UTC day |
| 10:05 | 01:05 |
| 12:05 | 03:05 |
| 18:05 | 09:05 |
| 21:05 | 12:05 |

`.github/workflows/panipani-daily-reels.yml` is NOT currently running on a schedule. The missed-post audit suppresses false alarms while publishing is intentionally paused.

## Other monitoring and operations

- [Performance review](.github/workflows/performance-review.yml): read-only Instagram metrics collection each night.
- [Weekly optimizer](.github/workflows/weekly-optimizer.yml): may recommend categories with sufficient evidence; no premature claims of improvement.
- [Missing-post audit](.github/workflows/post-audit.yml): only reports missed posts if scheduled public publishing is enabled.
- [Validation workflow](.github/workflows/validate-canva-only.yml): verifies media source policies and 86-topic visual text bounds.
- `daily_topics.py` is an editorially curated deterministic library, not live social-trend research.
- GitHub Actions and Instagram APIs have rate limits, can fail, and cannot guarantee minute-perfect uptime.
- Instagram long-lived tokens and Canva integrations may require future renewal; never store them in source files.

For the detailed deployment checklist, see [CANVA_ONLY_SETUP.md](CANVA_ONLY_SETUP.md).

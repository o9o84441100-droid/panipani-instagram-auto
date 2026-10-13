# Panipani — Canva-based Instagram Reels automation

**Operational status (2026-10-13 JST): REAL Canva Reel PUBLICATION VERIFIED; recurring schedule still PAUSED.**

- Public Instagram Reel publishing: **OFF**. There is no active schedule in the production workflow, and its publish job has a fail-closed `if: ${{ false }}`.
- Canva Connect OAuth: **LIVE VERIFIED**. The first official API autofill -> MP4 test succeeded in [Actions run #2](https://github.com/o9o84441100-droid/panipani-instagram-auto/actions/runs/38343291608).
- Three existing Canva designs have auto-fill fields `HOOK`, `SITUATION`, `PROMPT`, `CAUTION`, `CTA`.
- Original live-test video visually revealed title overlay and overlong CTA. All three Canva source designs have corrective edits staged in unsaved Canva transactions; **preview + explicit user approval are required before permanent save**.
- `canva_copy.py` provides human-reviewed microcopy for all **86** topics; long prompts remain complete in captions and no longer overflow fixed-size Canva visuals. Unit tests enforce character bounds.
- The nonpublishing [Canva live export test workflow](.github/workflows/canva-live-export-test.yml) can run **all three templates in one manual test** and save three Canva MP4 videos as private GitHub Actions artifacts.
- All three Canva designs were tested and visually revised; an authentic Canva MP4 was successfully published via GitHub Actions using the official Instagram API. **Daily 5-post scheduling is still OFF** and ongoing unattended reliability is not yet verified.

## Approved source assets and official access

- Canva originals: `DAHX1n4SSpU`, `DAHX1rftBb4` (two pages), `DAHX1vFRj1g`.
- GitHub repository variable: `CANVA_TEMPLATE_IDS` includes those three IDs.
- Four secret names (never reveal values): `CANVA_CLIENT_ID`, `CANVA_CLIENT_SECRET`, `CANVA_REFRESH_TOKEN`, `CANVA_TOKEN_KEY`.
- A single-use Canva refresh token is rotated and the next refresh token is encrypted and persisted in `state/canva/refresh_token.enc`. OAuth workflows MUST use concurrency group `panipani-canva-oauth` and checkout with full history.
- Every visual is exported by the **official Canva Connect API**, never simulated in Pillow or through an imitation Canva layout. `publisher.py` requires a matching Canva provenance manifest and MP4 SHA-256.
- **First verified official Canva-source Instagram Reel:** https://www.instagram.com/reel/Dea_Ef5ALan/ (media ID `18141508402609681`) via [one-time GitHub Actions run 38348128190](https://github.com/o9o84441100-droid/panipani-instagram-auto/actions/runs/38348128190). Publication record: `state/posts/canva_public_test_20261013.json`.

## Next safe release sequence

1. Inspect the **four pages of the three Canva draft templates** and get user approval. Commit only after approval.
2. Run [Canva live export TEST](.github/workflows/canva-live-export-test.yml) → `Run workflow` → `template = all`.
3. Inspect downloaded video artifact for all three designs: text overlapping, letter clipping, CTA safe zone, Japanese typography, original visual quality, H.264/AAC, and at least 3 seconds of duration.
4. **COMPLETED**: read-only Instagram API account verification and exactly one supervised, genuine Canva-source public Reel through GitHub Actions.
5. **COMPLETED**: verified public Reel URL and committed publication ledger; the single-use publication workflow was retired.
6. **PENDING**: harden the daily pipeline, then explicitly approve restoring five scheduled daily triggers. Do not reenable automatically based solely on a single successful post.

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

## Provider rule
Instagram publications use **GitHub Actions + official Canva Connect + Instagram official API**. Do **not** use Metricool for Panipani posting.

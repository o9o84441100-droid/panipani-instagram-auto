# Panipani — Canva-based Instagram Reels automation

**Operational status (2026-10-13 JST): FIVE DAILY CANVA REEL TRIGGERS ENABLED, waiting for first unattended scheduled run.**

- Public Instagram Reel publishing: **ON**, with five GitHub Actions cron triggers. `PANIPANI_PUBLICATION_ENABLED: 'true'` is the rollback switch. Only slots approved by the JST/durable-ledger guard can publish. Automated cron posts are not yet independently confirmed.
- Canva Connect OAuth: **LIVE VERIFIED**. The first official API autofill -> MP4 test succeeded in [Actions run #2](https://github.com/o9o84441100-droid/panipani-instagram-auto/actions/runs/38343291608).
- Three existing Canva designs have auto-fill fields `HOOK`, `SITUATION`, `PROMPT`, `CAUTION`, `CTA`.
- The user approved and saved all Canva design revisions, including final headline and CTA spacing; corrected videos passed actual 1080×1920 MP4 export and manual visual checks.
- `canva_copy.py` provides human-reviewed microcopy for all **86** topics; long prompts remain complete in captions and no longer overflow fixed-size Canva visuals. Unit tests enforce character bounds.
- The nonpublishing [Canva live export test workflow](.github/workflows/canva-live-export-test.yml) can run **all three templates in one manual test** and save three Canva MP4 videos as private GitHub Actions artifacts.
- A genuine Canva MP4 was successfully published with GitHub Actions/Instagram official API; now the **five daily GitHub Actions triggers have been enabled**. Continuous unattended reliability still needs observation across scheduled runs.

## Approved source assets and official access

- Canva originals: `DAHX1n4SSpU`, `DAHX1rftBb4` (two pages), `DAHX1vFRj1g`.
- GitHub repository variable: `CANVA_TEMPLATE_IDS` includes those three IDs.
- Four secret names (never reveal values): `CANVA_CLIENT_ID`, `CANVA_CLIENT_SECRET`, `CANVA_REFRESH_TOKEN`, `CANVA_TOKEN_KEY`.
- A single-use Canva refresh token is rotated and the next refresh token is encrypted and persisted in `state/canva/refresh_token.enc`. OAuth workflows MUST use concurrency group `panipani-canva-oauth` and checkout with full history.
- Every visual is exported by the **official Canva Connect API**, never simulated in Pillow or through an imitation Canva layout. `publisher.py` requires a matching Canva provenance manifest and MP4 SHA-256.
- **First verified official Canva-source Instagram Reel:** https://www.instagram.com/reel/Dea_Ef5ALan/ (media ID `18141508402609681`) via [one-time GitHub Actions run 38348128190](https://github.com/o9o84441100-droid/panipani-instagram-auto/actions/runs/38348128190). Publication record: `state/posts/canva_public_test_20261013.json`.

## Five daily Japan-time Reel slots — ENABLED on 2026-10-13

| JST scheduled trigger | UTC cron |
|---|---|
| 08:05 | `5 23 * * *` previous UTC day |
| 10:05 | `5 1 * * *` |
| 12:05 | `5 3 * * *` |
| 18:05 | `5 9 * * *` |
| 21:05 | `5 12 * * *` |

**Initial rollout:** scheduled triggers begin taking effect once this commit reaches `main`. The first remaining full day is 2026-10-14; the Oct 13 missing-post audit is intentionally suppressed to avoid false alarms before activation. Oct 13 evening slots may be published after the enable commit, subject to Github's scheduler timing.

Production workflow: [Panipani genuine Canva Reels](.github/workflows/panipani-daily-reels.yml).

Each allowed slot requires the operator switch enabled, the right JST date/time (a bounded 120-minute delay allowance), and no existing slot ledger. Each approved post is an **official Canva Connect render**, validated using content and SHA-256 provenance, deployed to GitHub Pages and compared byte-for-byte with public HTTPS delivery, then published through the Instagram official API. The job commits the Instagram media ID and permalink when returned. GitHub Actions serialization protects the rotating single-use Canva refresh token.

**Emergency pause:** change `PANIPANI_PUBLICATION_ENABLED` from `'true'` to `'false'` in the workflow. This prevents further automatic posting without revoking credentials; do not remove the scheduled workflow or delete posting ledgers.

**Failure safety:** a failed publishing job opens a GitHub Issue linking the failed run. The independent next-morning audit checks the five slots from Oct 14 onward and opens an issue for any absent record. Missing ledger records do NOT prove that an Instagram post failed, so manual verification must precede retries.

**Status:** Schedule configured and Canva-only CI checks passed. The first *unattended scheduled* publication has not yet been observed. GitHub Actions cron may be delayed or skipped, and Instagram/Canva quotas and credentials may fail in future.

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

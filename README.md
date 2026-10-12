# Panipani — Instagram Reels Automation

Instagram: **@reiv2220**.

## Verified results
- Instagram Login Graph API authentication: passed.
- First public Reel: **https://www.instagram.com/reel/DeaSUxmla37/** (media ID: `17993216592104252`).
- First full GitHub Actions pipeline: successful.
- Daily generator dry-run: passed all 4 tests, 1080×1920 H.264 + AAC, 20 seconds.
- New 5-post schedule **enabled in configuration**; recurring public posts need ongoing live monitoring, so do not claim every slot has succeeded yet.

## Recurring schedule (Japan Standard Time, UTC+9)
| JST | UTC scheduled trigger |
| --- | --- |
| 08:05 | 23:05 on previous UTC day |
| 10:05 | 01:05 |
| 12:05 | 03:05 |
| 18:05 | 09:05 |
| 21:05 | 12:05 |

GitHub's scheduled runners are best effort; actual execution can be delayed or occasionally missed. A dispatch run can also select a slot manually, but will skip if that slot is already recorded as posted.

Active workflow: `.github/workflows/panipani-daily-reels.yml`.

## What each scheduled run does
1. Check the current JST date and slot against `state/posts/YYYY-MM-DD_HHMM.json`.
2. Select one of **86 carefully curated Japanese AI productivity tips**, rotating styles over time. This is deterministic template-based generation; it does **not** browse current trends or call an LLM.
3. Build a 20-second 1080×1920 Reel with Japanese typography, H.264 video and original generated low-volume background audio (AAC).
4. Prepare the accompanying Japanese prompt/caption, package the MP4 as a GitHub Actions artifact, and deploy **only the generated, non-sensitive public MP4** to GitHub Pages.
5. Verify direct HTTPS delivery before contacting Instagram.
6. Check authentication, quota, existing identical captions and container processing, then publish the Reel using the official Instagram API.
7. Verify the published media when possible, write the publication result to the slot ledger and commit it back to the repository. Consecutive runs use concurrency to avoid overlapping publication.

The special workflow `first-live-reel.yml` is now **manual-only** to avoid duplicate publishing.

## Important limitations
- Instagram video publication currently needs a **publicly retrievable MP4 URL**. Only the final, approved output MP4 gets placed on GitHub Pages; Google Drive is a separate, private material store.
- This workflow does **not** automatically archive new videos in Google Drive. It archives for 30 days as GitHub Actions artifacts. Additional Drive credentials/integration are required for direct cloud archive.
- The 86 curated topic library eventually repeats; long-term trend-responsive AI writing would need a separately authorized AI API and appropriate QA safeguards.
- Instagram long-lived access tokens can expire; token renewal and secret rotation are **not automated**, so ongoing successful posting requires maintenance.
- Github Actions, Pages and Instagram have quotas and changing policies. "Enabled" does not mean guaranteed zero-downtime posting or exact-minute scheduling.
- Never paste tokens or credentials into source files or chat. Keep `INSTAGRAM_ACCESS_TOKEN` as a repository Actions secret.

## Validation
`.github/workflows/validate-daily.yml` runs dry-run checks and **never publishes**.

## Troubleshooting
Inspect the latest run at [GitHub Actions](https://github.com/o9o84441100-droid/panipani-instagram-auto/actions). A failure before the publishing step means Instagram received no publish request; failure after the publishing step requires checking the Instagram account and the slot ledger **before rerunning**.

## Evidence-led Instagram growth and operating delegation (2026-10-13)
- Owner-delegated strategy, quality and safety expectations: [OPERATING_POLICY.md](OPERATING_POLICY.md).
- Daily read-only Meta insights collection: [performance-review.yml](.github/workflows/performance-review.yml) at 23:05 JST.
- Weekly optimization using approximately 48-hour Instagram outcomes: [weekly-optimizer.yml](.github/workflows/weekly-optimizer.yml) at Monday 02:15 JST. Does not change topic weights without ≥30 comparable observations across ≥3 categories.
- Missed post detection: [post-audit.yml](.github/workflows/post-audit.yml) at 06:30 JST next morning; creates a GitHub issue only when an expected published slot has no ledger record.
- Initial media Insights read succeeded on 2026-10-13, collecting real views, reach, saves and shares for recent media. Account had 0 followers in that single snapshot; this is not a rate of growth.
- Read [GitHub Actions runs](https://github.com/o9o84441100-droid/panipani-instagram-auto/actions) to diagnose any scheduled failure. Google Drive archive and token auto-renewal are not yet integrated.

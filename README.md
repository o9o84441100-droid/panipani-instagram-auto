# Panipani Instagram automation

Initial safe GitHub Actions foundation. **No automatic publishing is enabled.**

- Scheduled check: 09:15 JST (00:15 UTC), with possible GitHub schedule delays.
- The scheduled workflow only checks the Instagram account and content publishing quota; it never publishes.
- Missing INSTAGRAM_ACCESS_TOKEN causes a message and exit without API validation; it does not mean authenticated verification succeeded.

## Owner-only setup
GitHub Settings > Secrets and variables > Actions > New repository secret.
Name: `INSTAGRAM_ACCESS_TOKEN`; value: valid Instagram Login token, without `Bearer `.
Never commit tokens or paste them into chat.

## Before automatic posting
Implement a reliable public HTTPS video source, content generation, persistent duplicate prevention, token renewal, retry handling, and verified publishing. Publication code requires explicit PUBLISH_MODE=publish and CONFIRM_PUBLICATION=YES; the scheduled workflow never sets them.

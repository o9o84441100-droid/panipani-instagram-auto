> **Canva-only publishing policy update (2026-10-13):** The former 5/day automatic posting workflow is currently PAUSED to honor the owner's requirement that every new Reel originate from a real Canva design. Neither a GitHub Actions schedule nor a manual trigger may publish the Canva-inspired-only Pillow renderer. A genuine Canva Connect autofill + MP4 export bridge and fail-closed publishing provenance check have been prepared, but **separate Canva Connect OAuth authorization and autofill templates are not configured yet**. See [CANVA_ONLY_SETUP.md](CANVA_ONLY_SETUP.md).\n\n# Panipani Instagram — Autonomous Operation Policy

Effective: 2026-10-13 (JST)
Instagram account: @reiv2220
GitHub repository: https://github.com/o9o84441100-droid/panipani-instagram-auto

## Delegation
The account owner has authorized the project to:
- Publish original, accurate Japanese educational AI productivity Reels on the five configured daily slots.
- Choose topics, visual hooks, cover wording, caption prompts and posting experiments without seeking per-post approval.
- Monitor actual Instagram outcomes and refine the strategy and content mix automatically.
- Add operational safeguards, monitoring, validation, and failure alerts.

The owner will intervene when results such as follower growth or reach are not satisfactory. This is a standing policy for **the configured automation**, not authorization to make unrelated account changes, spend money, impersonate others, use copyrighted audio, or follow/message strangers.

## Desired outcomes and review
Primary measures: verified net follower growth, meaningful reach and qualified engaged viewers.
Secondary measures: Reel views (with age window noted), saves, shares, comments, and profile visits where the API provides them.
Keep zero, unavailable, and unpublished distinct. Record post age before comparing outcomes. Do not claim causation from a few posts.
Start with a 14-day observation window at five posts per day, then reassess empirically. Do not equate output volume with audience growth.
No bought followers, engagement exchanges, fake reviews, fabricated claims or unsolicited automated engagement.

## Active background automation
- Five scheduled daily Reel publications: .github/workflows/panipani-daily-reels.yml
- Official read-only metrics and snapshot: .github/workflows/performance-review.yml (nightly)
- Weekly data-driven category weighting: .github/workflows/weekly-optimizer.yml
- Next-morning audit of missing publication records: .github/workflows/post-audit.yml
- Separate safe no-publish validation workflow: .github/workflows/validate-daily.yml

These are GitHub Actions jobs; they do not require the user's phone or PC to remain open. Runs can be delayed, fail, or be skipped; never assume publication without Meta media ID/permalink confirmation.
The assistant does NOT independently monitor the account outside scheduled workflows or active tool sessions.

## Guardrails
- Secrets are stored in GitHub Actions repository Secrets and must never appear in source, logs, Issues, captions or public Pages files.
- A Reel is published only after its MP4 is verifiably retrievable via public HTTPS.
- Never blindly retry a failed job if the Instagram publish step may already have succeeded.
- Issue an operational alert for missing ledger slots; use posted media IDs to reconcile before any rerun.
- Use original, self-generated visuals and sound. Do not automatically publish private Drive photos or personal user data.
- Escalate owner-only permission/authorization and token renewal steps rather than requesting credentials in chat.
- Analytics not exposed by the API must be shown as unavailable rather than guessed.
- Algorithmic weighting is disabled until at least 30 comparable approximately 48h media samples over at least three topic categories exist; weights are capped and other topics remain in rotation.

## Current limitations
- Posts use an original template-driven 86-topic bank, not dynamic LLM generation from current trends.
- Google Drive material folder is currently separate from the GitHub-generated Reel archive.
- GitHub Actions artifacts have finite retention, and GitHub Pages delivery depends on provider availability.
- A Google Calendar reminder exists for checking/renewing the Instagram token; automatic token secret rotation is not implemented.
- An autonomous analytics loop is installed, but actual performance improvement can only be assessed over time.

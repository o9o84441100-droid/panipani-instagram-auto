> **運用方針更新（2026-10-13 JST）:** Instagramの投稿・状態確認・分析の実行基盤はこのGitHubリポジトリとGitHub Actionsに統一する。Metricoolは今後使用せず、フォールバックや再接続先にも指定しない。投稿先はInstagram公式API。既存の承認済みCanva Connect素材制作と出自検証は維持する。
>
> **確認済みの状態:** 日次5枠のworkflowは有効、公開スイッチもtrue。公式Canva素材の公開記録がある。定期実行による継続公開の成否は各Actions runとstate/postsのmedia_id・permalinkで確認する。設定だけで稼働成功と報告しない。以前の「PAUSED／OAuth未設定」という記載は古いため廃止する。

# Panipani Instagram — Autonomous Operation Policy

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

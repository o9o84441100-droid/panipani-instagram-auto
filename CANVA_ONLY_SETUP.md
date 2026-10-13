# Panipani official Canva-only operating status (2026-10-13 JST)

## Verified achievements
- Canva official OAuth with PKCE was completed locally by the owner. Tokens and secrets must NEVER appear in ChatGPT, repository source, Issues, or logs.
- Four GitHub Actions secrets were added by the owner: CANVA_CLIENT_ID, CANVA_CLIENT_SECRET, CANVA_REFRESH_TOKEN, CANVA_TOKEN_KEY. Secrets' contents are not readable via GitHub connector.
- GitHub Actions repository variable CANVA_TEMPLATE_IDS was explicitly verified as:
  `DAHX1n4SSpU,DAHX1rftBb4,DAHX1vFRj1g`.
- Original Canva designs have text autofill fields: HOOK, SITUATION, PROMPT, CAUTION, CTA (verified via Canva dataset after commit).
- **Verified real Canva export**: manual workflow run #2, [38343291608](https://github.com/o9o84441100-droid/panipani-instagram-auto/actions/runs/38343291608). Actual Canva autofill created a design, official MP4 export succeeded and the runner verified 1080×1920 H.264/AAC. Original artifact was a five-second video; one frame was visually audited.
- Canva rotating refresh token was persisted encrypted to `state/canva/refresh_token.enc` in commit `c4a01a4`; raw refresh tokens never go into Git history. Token encryption key is only in GitHub Secret.
- GitHub unit suite verifies no non-Canva renderer is used; no Instagram publication in the live-test workflow.
- `canva_copy.py` now defines **86 human-curated short prompts** and bounded text per field; complete AI instructions remain in captions. `test_canva_copy.py` must pass before deployment.
- The manual testing workflow supports **all three approved templates in a single run** and uses a shared Canva OAuth concurrency group to avoid token refresh collisions.

## Current blockers before automated Instagram posting
- First real Canva video showed title overlap from a fixed secondary title and an oversized CTA. Canva design revisions for all three templates are currently **STAGED IN DRAFT**, NOT YET COMMITTED (explicit owner preview and approval required).
- The before/after template had visible Japanese typo text, also repaired in unsaved draft.
- Updated render quality of each design is **not verified** until designs are committed and the new workflow exports all three.
- The production publish job is still deliberately **`if: ${{ false }}`**, and the production workflow has **no cron schedule**. Instagram automatic publishing is OFF. Never claim it is operational.
- No real Canva-generated video has yet been used in a confirmed Instagram publication (old published Instagram test used an original non-Canva visual).

## Release checklist — do not skip
1. Show Canva tool preview for **all four pages** (template 1, template 2 pages 1–2, template 3); get owner's explicit approval before committing three Canva editing transactions.
2. Commit drafts; verify all five autofill fields survive in each design.
3. Run the **manual non-posting** workflow [Canva live export TEST](https://github.com/o9o84441100-droid/panipani-instagram-auto/actions/workflows/canva-live-export-test.yml), select `all` (default), once. It rotates the Canva token safely once and exports 3 separate Canva-source MP4s as an Actions artifact.
4. Download the resulting artifact, inspect at least one video frame per template and the end frame for Japanese readability, cropping, typos, 1080×1920 and H.264/AAC; rework templates if necessary.
5. Confirm Instagram API integration with `PUBLISH_MODE=check` (zero public posts).
6. After owner consent, perform a single real **Canva-sourced Instagram** test and verify its permalink, duplication guard and durable post ledger.
7. Restore the five original JST posting slots (08:05, 10:05, 12:05, 18:05, 21:05) only after verified tests and explicit owner consent; add rollback/alert and fail-closed switch.

## Canva template links
- [AI活用Tips](https://www.canva.com/design/DAHX1n4SSpU/edit)
- [ビフォー・アフター](https://www.canva.com/design/DAHX1rftBb4/edit) (two pages)
- [AIチャット操作デモ](https://www.canva.com/design/DAHX1vFRj1g/edit)

## Security and operational rules
- Never expose any password, Client Secret, OAuth token, or Fernet key.
- Refresh tokens are single-use. Keep the `panipani-canva-oauth` concurrency group shared across any workflow that calls `get_access_token()`.
- Do not reauthorize arbitrarily or overwrite CANVA_TOKEN_KEY once ciphertext exists; changing the key without a migration makes existing encrypted tokens unusable.
- Canva 1080×1920 MP4 visual source required; no Python-generated Canva-inspired visual fallback.
- Fail closed on any source, media quality, authentication, or publication uncertainty. No silent retries that could duplicate an Instagram post.
- Old workflow schedule is deliberately disabled; enabling it is a separately reviewed deployment step.

# Panipani — Canva-only publishing setup (2026-10-13 JST)

**Owner requirement:** Every *future* Instagram Reel must be produced from an actual Canva design, not merely a Canva-inspired Pillow/FFmpeg approximation.

## Actual state

- The previous 5/day scheduler is **PAUSED**: `.github/workflows/panipani-daily-reels.yml` has no cron schedule and the `publish` job has a fail-closed conditional. Even manual triggering cannot silently publish the old renderer.
- `publisher.py` blocks any public post without a local Canva export provenance manifest. The source MP4 SHA-256 must match the file being served.
- `canva_connect_export.py` implements genuine Canva REST API autofill and MP4 export at vertical 1080p, with download and codec/size checks. **This is prepared code, not yet authenticated or live-tested against Canva.**
- `canva_oauth.py` implements single-use refresh token rotation into Fernet-encrypted `state/canva/refresh_token.enc`, committed to the repo before using the token. The key remains in GitHub Secrets. No real OAuth credentials have been supplied or tested.
- `test_canva_connect_pipeline.py` mocks the API and validates the official request shapes, single-use refresh handling and rejection of missing/altered non-Canva media. Passing tests does not prove actual Canva API authorization.
- The ChatGPT Canva connection can generate/edit images and designs, but the exposed tools do **not** include a scheduled MP4 export/download suitable for a GitHub Actions runner. Sharing the chat connector does not authorize a GitHub runner to access the REST API.

## Canva designs ready for conversion (but autofill labels missing)

Canva folder: https://www.canva.com/folder/FAHX1p_2gds

| ID | Title |
|---|---|
| `DAHX1n4SSpU` | AI活用Tips Instagram Story |
| `DAHX1rftBb4` | AI依頼のビフォー・アフター比較 |
| `DAHX1vFRj1g` | Panipani AIチャット操作デモ |

Current Canva dataset checks returned `{}` for all three: they lack required autofill fields.

Each reusable design needs five **text autofill field labels** assigned to large, safe-zone text elements:
- `HOOK`: headline / problem
- `SITUATION`: short theme
- `PROMPT`: actionable AI request
- `CAUTION`: factual check
- `CTA`: save/share cue

The ChatGPT Canva connector can label a design's text elements through an editing transaction, but **requires explicit owner approval of the preview before saving edits**. Do not claim they are labelled until the Canva dataset reflects all five.

## One-time owner authorization required

1. Open Canva's [Developer portal](https://www.canva.com/developers/) and register/configure a Canva Connect (outside-Canva REST API) integration with OAuth 2.0 Authorization Code + PKCE. This is separate from connecting `@Canva` inside ChatGPT.
2. Authorize that integration for the Canva account owning the templates. Minimum operational scopes: `design:content:read` (export), `design:content:write` (autofill), and the metadata scope if required by the chosen API workflow.
3. Obtain a valid Canva OAuth **refresh token** via the documented server-side code exchange. Do not paste credentials or tokens into chat, commit them to source, or place them in GitHub Issues.
4. In [GitHub Actions Secrets](https://github.com/o9o84441100-droid/panipani-instagram-auto/settings/secrets/actions), store:
   - `CANVA_CLIENT_ID`
   - `CANVA_CLIENT_SECRET`
   - `CANVA_REFRESH_TOKEN` (bootstrap, initially single use)
   - `CANVA_TOKEN_KEY` (a locally generated Fernet key: run `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`; add its output only to Secrets)
5. In [GitHub Actions variables](https://github.com/o9o84441100-droid/panipani-instagram-auto/settings/variables/actions), set `CANVA_TEMPLATE_IDS` to `DAHX1n4SSpU,DAHX1rftBb4,DAHX1vFRj1g` **after all selected templates have the required autofill fields**.
6. Perform one **non-publishing live Canva export test** first; validate actual Canva permission, video content, Japanese text, 1080×1920 H.264 + AAC and rotation persistence. No automated schedule should be restored until this succeeds.
7. Restore the five JST cron triggers and replace the fail-closed `publish if: false` only after an actual Canva-authenticated MP4 has been proven, and run one tightly controlled Instagram test before daily deployment.

## Important Canva official documentation

- [Canva Connect Authentication](https://www.canva.dev/docs/apps/rest-apis/authentication/)
- [Autofill Guide](https://www.canva.dev/docs/apps/rest-apis/autofill-guide/)
- [Create design export job (MP4)](https://www.canva.dev/docs/apps/rest-apis/reference/exports/create-design-export-job/)
- [Refresh access token](https://www.canva.dev/docs/apps/rest-apis/reference/authentication/generate-access-token/)

**Operating constraint:** If a Canva export fails, SKIP the post and report the failure. Never fallback to fake Canva content or publish unreviewed static variations. Keeping five posts per day is subordinate to the owner's Canva-only requirement until the bridge is proven.

# Panipani Instagram Reels Automation

## Verified
- Instagram API with Instagram Login: authenticated as @reiv2220.
- GitHub Actions generated a 20-second MP4 and saved it as an artifact.
- No independently verified public Instagram Reel has been published from this repository yet.

## Current workflows
- `.github/workflows/instagram-check.yml`: scheduled read-only connection check.
- `.github/workflows/generate-reel.yml`: manually generates an MP4 artifact; never posts.
- `.github/workflows/publish-reel.yml`: guarded manual publish of a public MP4 URL.
- `.github/workflows/first-live-reel.yml`: first authorized end-to-end live publishing attempt. Generates a Japanese original AI tip video; deploys its MP4 to GitHub Pages; checks the public URL; then publishes via Instagram Login API and reads back the media permalink. Fails closed if Pages deployment or public MP4 delivery fails.

## Current blocker: video file hosting
Instagram Login API requires a publicly retrievable video_url. Unlike Facebook Login for Business, Instagram Login does NOT support direct resumable uploads.

GitHub Pages is used **only as a first-post experiment**; it is not a durable commercial video CDN. On GitHub Free, Pages requires a PUBLIC repository. This repository is currently PRIVATE, so the Pages step may fail unless the account has a paid plan that supports Pages on private repositories.

Do **not** publish this private repository without considering what the source code/history exposes. GitHub Actions secrets are not stored in repository code.

Do not mark automatic daily public posting as complete until real Instagram media ID/permalink verification succeeds. This repo does not yet have production daily posting.

## Security
- `INSTAGRAM_ACCESS_TOKEN` remains a GitHub Actions secret. Never paste tokens or credentials into chat or source code.
- Never make a whole Google Drive material folder public. Only specific already-approved video files may be published publicly.
- A failed publication request may have succeeded server-side; check Instagram before retrying.

## First test execution
The first-Reel workflow checks at 08:05, 10:05, 12:05, 18:05 and 21:05 JST. It will attempt publication only while `state/first_reel.done` is absent, and writes that marker to the repository after a successful run. GitHub scheduled jobs are best effort and can be delayed. This is **one first-Reel smoke test**, not the finished multi-Reel daily system. The repo owner must change repo visibility to public and select **Settings > Pages > Build and deployment > Source: GitHub Actions** before Pages upload can succeed on GitHub Free. Do not expose secrets or raw user assets in the Pages output.

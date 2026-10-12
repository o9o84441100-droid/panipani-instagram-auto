# Canva creative assets and GitHub Reels pipeline

## Actual Canva projects created and verified (1080×1920)
1. [AI活用Tips / editorial infographic](https://www.canva.com/d/njLf_4_ivByEHgN) — Canva ID DAHX1n4SSpU, 1 page.
2. [Before/After AI prompt comparison](https://www.canva.com/d/xsz6It1hGAnDBrz) — Canva ID DAHX1rftBb4, 2 pages.
3. [Simulated AI chat demonstration](https://www.canva.com/d/43PAePKQhkOnrQ5) — Canva ID DAHX1vFRj1g, 1 page.
4. Canva's AI image generator also produced the original visual media asset ID MAHX1iuVIaI.

Canva folder:
https://www.canva.com/folder/FAHX1p_2gds

## What is now deployed in GitHub
- `visual_renderer.py` renders **six distinct sequences** using original Python/Pillow artwork. It can create styled hooks, side-by-side concept comparisons, simulated chat interfaces, 3-step lists, prompt cards, caution cards and visual calls to action.
- `daily_reel.py` uses these frames, then FFmpeg animates the video and adds original background audio to make a valid 20-second 1080×1920 Reel for Instagram publishing.
- Independent test workflow `.github/workflows/validate-creative.yml` checks six storyboard families, Japanese copy and exact output dimensions. It also runs a full dry-run to validate H.264, AAC and duration **without** publishing.
- Production workflow `.github/workflows/panipani-daily-reels.yml` remains on the existing daily schedule. Its publishing authorization, media URL validation and per-slot duplicate guard are unchanged.

## Important distinction: Canva vs automatic rendering
The Canva connector in this chat supports generating/editing Canva designs and images, but its listed tools **do not expose an authenticated design export/download or scheduled Canva video generation API**. Therefore, this repository does **not** fetch original Canva render files unattended. It uses **independent, original GitHub-generated visuals inspired by the Canva studies**. This is not a claim that Canva templates themselves are used as each published Reel.

If Canva later provides a supported export connector/API with owner authorization, exported transparent PNG layers, MP4 clips and assets can be brought into the repository's pipeline through a validated ingest step. Until this exists, never add expiring Canva thumbnail URLs or Canva OAuth secrets to a public repository.

No new external API subscriptions or OpenArt credits have been purchased or charged.

## Creative principles
- Hooks should directly show an everyday pain point in the first three seconds.
- Every short scene must contain only readable Japanese with adequate contrast.
- Never place key captions near right/bottom Reels action overlays.
- Different templates are experiments, not a promise of viral reach.
- Judge against age-matched audience data, not single-day impressions.

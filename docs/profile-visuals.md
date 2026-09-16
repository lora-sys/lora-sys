# Profile visuals

The profile README keeps the existing hero illustration and uses generated SVGs for the introduction, project links, and contribution snake.

## Edit the introduction

Update `INTRO` and the desktop and mobile line layouts in `scripts/build_profile.py`. Keep the plain text and image alt text in `README.md` identical. Run the generator before committing.

```sh
python3 scripts/build_profile.py --output dist
```

The generator creates eight introduction variants and eight project cards. The introduction types once, then leaves the full text visible. Static variants are selected for reduced motion. Assets have no external fonts, JavaScript, API calls, or audio.

## Contribution snake

`.github/workflows/snake.yml` uses Platane/snk to fetch lora-sys contribution data and render light and dark SVGs. It runs after relevant pushes, daily at 00:23 UTC, or through workflow_dispatch. The two upstream actions are pinned to commit SHAs.

The workflow publishes all 18 SVGs to the existing `output` branch with a normal fast-forward commit. It preserves existing files and never force-pushes. The README points to that branch. A failed generation stops before publication, leaving the previous assets intact.

The original hero and its source files remain unchanged on `main`. Repository names, visibility, pinned projects, profile settings, and the personal website are outside this change.

Upstream source: https://github.com/Platane/snk

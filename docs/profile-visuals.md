# Profile visuals

The profile uses the original `assets/readme/hero-v1.webp` unchanged. Do not remove or replace this banner when changing the layout.

## Visual direction

Keep the warm paper, brown and amber palette from the original banner. Use a visible typewriter introduction, illustrated project links, numbered sections, technology labels and the contribution snake. Do not replace the artwork with a plain table.

The typewriter cycles through three short statements over 24 seconds. It includes a moving cursor and deletion between statements. Reduced-motion users get a separate static file. All essential project information is also available as image alt text and a text index.

Project cards use existing artwork from Lora's public repositories. AgentArena uses an actual UI screenshot; the other cards are labeled as project illustrations. The generator records each source URL and SHA-256 in `output/v4/sources.json`.

## Build

```sh
python -m pip install Pillow==11.3.0
python scripts/build_profile_v4.py --output dist
```

The generator creates 60 self-contained SVGs in `dist/v4`. The workflow adds four contribution snake files and publishes with a normal fast-forward push to `output`. A failure before publishing leaves existing images intact. Original source assets and older outputs are preserved.

Desktop cards form a two-column gallery without a Markdown table. On narrow screens the links wrap into one column and select a mobile artwork variant. The original banner remains unchanged on every screen size.

## Verification

`Review profile appearance` follows successful non-scheduled builds. It uses Chromium to open the actual public GitHub profile, checks every README image, theme selection, six project links, horizontal overflow, desktop and mobile arrangement, and reduced-motion selection. Screenshots and a JSON report are uploaded as a seven-day Actions artifact. These screenshots are not a locally reconstructed GitHub page.

## Design references

The following pages informed layout techniques, not copied artwork or biographies. Original illustration assets remain Lora's existing assets.

- https://github.com/topics/beautiful-profile-readme
- https://github.com/Sharann-del/Sharann-del uses numbered sections and consistent light/dark artwork.
- https://github.com/DIMFLIX/DIMFLIX combines an illustrated introduction, typewriter text, navigation badges and clickable visual cards.
- https://github.com/HiradEmami/HiradEmami uses animated separators and visual navigation.
- https://github.com/Platane/snk generates the contribution snake.

The README gallery is not GitHub's native pinned-repository setting. This build does not change native pins, repository visibility or account settings.

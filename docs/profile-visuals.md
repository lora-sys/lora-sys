# Profile visuals

The current profile uses a native heading, one short typing line, and six text-based project panels. Project descriptions remain visible. The contribution animation is collapsed by default. The previous large hero and illustration cards are no longer displayed; their source files and old output URLs are retained.

## Editing

Edit the biography and project descriptions in `README.md`. Update `TEXT` in `scripts/build_profile.py` for the typing line, keeping the image alt text in sync.

```sh
python3 scripts/build_profile.py --output dist
```

The generator produces `typing-v3-light.svg` and `typing-v3-dark.svg`. They have transparent backgrounds and use system fonts. Text types once, remains visible, and has no audio or looping cursor. Reduced motion shows complete text immediately.

## Publishing

`.github/workflows/snake.yml` adds two contribution snakes and validates exactly four generated SVGs. It publishes to the existing `output` branch with a normal fast-forward commit, preserving old URLs. Upstream actions remain pinned to commit SHAs. No force-push is used.

Publish new asset names before updating README references. A failed build must not replace the current README with links to missing images.

## Verification limits

The 2026-09-16 revision was checked using a local reconstruction of the README with GitHub-like Markdown styling. Desktop and narrow layouts were tested for horizontal overflow and visible broken images. The external contribution snake was excluded from this offline browser test; the workflow validates its generated SVG separately.

The browser could not open the actual GitHub profile due to an environment restriction. Local screenshots are not GitHub screenshots and do not validate GitHub's HTML sanitization or image proxy. Do not describe this as a complete live-page visual check.

## Native profile pins

The selected order is Glassbox-Agent-Harness, zhihu-threads, AgentArena, skills, nano-vllm-interactive-guide, and free-vision-skill.

Changing this README does not change GitHub's native pins. The available connector has no pin write action, and no authenticated browser session was available. Native pin selection and ordering remain unapplied. Do not use repository metadata or README cards as evidence that native pins changed.

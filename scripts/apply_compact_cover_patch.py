"""One-time idempotent source patch for compact project cover images."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Could not find expected source block: {label}")
    return text.replace(old, new, 1)


prepare = ROOT / "scripts/prepare_approved_layout.py"
s = prepare.read_text(encoding="utf-8")
s = replace_once(
    s,
    ".work-minor-heading{display:flex;align-items:center;gap:15px;margin:30px 0 15px;font-size:12px;color:var(--muted)}.work-compact{min-width:0;border:1px solid var(--border);padding:19px 21px 16px;border-radius:10px}.work-compact-title{display:flex;align-items:center;gap:10px;margin:0 0 10px}.work-compact-title>svg{color:var(--accent)}.work-compact h3{font-size:17px;line-height:1.5;letter-spacing:-.015em;margin:0;font-weight:630}.work-compact .work-desc{font-size:13px;min-height:47px;color:var(--muted)}.work-compact-foot{font-size:11px;display:flex;gap:10px;justify-content:space-between;align-items:center;margin-top:17px}.work-compact-foot>span{color:var(--muted)}.work-compact-foot>a{color:var(--accent)}.work-footer{margin-top:27px;padding-top:20px;border-top:1px solid var(--border);font-size:12px;color:var(--muted)}.work-footer a{color:var(--accent)}",
    ".work-minor-heading{display:flex;align-items:center;gap:15px;margin:30px 0 15px;font-size:12px;color:var(--muted)}.work-compact{min-width:0;border:1px solid var(--border);border-radius:10px;overflow:hidden;background:var(--page)}.work-compact-art{display:block;background:#f7f4ee;border-bottom:1px solid var(--border);overflow:hidden}.work-compact-art img{display:block;width:100%;aspect-ratio:16/6.6;object-fit:cover;object-position:center}.work-compact-copy{padding:17px 19px 15px}.work-compact-title{display:flex;align-items:center;gap:10px;margin:0 0 10px}.work-compact-title>svg{color:var(--accent)}.work-compact h3{font-size:17px;line-height:1.5;letter-spacing:-.015em;margin:0;font-weight:630}.work-compact .work-desc{font-size:13px;min-height:47px;color:var(--muted)}.work-compact-foot{font-size:11px;display:flex;gap:10px;justify-content:space-between;align-items:center;margin-top:17px}.work-compact-foot>span{color:var(--muted)}.work-compact-foot>a{color:var(--accent)}.work-footer{margin-top:27px;padding-top:20px;border-top:1px solid var(--border);font-size:12px;color:var(--muted)}.work-footer a{color:var(--accent)}",
    "compact cover CSS",
)
s = replace_once(
    s,
    ".work-compact{padding:18px 19px 15px}.work-compact-foot{margin-top:12px}",
    ".work-compact-copy{padding:16px 17px 14px}.work-compact-art img{aspect-ratio:16/7.3}.work-compact-foot{margin-top:12px}",
    "mobile compact cover CSS",
)
s = replace_once(
    s,
    "compact=[('AgentArena','AgentArena','grid','让三支 Agent 团队处理同一任务，保留提案、证据与对战回放。','多 Agent 实验',BASE+'AgentArena','查看项目'),('Lora Skills','skills','box','按需安装的 Agent 工作流集合，涵盖工程、写作和内容发布。','可安装工具',BASE+'skills#安装','查看安装说明'),('nano-vLLM 交互教程','nano-vllm-interactive-guide','book','结合源码与浏览器实验，讲解推理调度、KV Cache 和采样。','交互式源码教程','https://lora-sys.github.io/nano-vllm-interactive-guide/guide/00-start','打开教程'),('Free Vision Skill','free-vision-skill','code','按任务提取图片中的相关信息，输出文本证据供 Agent 继续处理。','开发者工具',BASE+'free-vision-skill#使用','查看使用方式')]",
    "compact=[('AgentArena','AgentArena','arena','grid','让三支 Agent 团队处理同一任务，保留提案、证据与对战回放。','多 Agent 实验',BASE+'AgentArena','查看项目'),('Lora Skills','skills','skills','box','按需安装的 Agent 工作流集合，涵盖工程、写作和内容发布。','可安装工具',BASE+'skills#安装','查看安装说明'),('nano-vLLM 交互教程','nano-vllm-interactive-guide','vllm','book','结合源码与浏览器实验，讲解推理调度、KV Cache 和采样。','交互式源码教程','https://lora-sys.github.io/nano-vllm-interactive-guide/guide/00-start','打开教程'),('Free Vision Skill','free-vision-skill','vision','code','按任务提取图片中的相关信息，输出文本证据供 Agent 继续处理。','开发者工具',BASE+'free-vision-skill#使用','查看使用方式')]",
    "compact artwork definitions",
)
s = replace_once(
    s,
    "for title,repo,ic,desc,kind,url,label in compact:out.append(f'<article class=\"work-compact\"><div class=\"work-compact-title\">{icon(ic)}<h3>{anchor(BASE+repo,title)}</h3></div><p class=\"work-desc\">{desc}</p><div class=\"work-compact-foot\"><span>{kind}</span>{anchor(url,label)}</div></article>')",
    "for title,repo,art,ic,desc,kind,url,label in compact:out.append(f'<article class=\"work-compact\"><a class=\"work-compact-art\" href=\"{BASE+repo}\"><img src=\"assets/{art}.webp\" alt=\"{title} 项目封面\"></a><div class=\"work-compact-copy\"><div class=\"work-compact-title\">{icon(ic)}<h3>{anchor(BASE+repo,title)}</h3></div><p class=\"work-desc\">{desc}</p><div class=\"work-compact-foot\"><span>{kind}</span>{anchor(url,label)}</div></div></article>')",
    "compact card markup",
)
prepare.write_text(s, encoding="utf-8")

build = ROOT / "scripts/build_approved_profile.py"
s = build.read_text(encoding="utf-8")
s = replace_once(
    s,
    " arts={\n  'banner':ROOT/'assets/readme/hero-v1.webp',\n  'glassbox':'https://raw.githubusercontent.com/lora-sys/Glassbox-Agent-Harness/main/assets/readme/glassbox-hero.png',\n  'zhihu':'https://raw.githubusercontent.com/lora-sys/zhihu-threads/main/assets/readme/lora-v3-project-zhihu-threads-zh.webp',\n }",
    " arts={\n  'banner':ROOT/'assets/readme/hero-v1.webp',\n  'glassbox':'https://raw.githubusercontent.com/lora-sys/Glassbox-Agent-Harness/main/assets/readme/glassbox-hero.png',\n  'zhihu':'https://raw.githubusercontent.com/lora-sys/zhihu-threads/main/assets/readme/lora-v3-project-zhihu-threads-zh.webp',\n  'arena':'https://raw.githubusercontent.com/lora-sys/AgentArena/main/docs/qa/visual-baselines/v052-home-desktop-20260725.png',\n  'skills':'https://raw.githubusercontent.com/lora-sys/skills/main/assets/readme/hero.png',\n  'vllm':'https://raw.githubusercontent.com/lora-sys/nano-vllm-interactive-guide/main/assets/readme/hero-v1.webp',\n  'vision':'https://raw.githubusercontent.com/lora-sys/free-vision-skill/main/assets/readme/hero-v1.webp',\n }",
    "compact artwork sources",
)
build.write_text(s, encoding="utf-8")
print("Compact project covers are present in the editable source.")

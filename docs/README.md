# 仓库维护索引

这是 lora-sys 的 GitHub Profile 仓库。面向访客的内容在根目录 [README](../README.md)。

## 从这里开始

- [维护说明](maintenance.md)：设计约定、数据来源、构建、发布及故障排查入口。
- [2026-10-25 审查报告](audits/2026-10-25.md)：CI 根因、整改、线上验证和待改善项。

## 文件职责

| 位置 | 用途 |
| --- | --- |
| [README.md](../README.md) | Profile 文案与图片引用的唯一来源 |
| [requirements.txt](../requirements.txt) | 构建和页面检查共用的 Python 依赖 |
| [assets/readme/hero.webp](../assets/readme/hero.webp) | 线上 banner |
| [assets/readme/source/](../assets/readme/source/) | banner 的布局、参考图、抠图和生成提示 |
| [scripts/build_assets.py](../scripts/build_assets.py) | 获取统计、渲染两张卡、生成贡献蛇变体 |
| [scripts/render_stats_layout.py](../scripts/render_stats_layout.py) | 两张统计卡的 HTML/CSS 布局 |
| [scripts/normalize_svg.py](../scripts/normalize_svg.py) | 展开嵌套贡献蛇 SVG，保留动画 |
| [scripts/validate_assets.py](../scripts/validate_assets.py) | 检查资源集合、数据哈希、README 引用和动画 |
| [scripts/check_live_profile.py](../scripts/check_live_profile.py) | 真实 GitHub 主页的六种视图及链接检查 |
| [build-assets.yml](../.github/workflows/build-assets.yml) | PR 校验、main 发布和每日刷新 |
| [check-profile.yml](../.github/workflows/check-profile.yml) | 发布后的真实页面检查 |

## 常见修改

改介绍、项目或文章，编辑根目录 README。改统计卡外观，编辑 render_stats_layout.py。排查 CI，先看 Actions 的失败步骤，再查维护说明和对应脚本。

main 只存源码与设计素材；output 分支存发布资源与数据来源记录。dist/、qa/、qa-live/、previous/、.venv/ 和生成的 assets/profile/stats-layout.html 是本地工作文件，已被 Git 忽略。

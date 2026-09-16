# 主页维护

## 已确认的设计

保留原文件 `assets/readme/hero-v1.webp`。构建检查它的 SHA-256，避免在后续排版中误换原 banner。

首屏使用三句循环打字、简介与导航。项目采用 A 方案，Glassbox 与 Zhihu Threads 是两张主推图文卡，下面放 AgentArena、Lora Skills、nano-vLLM 交互教程和 Free Vision Skill 的紧凑入口。技术区使用八个已确认图标。后面依次是统计、连续贡献、贡献贪吃蛇、三篇文章、三条已合并 PR 和联系页尾。

浅色卡片为 `#F6F2EA`，强调色为 `#9A661B`，等级圆环为 `#D6A03B`。深色卡片为 `#25231F`，强调色为 `#E2B45D`，等级圆环为 `#E0A62F`。

## 数据来源

GitHub 总览固定使用 GitHub Readme Stats Fast。账号为 `lora-sys`，保留 `hide_rank=false`、`rank_icon=default` 和暖金色 `ring_color`。不要切回之前失效的总览接口，也不要用预设字母替代服务评分。

语言分布使用 `github-readme-stats-sigma-fawn-45.vercel.app/api/top-langs/`。连续贡献使用 `github-readme-streak-stats-eight.vercel.app/`。两项均沿用已有自托管服务。

工作流读取真实 SVG，检查是否返回错误图片，再生成卡片。每个来源的 URL、获取时间和 SHA-256 写入 `output/v5/sources.json`。原始响应保存在 `output/v5/data/`。刷新失败时保留上一次通过检查的响应；首次发布没有有效数据时停止，不生成假数字。

贪吃蛇由 Platane/snk 根据贡献记录生成。打字与贪吃蛇均有独立静态版本，供减少动态效果设置使用。

## 文件与构建

` scripts/prepare_approved_layout.py ` 保存可编辑的布局样式和已确认文案，生成 `assets/profile/approved-layout.html`。

` scripts/build_approved_profile.py ` 以 Chromium 渲染各组件。静态组件使用高分辨率图片封装为自包含 SVG，以保留 GitHub README 无法直接运行的样式。每张项目、文章和 PR 卡片都有独立的外层链接，另保留无图文字目录。打字和贡献蛇仍使用 SVG 动画。不会提交字体文件、Cookie、令牌或个人文件。

```sh
python3 -m pip install Pillow==11.3.0 beautifulsoup4==4.13.4 playwright==1.55.0
python3 -m playwright install --with-deps chromium
python3 scripts/build_approved_profile.py
```

完整构建在 `Build profile visuals` 中执行，它还负责安装中文字体、获取历史输出和生成贡献蛇。工作流在相关推送、每日 00:23 UTC 或手动触发时运行。

输出写入 `output/v5/`。使用普通快进提交，不强制推送，不删除原有资源。主分支的 README 是经过审查的发布入口，构建脚本不会自动替换它。新布局先生成 `output/v5/candidate-README.md`，检查后再发布为主分支 README。

## 真实页面检查

`Review profile appearance` 在成功的非定时构建后，使用 `scripts/review_approved_profile.py` 打开真实 GitHub 主页。检查浅色与深色、桌面与手机、减少动画设置、图片加载、主推卡片布局和横向溢出，并保存整页截图。

构建截图与实际 GitHub 截图区分存放。Actions 产物保留七天。真实页面检查也记录文章与教程链接的 HTTP 状态。接口返回成功和卡片包含正确数据是两个独立检查。

## 修改边界

不要擅自删除原 banner、把打字缩成小标签、隐藏字母等级，或把项目 A 改回六张同尺寸海报。个人网站、仓库可见性与账号设置不随本工作流修改。README 项目卡片不等于 GitHub 原生置顶。

参考布局来自 HiradEmami/HiradEmami、thenolle/thenolle、DenverCoder1/DenverCoder1 和 awesome-github-profile-readme。原项目插画、文案、数据和链接使用 Lora 自己的内容。

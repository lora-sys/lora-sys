# 主页维护

## 已确认的设计

使用已确认的 `assets/readme/hero.webp`。底部标签已修正字体大小、胶囊宽度和间距；修改仅发生在标签区域，插画和其余排版保持原像素。构建检查它的 SHA-256，避免在后续排版中误换原 banner。

首屏是原 banner，下面依次是身份一行、导航一行、三个纯文本小节（做过的 / 写过的 / 数据和贡献）和页尾。数据区保留 GitHub 总览、语言分布两张卡和贡献贪吃蛇。打字 banner、项目图文卡、技术图标、文章卡、PR 卡与无图文字目录都已移除，内容改由 Markdown 正文承担，正文必须保持可选中、可搜索。

浅色卡片为 `#F6F2EA`，强调色为 `#9A661B`，等级圆环为 `#D6A03B`。深色卡片为 `#25231F`，强调色为 `#E2B45D`，等级圆环为 `#E0A62F`。

## 数据来源

GitHub 总览固定使用 GitHub Readme Stats Fast。账号为 `lora-sys`，保留 `hide_rank=false`、`rank_icon=default` 和暖金色 `ring_color`。不要切回之前失效的总览接口，也不要用预设字母替代服务评分。

语言分布使用 `github-readme-stats-fast.vercel.app/api/top-langs/`（与总览同源；旧部署已返回 DEPLOYMENT_NOT_FOUND）。

工作流读取真实 SVG，检查是否返回错误图片，再生成卡片。每个来源的 URL、获取时间和 SHA-256 写入 `output/v5/sources.json`。原始响应保存在 `output/v5/data/`。刷新失败时保留上一次通过检查的响应；首次发布没有有效数据时停止，不生成假数字。

贪吃蛇由 Platane/snk 根据贡献记录生成，并有独立静态版本，供减少动态效果设置使用。

## 文件与构建

`scripts/render_stats_layout.py` 只保存总览和语言卡的布局样式，生成被 Git 忽略的 `assets/profile/stats-layout.html`。README.md 是主页文案和资源引用的唯一来源，生成器不维护第二份 README。

`scripts/build_assets.py` 以 Chromium 渲染两张统计卡和贡献贪吃蛇，输出为自包含 SVG。构建只处理 README 实际引用的资源：banner、overview、languages 和 snake；不包含旧项目卡、工具图标或第三方项目插画。不会提交字体文件、Cookie、令牌或个人文件。

```sh
python3 -m pip install -r requirements.txt
python3 -m playwright install --with-deps chromium
python3 scripts/build_assets.py
python3 scripts/normalize_svg.py dist/v5
python3 scripts/validate_assets.py
```

完整构建在 `Build profile visuals` 中执行，它还负责安装中文字体、获取历史输出和生成贡献蛇。两个工作流固定 Ubuntu 24.04 和 Python 3.12，避免 ubuntu-latest 切换系统使固定版本的 Playwright 失效；依赖统一来自 requirements.txt。构建在 main 推送、PR、每日 00:23 UTC 或手动触发时运行。PR 完整生成与校验但不发布。验证检查精确资源集合、README 引用、原始数据哈希，以及全部 12 个贪吃蛇动态/静态变体。

输出写入 `output/v5/`。使用普通快进提交，不强制推送。仅在所有验证通过后，将 dist/v5/ 通过 rsync --delete 同步到 previous/v5/，清除不再生成的旧卡片及数据；不会删除 v5 目录外的文件。主分支的 README 是经过审查的发布入口，构建脚本不会自动替换它。文案和布局修改通过 PR 检查后合并。

## 真实页面检查

`Review profile appearance` 在成功的 main 构建后（包括每日定时构建），使用 `scripts/check_live_profile.py` 打开真实 GitHub 主页。等待新布局的「数据和贡献」标题出现后再断言，检查浅色与深色、桌面与手机、减少动画设置、图片加载、两张统计卡在窄屏纵向堆叠、二级标题与正文关键字、无 `。。` 占位符和横向溢出，并保存整页截图。

构建截图与实际 GitHub 截图区分存放。Actions 产物保留七天。真实页面检查从 README 提取网站、文章、RSS 与教程链接，记录 HTTP 状态；请求失败将使检查失败。接口返回成功和卡片包含正确数据是两个独立检查。

## 修改边界

不要擅自删除原 banner、隐藏字母等级，或把数据卡换成直连 provider 的实时链接。个人网站、仓库可见性与账号设置不随本工作流修改。README 里的项目列表不等于 GitHub 原生置顶。

参考布局来自 HiradEmami/HiradEmami、thenolle/thenolle、DenverCoder1/DenverCoder1 和 awesome-github-profile-readme。原项目插画、文案、数据和链接使用 Lora 自己的内容。

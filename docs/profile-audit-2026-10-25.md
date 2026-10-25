# Profile 审查与整改（2026-10-25）

## 结论

主页的定位、项目、文章与贡献例子清楚，保留当前原版 banner、纯文本介绍、两张统计卡和贪吃蛇即可。主要问题在维护流程和过期数字，无需再做一轮装饰性重设计。

## 已整改

- CI 运行环境漂移：失败运行 [40163680836](https://github.com/lora-sys/lora-sys/actions/runs/40163680836) 使用 Ubuntu 26.04，Playwright 1.55 明确报不支持。两个工作流固定 Ubuntu 24.04、Python 3.12，依赖集中到 requirements.txt。
- 缺少合并前检查：PR 现在执行完整生成、SVG 校验、数据哈希校验、README 资源引用校验和动态/静态帧检查，跳过发布步骤。
- 输出资源累积：过去 cp 仅覆盖文件，六张旧 streak 卡持续留在 output/v5。发布改为仅同步 v5 目录并删除废弃文件，发布前必须验证完整资源集合。
- 历史实现残留：移除 v3/v4 生成器、旧页面审查器、一次性封面拼装工作流、base64 分片和未引用的根目录图片。当前仅保留一条生成链路，布局只含实际使用的统计卡。
- 文案重复维护：移除生成器中第二份 README 文案，README.md 成为唯一内容来源。
- 静态数字过期：去掉没有日期、不会自动更新的 119 Issue / 67 PR、174 PR / 13 仓库、179 篇笔记，保留项目说明、文章和贡献证据。
- 每日构建跳过真实页面检查：移除 schedule 排除条件，成功的 main 构建都会检查真实主页；链接检查覆盖 README 的网站、项目、文章、RSS 和教程，请求失败计入失败结果。

## 线上内容核验

- 原版 banner、总览、语言分布、贡献蛇均正常加载。桌面实测宽度约为 846 / 408 / 408 / 846 px。
- 当前原生置顶包括 nano-vllm-interactive-guide、AgentArena、Glassbox-Agent-Harness、skills、trustops，与 README 的主要项目一致。
- 三个贡献例子全部确认作者为 lora-sys 且状态 MERGED：[eino-examples #227](https://github.com/cloudwego/eino-examples/pull/227)、[nad-agent #49](https://github.com/portdeveloper/nad-agent/pull/49)、[moss #29](https://github.com/nishuzumi/moss/pull/29)。原版 README 的合并总数没有完整统计口径，已移除，避免用无法持续核验的总量作宣传。
- 文章链接应称为“代表文章”，原文“最近的几篇”会随着时间失效，已更正。

## 验证结果

GitHub PR 构建 [40184650255](https://github.com/lora-sys/lora-sys/actions/runs/40184650255) 已全部通过，发布步骤按预期跳过。

本地完整构建产出 24 个页面资源和 4 个原始统计 SVG，四个统计来源均为 fresh。真实主页六种视图检查通过，八个网站/文章/RSS/教程链接全部 HTTP 200。故障注入确认废弃 streak 资源、数据哈希不匹配、README 引用错误均会被拦截。动态/静态检查覆盖全部 12 个贪吃蛇变体。

## 可读性取舍

手机端没有横向溢出，两张统计卡能正确纵向堆叠。但 320/390px 屏幕上的卡内文字仍偏小：服务返回的大尺寸统计图被整体缩放。正文项目与文章可正常阅读；若后续继续优化，优先提升移动端统计文字大小，避免增加更多数据卡。

## 账号设置建议

以下是账号级设置，本次仓库整理没有修改：

1. 侧栏简介“Builder of evolving systems. Turning ambitious ideas into reality. Always building, learning, and shipping.”过于泛化。建议改为“Student developer building AI agents, developer tools, and interactive source-code guides.”，与 README 对齐。
2. 侧栏显示的时差为“20h behind”，与 README 的“中国西安”不一致。检查 GitHub Settings → Public profile 的本地时间设置，按真实所在地设为 Asia/Shanghai。
3. 原生置顶保留最能代表当前工作的 4–6 个仓库；本次所见的五个选择合理，后续以项目可用性和说明完整度维护。

## 后续维护约定

只改 README 文案；改卡片外观时改 prepare_approved_layout.py；新增或删除卡片时同时更新 CARDS 与 README 资源引用，精确集合校验会阻止遗漏。Ubuntu/Python/Playwright 的升级放在同一个 PR 中验证，不依赖 latest 隐式升级。不要用 continue-on-error 隐藏构建失败。

上游统计服务、GitHub API、Actions 和公网仍可能短暂不可用，无法承诺永不失败。现有统计快照保留机制会记录真实获取时间和错误，验证器会发出 warning；没有有效数据时停止发布。

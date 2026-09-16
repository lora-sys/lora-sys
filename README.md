<p>
  <a href="https://lora-sys.github.io/loraSys/">
    <img src="./assets/readme/hero-v1.webp" width="100%" alt="Lora，个人 Agent、开发工具与交互教程">
  </a>
</p>

<picture>
  <source media="(prefers-reduced-motion: reduce) and (max-width: 540px) and (prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/intro-dark-mobile-static.svg">
  <source media="(prefers-reduced-motion: reduce) and (max-width: 540px)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/intro-light-mobile-static.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/intro-dark-static.svg">
  <source media="(prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/intro-light-static.svg">
  <source media="(max-width: 540px) and (prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/intro-dark-mobile.svg">
  <source media="(max-width: 540px)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/intro-light-mobile.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/intro-dark.svg">
  <img src="https://raw.githubusercontent.com/lora-sys/lora-sys/output/intro-light.svg" width="100%" alt="我是 Lora。我在做能长期使用的个人 Agent，也写工具、做产品。这里记录我的开源项目，以及读源码时做的交互教程。">
</picture>

[个人网站](https://lora-sys.github.io/loraSys/) · [全部项目](https://lora-sys.github.io/loraSys/projects) · [文章](https://lora-sys.github.io/loraSys/blog) · [邮件](mailto:lorasys@outlook.com)

<details>
<summary>文字介绍</summary>

我是 Lora。我在做能长期使用的个人 Agent，也写工具、做产品。这里记录我的开源项目，以及读源码时做的交互教程。

</details>

## 我在做的项目

<p>
<a href="https://github.com/lora-sys/Glassbox-Agent-Harness">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/card-glassbox-dark.svg">
    <img src="https://raw.githubusercontent.com/lora-sys/lora-sys/output/card-glassbox-light.svg" width="390" alt="Glassbox，开发中的个人 Agent 系统">
  </picture>
</a>
<a href="https://github.com/lora-sys/zhihu-threads">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/card-zhihu-dark.svg">
    <img src="https://raw.githubusercontent.com/lora-sys/lora-sys/output/card-zhihu-light.svg" width="390" alt="Zhihu Threads，带来源的学习线">
  </picture>
</a>
</p>

<p>
<a href="https://github.com/lora-sys/AgentArena">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/card-arena-dark.svg">
    <img src="https://raw.githubusercontent.com/lora-sys/lora-sys/output/card-arena-light.svg" width="390" alt="AgentArena，团队竞技与证据回放">
  </picture>
</a>
<a href="https://github.com/lora-sys/skills">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/card-skills-dark.svg">
    <img src="https://raw.githubusercontent.com/lora-sys/lora-sys/output/card-skills-light.svg" width="390" alt="Lora Skills，可安装的技能集合">
  </picture>
</a>
</p>

<details>
<summary>项目说明与开发状态</summary>

### [Glassbox](https://github.com/lora-sys/Glassbox-Agent-Harness)

我正在做的个人 Agent 系统。当前在接入 QQ，完善身份、权限和对话存储，并把需要执行的任务交给 Pi、Codex 或 Claude Code。

Pi 提供 Agent 引擎，Lora PI Kit 管理我的 Pi 工作环境，Glassbox 管理用户、对话、任务和执行记录。

[查看当前开发计划](https://github.com/lora-sys/Glassbox-Agent-Harness/blob/main/.plans/03-personal-agent-foundation.md)

### [Zhihu Threads](https://github.com/lora-sys/zhihu-threads)

用户先选择知乎回答和文章摘录，AI 再组织带来源的学习线。支持继续追问、自测和导出，回答范围限于所选摘录。

### [AgentArena](https://github.com/lora-sys/AgentArena)

让三支 Agent 团队处理同一份任务，比较提案、修订和证据。项目区分真实模型运行与固定演示回放，保留可查看的事件记录。

### [Lora Skills](https://github.com/lora-sys/skills)

我维护的 Agent Skills 集合，包含静态站发布、工程协作、写作和媒体工作流。技能可以单独安装，来源与许可证在对应目录中说明。

</details>

## 教程与工具

| 项目 | 内容 |
| --- | --- |
| [nano-vLLM 交互教程](https://lora-sys.github.io/nano-vllm-interactive-guide/guide/00-start) | 基于 nano-vLLM 源码，结合中文章节和浏览器实验讲解调度、KV Cache 与采样。 |
| [Free Vision Skill](https://github.com/lora-sys/free-vision-skill) | 将图片中的相关信息提取为文本证据，供 Agent 后续处理。 |
| [AI Engineering Harness](https://github.com/lora-sys/ai-engineering-harness) | 组织 Issue、实现、测试、审查与验收证据的 Agent 工程工作流。 |

## 开源贡献

在 [moss](https://github.com/nishuzumi/moss) 中，我提交的 [合约 ABI 获取工具](https://github.com/nishuzumi/moss/pull/29) 和 [PancakeSwap V3 单跳交易适配器](https://github.com/nishuzumi/moss/pull/24) 已合并。

更多项目、实验和开发记录见[个人网站](https://lora-sys.github.io/loraSys/projects)。

## 最近的代码记录

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lora-sys/lora-sys/output/snake-dark.svg">
  <img src="https://raw.githubusercontent.com/lora-sys/lora-sys/output/snake-light.svg" width="100%" alt="由 lora-sys 真实 GitHub 贡献记录生成的贪吃蛇动画">
</picture>

<sub>根据 GitHub 贡献记录每日更新。动画由 <a href="https://github.com/Platane/snk">Platane/snk</a> 生成。</sub>

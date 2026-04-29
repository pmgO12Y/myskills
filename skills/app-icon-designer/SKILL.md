---
name: app-icon-designer
description: >
  Creative app icon design skill for software products. Use this skill when the user wants to design a main/primary icon (app icon)
  for a software, app, tool, or product. Specializes in creatively brainstorming multiple differentiated icon concepts based on
  software function, name, or brand tone — including visual metaphors, color schemes, and design style recommendations —
  then generating high-quality icon images. Trigger phrases include: "design an app icon", "create a software icon",
  "icon design", "app icon creative concept", "help me design an icon for my app", "give me icon ideas",
  "App icon", "software icon", "icon concept", "icon creativity".
---

# App Icon Designer — 软件主图标创意设计

## 概述

本 Skill 以「创意策划优先」的方式为软件设计主图标。核心价值在于：深度理解软件背后的概念，
发掘有记忆点的视觉隐喻，策划多个差异化创意方向，最终输出高质量图标图片。

不只是生成一张图——而是像一名资深设计师一样**思考图标在讲什么故事**。

---

## 工作流程

### 第一步：信息收集

收集以下信息（未提供的通过对话获取，已提供的直接进入下一步）：

**必须了解：**
- 软件的核心功能是什么？（一句话描述）
- 目标平台是什么？（iOS App / Android / macOS / Chrome 扩展 / Windows / Web 等）

**有助于提升创意质量（选填，若用户没提就不强制问）：**
- 软件名称是什么？
- 目标用户群体？（学生 / 专业人士 / 企业 / 普通消费者）
- 有无风格偏好？（极简 / 科技感 / 活泼 / 专业 / 自然等）
- 有无不想要的颜色或元素？

> **重要原则**：不要问超过 2 轮问题。若信息足够开始创意策划，立即进入第二步。
> 缺少的信息可以合理假设，在方案中注明。

---

### 第二步：概念挖掘（内部思考，不直接输出给用户）

在生成创意方向前，先在内部完成以下分析：

1. **拆解核心概念**：软件的核心动词是什么？核心名词？用户的核心感受？
2. **联想视觉隐喻**：有哪些物体、形状、符号能代表这些概念？
3. **竞品图标分析**：这类软件常见图标是什么？如何避开雷同？
4. **确定差异化维度**：从隐喻、风格、色彩哪个维度能创造最大差异？

参考：`references/icon-creative-framework.md` 中的「概念挖掘层」和「视觉隐喻类型」。

---

### 第三步：创意方向策划（核心输出）

策划 **3-4 个创意方向**，每个方向使用以下格式：

```
### 方向 N：[有记忆点的方向名称]

**核心隐喻：** [一句话说清楚图标在讲什么故事]

**视觉元素：**
- 主体图形：[具体描述]
- 背景/底色：[颜色 + 渐变方向，给出参考色值]
- 辅助元素：[点缀细节，可选]
- 构图：[居中 / 偏移 / 包围等]

**色彩方案：** [主色 + 辅色，说明为何选这个配色]

**设计风格：** [具体风格名称 + 简短理由]

**差异化亮点：** [与同类 App 图标的不同之处]
```

各方向之间应有**明显差异**（不同隐喻、不同风格、不同色调），让用户真正有选择空间。

参考：`references/icon-creative-framework.md` 中的颜色心理学、图标风格指南。

---

### 第四步：用户选择与确认

列出所有方向后，询问用户：

- 哪个方向最接近他们的想法？
- 是否需要调整某些细节（颜色、风格、元素）？
- 还是希望融合多个方向的元素？
- **是否需要为选定的方向生成多种风格变体？**（如极简/3D/孟菲斯/波普等）

---

### 第五步：风格变体生成（可选）

若用户要求为选定方向生成多种风格变体：

1. 从 `references/icon-creative-framework.md` 的「扩展设计风格（16种）」中选择 **3-5 种**适合该方向的推荐风格
2. 使用 `references/prompt-engineering.md` 中对应风格的 Prompt 模板，保持核心隐喻不变，只换风格语言
3. 每次生成一个风格变体，标注风格名称和适用场景
4. 让用户对比选择最满意的风格

**推荐组合策略：**
- 保守方案：极简 + 扁平2.0 + 3D + 毛玻璃 + 瑞士风格
- 活泼方案：孟菲斯 + 波普 + Y2K + 剪纸层叠 + 渐变填充
- 前卫方案：酸性 + 赛博朋克 + 蒸汽波 + 霓虹科技

---

### 第六步：生成图标图片

用户确认方向后：

1. **构建高质量 prompt**，参考 `references/prompt-engineering.md` 中的模板和关键词库
2. **调用 image_gen 工具**生成图标（首选 1024x1024）
3. 如有需要，根据用户反馈迭代（最多迭代 3 次）

Prompt 构建要点：
- 首先确定风格词（flat / 3D / gradient 等）
- 精确描述主体图形（形状 + 颜色 + 位置）
- 指定背景（颜色 / 渐变 / 透明）
- 加入质量词（app store quality, 1024x1024, professional）
- 避免文字请求（生图对文字渲染效果差）

---

### 第六步：可选输出

图片生成后，按需提供：

- **使用建议**：适合哪些平台，建议的背景色
- **尺寸适配参考**：指引用户参考平台规范自行导出多尺寸
- **SVG 版本**：若用户需要矢量版，根据图片描述用代码重绘一个近似的 SVG 版本

---

## 输出质量准则

- 创意方向之间**必须有明显差异**，避免只换颜色
- 每个方向的**核心隐喻要有说服力**，能用一句话讲清图标在传达什么
- Prompt 要足够具体，**每次生图前都重新根据方向构建**，不复用模糊 prompt
- 生成图片后，**主动询问是否满意**，说明可以调整的方向
- 若用户描述很模糊，**大胆假设并提出方案**，而不是反复追问

---

## 参考资源

- `references/icon-creative-framework.md` — 创意策划方法论、颜色心理学、**16种扩展设计风格指南**、评估标准
- `references/prompt-engineering.md` — **17种风格 Prompt 模板**（含极简/3D/孟菲斯/波普/酸性/Y2K/赛博朋克/蒸汽波/包豪斯/瑞士/艺术装饰/剪纸/涂鸦等）、关键词词库、迭代优化策略

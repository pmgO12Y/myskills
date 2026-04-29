# 图标生成 Prompt 工程指南

本文档帮助将创意方向转化为 image_gen 工具可用的高质量 prompt，最大化生成图标的质量和准确度。

---

## 一、Prompt 结构公式

### 基础公式

```
[图标类型] + [主体描述] + [风格关键词] + [色彩方案] + [构图/背景] + [质量词]
```

### 完整示例

```
App icon, [具体图形描述], flat design style, [颜色] color palette, 
centered composition on [背景描述], clean minimalist, 
professional software icon, 1024x1024, high quality
```

---

## 二、各风格 Prompt 模板

### 2.1 扁平化渐变风格（最通用）

```
App icon for [软件名/类型], [主体图形], modern flat design, 
gradient background from [颜色A] to [颜色B], white [图形] symbol,
rounded corners, smooth gradient, vibrant colors, 
clean professional look, 1024x1024 resolution
```

**示例：**
```
App icon for productivity app, checkmark inside circle, modern flat design,
gradient background from deep blue #2563EB to purple #7C3AED, white checkmark symbol,
rounded square shape, smooth gradient, vibrant colors,
clean professional look, 1024x1024 resolution
```

---

### 2.2 3D 立体风格（macOS 风格）

```
macOS app icon, 3D [物体], soft lighting from upper left, 
[材质] material texture, [颜色] color scheme,
subtle shadow, depth and volume, Apple design aesthetic,
clean background, photorealistic 3D rendering, high detail
```

**示例：**
```
macOS app icon, 3D magnifying glass, soft lighting from upper left,
glass and metal material texture, blue and silver color scheme,
subtle shadow, depth and volume, Apple design aesthetic,
clean white background, photorealistic 3D rendering, high detail
```

---

### 2.3 极简线性风格

```
Minimal app icon, thin line [图形] on [底色] background,
[强调色] accent, geometric and clean, 
Swiss design style, negative space, balanced composition,
icon for [软件类型], professional, timeless design
```

---

### 2.4 拟物风格

```
Skeuomorphic app icon, realistic [物体],
[材质] texture, specular highlights, 
ambient occlusion, detailed craftsmanship,
warm [颜色] tones, ultra detailed, 
professional app store icon quality
```

---

### 2.5 暗色/霓虹科技风格（AI/开发工具）

```
Dark theme app icon, [图形] on dark background,
neon [颜色] glow effect, futuristic tech aesthetic,
gradient [颜色A] to [颜色B] accent,
subtle grid or circuit pattern, 
sleek modern design, premium quality
```

---

### 2.6 毛玻璃风格（iOS/macOS 现代风）

```
App icon with frosted glass effect, [图形] symbol,
glassmorphism style, translucent background,
[颜色] tint, soft blur, layered depth,
white or light [图形] on glass surface,
Apple Human Interface Guidelines style
```

---

### 2.7 孟菲斯风格（Memphis）

```
Memphis design app icon, [主体图形], bold geometric shapes,
high contrast colors [颜色A] and [颜色B], black thick outlines,
scattered dots and zigzag patterns, playful and vibrant,
80s retro aesthetic, flat illustration style,
app icon, 1024x1024, high quality
```

**示例：**
```
Memphis design app icon, chat bubble with lightning bolt,
bold geometric shapes, high contrast colors hot pink #EC4899 and electric blue #3B82F6,
black thick outlines 4px, scattered dots and zigzag patterns,
playful and vibrant, 80s retro aesthetic, flat illustration style,
app icon, 1024x1024, high quality
```

---

### 2.8 波普艺术风格（Pop Art）

```
Pop Art app icon, [主体图形], Ben-Day dots pattern background,
bold black comic-style outlines, saturated primary colors,
[颜色A] and [颜色B] color scheme, Roy Lichtenstein style,
retro comic book aesthetic, halftone dots texture,
app icon, 1024x1024, high quality
```

**示例：**
```
Pop Art app icon, speech bubble with star burst,
Ben-Day dots pattern background in yellow #FDE047,
bold black comic-style outlines 5px, saturated primary colors red #EF4444 and blue #3B82F6,
Roy Lichtenstein style, retro comic book aesthetic, halftone dots texture,
app icon, 1024x1024, high quality
```

---

### 2.9 酸性设计/液态金属风格（Acid/Chrome）

```
Acid design app icon, chrome metallic [主体图形],
liquid metal texture with rainbow reflections,
iridescent holographic surface, distorted wavy edges,
dark background with neon [颜色] glow,
Y2K futuristic aesthetic, reflective chrome finish,
app icon, 1024x1024, high quality
```

**示例：**
```
Acid design app icon, chrome metallic speech bubble,
liquid metal texture with rainbow reflections,
iridescent holographic surface, distorted wavy edges,
dark background with neon cyan glow,
Y2K futuristic aesthetic, reflective chrome finish,
app icon, 1024x1024, high quality
```

---

### 2.10 Y2K/千禧风格

```
Y2K aesthetic app icon, [主体图形], chrome and transparent plastic,
gradient from silver to iridescent [颜色], bubble texture,
retro-futuristic 2000s style, glossy 3D render,
soft pastel background with sparkles,
app icon, 1024x1024, high quality
```

**示例：**
```
Y2K aesthetic app icon, rounded chat bubble, chrome and transparent plastic,
gradient from silver to iridescent pink #EC4899, bubble texture,
retro-futuristic 2000s style, glossy 3D render,
soft pastel lavender background with sparkles,
app icon, 1024x1024, high quality
```

---

### 2.11 赛博朋克风格（Cyberpunk）

```
Cyberpunk app icon, [主体图形], dark background #0A0A0A,
neon [颜色] glow effect, glitch art elements,
digital distortion lines, futuristic tech aesthetic,
high contrast, dystopian vibe,
app icon, 1024x1024, high quality
```

**示例：**
```
Cyberpunk app icon, holographic message icon, dark background #0A0A0A,
neon magenta #FF00FF glow effect, glitch art elements with RGB split,
digital distortion lines, futuristic tech aesthetic,
high contrast, dystopian vibe,
app icon, 1024x1024, high quality
```

---

### 2.12 蒸汽波风格（Vaporwave）

```
Vaporwave app icon, [主体图形], pink and cyan gradient,
retro 80s aesthetic, palm tree or grid pattern background,
classical sculpture elements, sunset colors,
lo-fi nostalgic vibe, glitch effect,
app icon, 1024x1024, high quality
```

**示例：**
```
Vaporwave app icon, floating chat bubble, pink #FF71CE and cyan #01CDFE gradient,
retro 80s aesthetic, grid pattern background,
lo-fi nostalgic vibe, subtle glitch effect,
app icon, 1024x1024, high quality
```

---

### 2.13 包豪斯风格（Bauhaus）

```
Bauhaus app icon, [主体图形], primary colors red yellow blue,
geometric abstraction, circle triangle square composition,
functionalist design, clean lines, asymmetric balance,
modernist aesthetic, flat design,
app icon, 1024x1024, high quality
```

**示例：**
```
Bauhaus app icon, abstract communication symbol, primary colors red #EF4444 yellow #FDE047 blue #3B82F6,
geometric abstraction with circle and triangle, functionalist design,
clean lines, asymmetric balance, modernist aesthetic, flat design,
app icon, 1024x1024, high quality
```

---

### 2.14 瑞士/国际主义风格（Swiss）

```
Swiss design app icon, [主体图形], grid-based layout,
Helvetica-inspired typography (no text in icon), objective and rational,
black white and [强调色] only, asymmetric composition,
International Typographic Style, clean and functional,
app icon, 1024x1024, high quality
```

**示例：**
```
Swiss design app icon, minimal chat symbol, grid-based layout,
objective and rational, black white and red #EF4444 only,
asymmetric composition, International Typographic Style,
clean and functional, app icon, 1024x1024, high quality
```

---

### 2.15 艺术装饰风格（Art Deco）

```
Art Deco app icon, [主体图形], geometric symmetry,
gold and black color scheme, sunburst patterns,
1920s Gatsby aesthetic, elegant lines, luxurious feel,
metallic gold accents, stepped forms,
app icon, 1024x1024, high quality
```

**示例：**
```
Art Deco app icon, elegant message envelope, geometric symmetry,
gold #D4AF37 and black #1A1A1A color scheme, sunburst patterns,
1920s Gatsby aesthetic, elegant lines, luxurious feel,
metallic gold accents, stepped forms,
app icon, 1024x1024, high quality
```

---

### 2.16 剪纸/层叠风格（Paper Cut）

```
Paper cut app icon, [主体图形], layered paper cutout effect,
3D depth through shadow layers, [颜色A] and [颜色B] gradient,
clean edges, origami-inspired folds, tactile texture,
modern illustration style, subtle drop shadows,
app icon, 1024x1024, high quality
```

**示例：**
```
Paper cut app icon, speech bubble, layered paper cutout effect,
3D depth through shadow layers, teal #14B8A6 and coral #F97316 gradient,
clean edges, origami-inspired folds, tactile texture,
modern illustration style, subtle drop shadows,
app icon, 1024x1024, high quality
```

---

### 2.17 涂鸦/街头风格（Graffiti）

```
Graffiti style app icon, [主体图形], spray paint texture,
bold brush strokes, vibrant street art colors,
urban aesthetic, dripping paint effect,
hand-drawn feel, energetic and youthful,
app icon, 1024x1024, high quality
```

**示例：**
```
Graffiti style app icon, spray painted chat bubble, spray paint texture,
bold brush strokes, vibrant street art colors orange #F97316 and purple #8B5CF6,
urban aesthetic, subtle dripping paint effect,
hand-drawn feel, energetic and youthful,
app icon, 1024x1024, high quality
```

---

## 三、关键词词库

### 3.1 质量与风格词

**通用质量词：**
- `high quality`, `professional`, `app store ready`
- `clean`, `polished`, `refined`
- `1024x1024`, `high resolution`, `pixel perfect`

**设计风格词：**
- `flat design`, `material design`, `neumorphism`
- `minimalist`, `skeuomorphic`, `glassmorphism`
- `Swiss design`, `Bauhaus style`, `Memphis design`
- `Pop Art style`, `Acid design`, `Y2K aesthetic`
- `Cyberpunk style`, `Vaporwave`, `Art Deco`
- `Paper cut layered style`, `Isometric 3D`, `Graffiti style`
- `Chrome metallic`, `Holographic`, `Retro-futuristic`

**渲染质量词：**
- `smooth gradients`, `crisp edges`, `sharp details`
- `vibrant colors`, `balanced composition`
- `subtle shadows`, `soft glow`

### 3.2 常见图形关键词（中英对照）

| 中文 | 英文 Prompt 词 |
|------|---------------|
| 对勾/完成 | checkmark, tick, check symbol |
| 放大镜 | magnifying glass, search lens |
| 锁/安全 | padlock, shield, security lock |
| 闪电/速度 | lightning bolt, thunderbolt |
| 星星/收藏 | star, sparkle, asterisk |
| 齿轮/设置 | gear, cog, settings wheel |
| 铃铛/通知 | bell, notification bell |
| 纸飞机/发送 | paper plane, send arrow |
| 书/阅读 | book, open book, reading |
| 图表/数据 | bar chart, line graph, analytics |
| 花朵/自然 | flower, petal, bloom |
| 火焰/热门 | flame, fire, spark |
| 钻石/高端 | diamond, gem, crystal |
| 眼睛/监控 | eye, vision, iris |
| 链接/连接 | chain link, connection nodes |
| 地球/全球 | globe, earth, world |
| 指纹/识别 | fingerprint, biometric |
| 思维导图 | mind map, brain, neural network |
| 相机 | camera, lens, aperture |
| 音符/音乐 | music note, waveform, headphones |

### 3.3 颜色描述词

**渐变描述：**
- `gradient from [color] to [color]`
- `warm sunset gradient`
- `cool ocean gradient`
- `monochromatic [color] gradient`
- `rainbow gradient`

**具体颜色：**
- 蓝色系：`deep blue`, `sky blue`, `navy`, `cerulean`, `cobalt`
- 绿色系：`emerald green`, `mint`, `forest green`, `sage`
- 紫色系：`violet`, `lavender`, `deep purple`, `indigo`
- 橙色系：`coral`, `tangerine`, `amber`, `burnt orange`
- 红色系：`crimson`, `scarlet`, `rose red`

---

## 四、Prompt 优化技巧

### 4.1 避免的表达

- ❌ 过于抽象：`beautiful icon`（没有具体视觉指导）
- ❌ 矛盾指令：`realistic AND flat design`
- ❌ 过于复杂：描述超过5个不同图形元素
- ❌ 文字请求：`icon with text saying "APP"`（生图模型处理文字效果差）

### 4.2 增强效果的技巧

- ✅ 指定光源：`soft light from upper-left`
- ✅ 指定比例感：`icon fills 70% of canvas, centered`
- ✅ 参考风格：`in the style of Apple App Store icons`
- ✅ 排除不想要的：在 negative prompt 中排除 `text, watermark, realistic photo`
- ✅ 强调边缘：`crisp edges, clean outline`

### 4.3 迭代优化策略

第一轮：确立主形和色调
```
[基础 prompt] + [主色调] + [风格]
```

第二轮：细化细节
```
[前一轮成功的元素] + more detailed [具体细节] + [光影描述]
```

第三轮：精修质量
```
[前一轮 prompt] + ultra high quality, app store ready, pixel perfect
```

---

## 五、完整 Prompt 生成示例

### 场景：为一款「番茄钟时间管理工具」生成图标

**创意方向：** 番茄 + 时钟指针 + 极简渐变

**构建 prompt：**

```
App icon, stylized tomato shape with clock hands forming a timer dial inside,
modern flat design with subtle gradient, 
warm gradient background from red #E53E3E to orange #ED8936,
white minimalist clock hands symbol centered within tomato silhouette,
clean rounded square background, smooth gradient, vibrant warm colors,
professional productivity app icon, 1024x1024, app store quality
```

**Negative prompt（如支持）：**
```
text, watermark, realistic photo, complex details, multiple objects, dark background
```

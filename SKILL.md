---
name: wechat-article-publisher
description: 自动作为新媒体编辑撰写、排版并发布任意主题的公众号文章到微信草稿箱（需结合 generate_image 技能和 Python 脚本）。
metadata: {"requires": {"bins": ["python3"]}}
---

# WeChat Article Creator & Publisher (微信公众号文章创作与发布方案)

你是一位资深的新媒体编辑和排版专家，熟练掌握微信公众号的排版规范、内容创作技巧，并能自主使用工具完成文章的端到端发布。
当用户要求你“写一篇公众号文章”、“发布推文”、“创作公众号内容”时，请严格按照以下标准化流程（SOP）执行。

## 标准流程 (Workflow SOP)

### 阶段一：研究与创作 (Research & Write)
1. **确认需求**：通过与用户的对话或用户的原始指令，确认文章的 **主题**、**风格 (Style)**（如 purple, github, newsprint）、**基调**、以及**是否需要配图**。
2. **收集资料**：如有需要，自主使用你自带的 Web Search 功能收集素材。确保内容翔实且具深度。
3. **撰写 Markdown**：
   - 编写结构清晰、段落分明、钩子突出的文章 Markdown。
   - 在正文需要配图的地方，只需使用本地图片占位符，例如：`![展示架构图](/tmp/wechat_img_1.png)`。
   - 撰写完成后，将完整的 Markdown 文本写入一个临时文件，例如 `/tmp/article.md`。

### 阶段二：资产准备 (Asset Preparation)
利用你的 `generate_image` 等绘图工具生成文章需要的本地图片（如果有的话）。

1. **封面图 (Cover)**：微信公众号必须有封面图。请为其生成一张宽高比约为 16:9 的图片（或直接用 1:1），并保存为 `/tmp/wechat_cover.png`。
2. **内嵌配图**：根据你在 Markdown 文件中预留的路径（如 `/tmp/wechat_img_1.png`），生成对应的横版配图。
   - *注意*：生成图片时使用的 prompt 可以追加“中文标注”等提示指令，以适配中文文章的需求。

### 阶段三：自动化排版与发布 (Publishing)
环境要求：确保环境中已设置 `WECHAT_APPID` 和 `WECHAT_SECRET` 环境变量。

使用 `run_command` 工具调用发布脚本。脚本位于当前 Skill 的同一级目录：
```bash
# 假设脚本位于 ~/.gemini/antigravity/scratch/wechat-article-publisher/publish_to_wechat.py
# (请根据实际路径调用。如果你在执行此 skill，可用绝对路径)

python3 ~/.gemini/antigravity/scratch/wechat-article-publisher/publish_to_wechat.py \
  --markdown /tmp/article.md \
  --cover /tmp/wechat_cover.png \
  --title "用户要求的或你拟定的吸引人的文章标题（不超过20字符）" \
  --digest "文章的一句话精炼摘要，会在卡片上显示" \
  --style purple \
  --author "你设定的作者名"
```

### 阶段四：通知查阅 (Notify)
命令执行成功后，告知用户草稿创建完成：
“✅ 文章已成功生成排版并发布至微信公众号草稿箱！请登录公众平台后台查阅预览效果，确认无误后即可正式群发。”

---

## 排版样式 (Styles) 参考
你可以在阶段三的 `--style` 参数中选用以下预设值（定义均在 `styles.json` 中）：
- `purple`: 紫色经典（适合科技与深度分享）
- `purple-blue`: 紫蓝渐变（现代化主题）
- `orangeheart`: 橙心暖色（热情饱满，适合热点与生活）
- `github`: 程序员风格代码块（适合硬核技术/教程）
- `newsprint`: 报纸风格（复古报纸感阅读）
- `pixyll` / `whitey`: 极简留白风格
- `dyzj-light`: 浅亮淡雅

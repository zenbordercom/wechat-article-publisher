# WeChat Article Publisher (通用公众号发布 Skill)

一个通用的微信公众号文章自动创作与发布工具。它结合了 AI 的搜索与撰写能力、本地代码的 Markdown 渲染、以及微信素材库的自动上传 API，让你可以通过一句话指令产出排版精美的公众号推文。

## 功能特性

- **通用写作**：不再局限于 AI 资讯，支持任意领域的文章撰写（科技、医疗、管理、情感等）。
- **稳健渲染**：不再让 AI 直接手写脆弱的内联 CSS 和 HTML，而是通过 Python 的 `markdown` 和 `css-inline` 库在本地执行转换，杜绝格式错乱。
- **自动配图与上传**：AI 负责生成 Markdown 和本地图片，Python 脚本负责识别 Markdown 中的图片路径（如 `![配图](/tmp/img.png)`），自动上传到微信公众号并替换为 `mmbiz.qpic.cn` 的合法链接。
- **多主题支持**：内置 `styles.json` 包含十余种经典的公众号排版风格（如 purple, github, newsprint 等）。

## 安装依赖

在你的运行环境中安装所需的 Python 库：

```bash
cd ~/.gemini/antigravity/scratch/wechat-article-publisher
pip install -r requirements.txt
```

## 配置环境变量

请在环境中配置好以下微信开发者凭证（可在公众号后台 `开发 > 基本配置` 中获取）：

```bash
export WECHAT_APPID="your_appid_here"
export WECHAT_SECRET="your_secret_here"
```

## 使用方法

通常情况下，你无需手动执行脚本，**只需要对 AI Agent 说**：

> “帮我写一篇介绍微前端架构的公众号文章，配上代码示例和两张图，使用 Github 风格，写完后发到我公众号草稿箱。”

AI 会自动：
1. 搜索相关资料并撰写 Markdown。
2. 生成所需配图。
3. 调用本仓库下的 `publish_to_wechat.py` 完成发布。

### 手动调试

如果你想自己调用发布脚本，可以使用：

```bash
python3 publish_to_wechat.py \
  --markdown /path/to/article.md \
  --cover /path/to/cover.png \
  --title "微前端架构实践" \
  --digest "本文将深入探讨微前端的核心概念和落地经验..." \
  --style github
```

可以在 `styles.json` 中查阅和修改你喜欢的排版样式。

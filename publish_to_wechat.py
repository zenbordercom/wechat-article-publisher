import argparse
import json
import os
import re
import sys
import requests
import markdown
import css_inline

def get_access_token(appid, secret):
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    resp = requests.get(url).json()
    if 'access_token' not in resp:
        raise Exception(f"获取 Token 失败 / Failed to get token: {resp}")
    return resp['access_token']

def upload_permanent_image(token, file_path):
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    with open(file_path, "rb") as f:
        resp = requests.post(url, files={"media": f}).json()
    if 'media_id' not in resp:
        raise Exception(f"上传封面图失败 / Failed to upload permanent material {file_path}: {resp}")
    return resp['media_id']

def upload_article_image(token, file_path):
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
    with open(file_path, "rb") as f:
        resp = requests.post(url, files={"media": f}).json()
    if 'url' not in resp:
        raise Exception(f"上传正文图片失败 / Failed to upload article image {file_path}: {resp}")
    return resp['url']

def create_draft(token, article_data):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    resp = requests.post(
        url,
        data=json.dumps({"articles": [article_data]}, ensure_ascii=False).encode('utf-8'),
        headers=headers
    ).json()
    if 'media_id' not in resp:
        raise Exception(f"创建草稿失败 / Failed to create draft: {resp}")
    return resp['media_id']

def process_markdown_to_wechat_html(md_text, token, style_id, styles_file):
    # Load styles
    with open(styles_file, 'r', encoding='utf-8') as f:
        styles_config = json.load(f)["styles"]
    style = styles_config.get(style_id, styles_config["github"])
    
    # 1. Convert Markdown to HTML
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'sane_lists'])
    
    # 2. Upload local inline images and replace src in html
    # Match <img src="..."> or <img alt="..." src="...">
    img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')
    matches = img_pattern.finditer(html)
    for match in matches:
        local_src = match.group(1)
        if os.path.exists(local_src):
            print(f"  - Uploading article image: {local_src}")
            wechat_url = upload_article_image(token, local_src)
            html = html.replace(local_src, wechat_url)
        else:
            print(f"  - Warning: Image {local_src} not found locally. Skipping upload.")
    
    # 3. Add CSS classes to mapping tags for our basic theme
    base_css = f"""
    <style>
        .wechat-container {{
            font-family: {style['font']};
            line-height: 1.8;
            color: {style['text_color']};
            padding: 15px;
            font-size: 16px;
        }}
        .wechat-container h1, .wechat-container h2, .wechat-container h3 {{
            color: {style['title_color']};
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .wechat-container p {{
            margin-bottom: 20px;
            text-align: justify;
        }}
        .wechat-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            display: block;
            margin: 20px auto;
        }}
        .wechat-container blockquote {{
            background: {style['quote_bg']};
            border-left: 4px solid {style['quote_border']};
            padding: 12px 16px;
            color: {style['text_color']};
            margin: 20px 0;
        }}
        .wechat-container a {{
            color: {style['link_color']};
            text-decoration: none;
        }}
        .wechat-container pre {{
            background: #f6f8fa;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        .wechat-container code {{
            background: #f6f8fa;
            padding: 2px 5px;
            border-radius: 4px;
            color: #d73a49;
            font-family: monospace;
        }}
        .wechat-container table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        .wechat-container th, .wechat-container td {{
            border: 1px solid #dfe2e5;
            padding: 8px 12px;
        }}
        .wechat-container th {{
            background: #f6f8fa;
        }}
        .wechat-container ul, .wechat-container ol {{
            margin-bottom: 20px;
            padding-left: 20px;
        }}
    </style>
    """
    
    full_html = f"<html><head>{base_css}</head><body><section class='wechat-container'>{html}</section></body></html>"
    
    # 4. Inline CSS
    inliner = css_inline.CSSInliner(keep_style_tags=False, inline_style_tags=True)
    try:
        inlined_html = inliner.inline(full_html)
    except Exception as e:
        print(f"Error inlining CSS (fallback to raw html): {e}")
        inlined_html = full_html
    
    # Extract just the contents of body
    body_match = re.search(r'<body[^>]*>(.*?)</body>', inlined_html, re.DOTALL | re.IGNORECASE)
    if body_match:
        final_html = body_match.group(1).strip()
    else:
        final_html = html # absolute fallback
        
    return final_html

def main():
    parser = argparse.ArgumentParser(description="WeChat Article Publisher")
    parser.add_argument("--markdown", required=True, help="Path to article markdown file")
    parser.add_argument("--cover", required=True, help="Path to cover image file (local)")
    parser.add_argument("--title", required=True, help="Article title")
    parser.add_argument("--digest", required=True, help="Article digest")
    parser.add_argument("--style", default="purple", help="CSS Style ID from styles.json")
    parser.add_argument("--author", default="AI Writer", help="Author name")
    
    args = parser.parse_args()
    
    appid = os.environ.get("WECHAT_APPID")
    secret = os.environ.get("WECHAT_SECRET")
    
    if not appid or not secret:
        print("错误: 必须在环境变量中设置 WECHAT_APPID 和 WECHAT_SECRET。")
        sys.exit(1)
        
    print("1. 获取微信接口 Token...")
    try:
        token = get_access_token(appid, secret)
    except Exception as e:
        print(e)
        sys.exit(1)
    
    print(f"2. 上传封面图片: {args.cover}")
    try:
        thumb_media_id = upload_permanent_image(token, args.cover)
    except Exception as e:
        print(e)
        sys.exit(1)
    
    print(f"3. 注入Markdown样式及上传正文图片...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    styles_file = os.path.join(base_dir, "styles.json")
    
    try:
        with open(args.markdown, "r", encoding="utf-8") as f:
            md_text = f.read()
    except Exception as e:
        print(f"读取 Markdown 文件失败: {e}")
        sys.exit(1)
        
    html_content = process_markdown_to_wechat_html(md_text, token, args.style, styles_file)
    
    print("4. 生成并提交草稿箱...")
    article_data = {
        "title": args.title,
        "author": args.author,
        "digest": args.digest,
        "content": html_content,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }
    
    try:
        draft_media_id = create_draft(token, article_data)
        print("\n✅ 成功发布到微信公众号草稿箱！")
        print(f"草稿 Media ID: {draft_media_id}")
        print("请前往微信公众平台后台查阅预览并正式群发。")
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()

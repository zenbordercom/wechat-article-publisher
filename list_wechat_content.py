import os
import json
import requests
import sys

def get_access_token(appid, secret):
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    resp = requests.get(url).json()
    if 'access_token' not in resp:
        raise Exception(f"获取 Token 失败: {resp}")
    return resp['access_token']

def list_drafts(token, offset=0, count=10):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}"
    data = {"offset": offset, "count": count, "no_content": 1}
    resp = requests.post(url, json=data).json()
    return resp

def list_published(token, offset=0, count=10):
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/batchget?access_token={token}"
    data = {"offset": offset, "count": count, "no_content": 1}
    resp = requests.post(url, json=data).json()
    return resp

def main():
    appid = os.environ.get("WECHAT_APPID")
    secret = os.environ.get("WECHAT_SECRET")
    if not appid or not secret:
        print("Error: Missing WECHAT_APPID or WECHAT_SECRET")
        sys.exit(1)
        
    token = get_access_token(appid, secret)
    
    print("--- 最近的草稿 (Drafts) ---")
    drafts = list_drafts(token)
    if 'item' in drafts and drafts['item']:
        # Debug structure
        # print("Debug draft raw data:", json.dumps(drafts['item'][0], indent=2))
        for item in drafts['item']:
            articles = item.get('content', {}).get('news_item', [])
            if articles:
                article = articles[0]
                # Some keys might be media_id vs article_id depending on published or draft
                article_id = item.get('media_id') or item.get('article_id') or "N/A"
                print(f"Title: {article['title']} | ID: {article_id}")
    else:
        print("No drafts found or error:", drafts)
        
    print("\n--- 最近已发布的文章 (Published) ---")
    published = list_published(token)
    if 'item' in published:
        for item in published['item']:
            article = item['content']['news_item'][0]
            print(f"Title: {article['title']} | ID: {item['article_id']}")
    else:
        print("No published articles found or error:", published)

if __name__ == "__main__":
    main()

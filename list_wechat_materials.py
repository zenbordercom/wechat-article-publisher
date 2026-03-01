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

def list_materials(token, mtype="image", offset=0, count=20):
    url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}"
    data = {
        "type": mtype,
        "offset": offset,
        "count": count
    }
    resp = requests.post(url, json=data).json()
    return resp

def main():
    appid = os.environ.get("WECHAT_APPID")
    secret = os.environ.get("WECHAT_SECRET")
    if not appid or not secret:
        print("Error: Missing WECHAT_APPID or WECHAT_SECRET")
        sys.exit(1)
        
    try:
        token = get_access_token(appid, secret)
        print(f"--- 最近的图片素材 (Image Materials) ---")
        materials = list_materials(token, "image")
        
        if 'item' in materials:
            print(f"总计找到 {materials.get('total_count', 0)} 个素材。显示最近的 {materials.get('item_count', 0)} 个：")
            for item in materials['item']:
                name = item.get('name', '未命名')
                media_id = item.get('media_id')
                url = item.get('url')
                print(f"Name: {name} | Media_ID: {media_id} | URL: {url}\n")
        else:
            print("未能获取素材列表，返回数据:", json.dumps(materials, indent=2))
            
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()

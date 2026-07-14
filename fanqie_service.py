# -*- coding: utf-8 -*-
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 番茄下载器的 Web API 地址
TOMATO_API_BASE = "http://127.0.0.1:18423"


def search_books(keyword):
    """搜索番茄小说"""
    url = f"{TOMATO_API_BASE}/api/search"
    params = {"q": keyword}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])

            results = []
            for item in items:
                raw = item.get('raw', {})
                results.append({
                    'book_id': raw.get('book_id', ''),
                    'title': raw.get('book_name', ''),
                    'author': raw.get('author', ''),
                    'score': raw.get('score', ''),
                    'cover': raw.get('thumb_url', ''),
                    'abstract': raw.get('abstract', '')[:200],
                    'category': raw.get('category', ''),
                    'read_count': raw.get('read_cnt_text', ''),
                })
            return results
        else:
            print(f"请求失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"搜索异常: {e}")
        return []


def get_book_detail(book_id):
    """获取单本书的详细信息"""
    # 先搜索，然后从结果中提取
    # 或者可以直接调用详情 API（如果有的话）
    pass


# 测试
if __name__ == "__main__":
    results = search_books("斩神")
    print(f"找到 {len(results)} 本书")
    for book in results[:3]:
        print(f"\n📚 {book['title']}")
        print(f"   作者: {book['author']}")
        print(f"   评分: {book['score']}")
        print(f"   封面: {book['cover']}")
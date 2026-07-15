from flask import Flask, render_template, request, redirect, url_for, send_file, abort, jsonify, Response, session
from flask_caching import Cache
from models import db, Novel
import requests
import io
import os
import hashlib
import random
import json
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///novels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ===== 缓存配置 =====
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# ===== 分类颜色配置 =====
CATEGORY_COLORS = {
    '男频·都市': '#4A90D9',
    '男频·玄幻': '#9B59B6',
    '男频·仙侠': '#1ABC9C',
    '男频·科幻': '#3498DB',
    '男频·悬疑': '#2C3E50',
    '男频·衍生': '#E67E22',
    '男频·二次元': '#E91E63',
    '女频·现代言情': '#FF6B81',
    '女频·古风言情': '#E74C3C',
    '女频·玄幻言情': '#9B59B6',
    '女频·古代言情': '#C0392B',
    '女频·衍生': '#E67E22',
    '女频·都市言情': '#FF6B81',
    '未分类': '#95A5A6',
}


# ===== 自定义过滤器 =====
@app.template_filter('stars')
def stars_filter(rating):
    if not rating:
        return ''
    full = int(rating // 2)
    half = 1 if rating % 2 >= 0.5 else 0
    empty = 5 - full - half

    result = ''
    for i in range(full):
        result += '<i class="bi bi-star-fill text-warning"></i>'
    for i in range(half):
        result += '<i class="bi bi-star-half text-warning"></i>'
    for i in range(empty):
        result += '<i class="bi bi-star text-warning"></i>'
    return result


@app.template_filter('category_color')
def category_color_filter(category):
    return CATEGORY_COLORS.get(category, '#6C757D')


@app.template_filter('from_json')
def from_json_filter(json_str):
    if not json_str:
        return []
    try:
        return json.loads(json_str)
    except:
        return []


# ===== 封面下载函数（已禁用，保留备用） =====
def download_cover_to_local(url):
    """下载封面到本地（已禁用，使用 weserv 代理）"""
    return None


# ===== 错误处理 =====
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


# ===== 静态文件缓存 =====
@app.after_request
def add_header(response):
    if 'static' in request.path:
        response.headers['Cache-Control'] = 'public, max-age=86400'
    if request.path.startswith('/cover') or 'image' in request.path:
        response.headers['Cache-Control'] = 'public, max-age=604800'
    return response


# ===== 导出书单 =====
@app.route('/export')
def export_data():
    novels = Novel.query.all()
    data = []
    for n in novels:
        data.append({
            'title': n.title,
            'author': n.author,
            'category': n.category,
            'rating': n.rating,
            'summary': n.summary,
            'recommendation': n.recommendation,
            'platform': n.platform,
            'read_date': n.read_date,
            'book_id': n.book_id,
            'cover': n.cover,
            'word_count': n.word_count,
            'chapter_count': n.chapter_count,
            'status': n.status,
            'read_count': n.read_count,
            'want_to_read': n.want_to_read,
            'progress': n.progress,
            'rating_history': n.rating_history
        })

    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    return Response(
        json_str,
        mimetype='application/json; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=booklist.json'}
    )


# ===== 导入书单 =====
@app.route('/import', methods=['GET', 'POST'])
def import_data():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return "请选择文件", 400

        try:
            data = json.load(file)
            count = 0

            for item in data:
                existing = Novel.query.filter_by(title=item.get('title')).first()
                if not existing:
                    novel = Novel(
                        title=item.get('title', ''),
                        author=item.get('author', ''),
                        category=item.get('category', ''),
                        cover=item.get('cover', ''),
                        summary=item.get('summary', ''),
                        rating=item.get('rating', 0),
                        recommendation=item.get('recommendation', ''),
                        platform=item.get('platform', '番茄小说'),
                        read_date=item.get('read_date', ''),
                        book_id=item.get('book_id', ''),
                        word_count=item.get('word_count', ''),
                        chapter_count=item.get('chapter_count', ''),
                        status=item.get('status', '连载中'),
                        read_count=item.get('read_count', ''),
                        want_to_read=item.get('want_to_read', False),
                        progress=item.get('progress', 0),
                        rating_history=item.get('rating_history', '')
                    )
                    db.session.add(novel)
                    count += 1
            db.session.commit()
            cache.clear()
            return render_template('import.html', success=True, count=count)
        except Exception as e:
            return f"导入失败: {e}", 500

    return render_template('import.html', success=False)


# ===== 更新阅读进度 =====
@app.route('/update_progress/<int:novel_id>', methods=['POST'])
def update_progress(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    progress = request.form.get('progress', 0, type=int)
    novel.progress = progress
    db.session.commit()
    return redirect(url_for('detail', novel_id=novel.id))


# ===== 清空搜索历史 =====
@app.route('/clear_history')
def clear_history():
    session.pop('search_history', None)
    return redirect(url_for('search'))


# ===== 换一换今日推荐 =====
@app.route('/refresh_today')
def refresh_today():
    referer = request.headers.get('Referer', '/')
    novels = Novel.query.filter_by(want_to_read=False).all()
    if not novels:
        return redirect(referer)

    random.seed()
    today_recommendation = random.choice(novels)
    session['custom_today'] = today_recommendation.id

    return redirect(referer)


# ===== 番茄小说 API 配置 =====
TOMATO_API_BASE = "http://127.0.0.1:18423"


# ===== 自动分类映射 =====
def get_category_name(raw_category, gender):
    male_categories = {
        '都市': '都市', '玄幻': '玄幻', '仙侠': '仙侠', '历史': '历史',
        '军事': '军事', '科幻': '科幻', '悬疑': '悬疑', '灵异': '灵异',
        '游戏': '游戏', '体育': '体育', '同人': '同人', '衍生': '衍生',
        '女频衍生': '衍生', '男频衍生': '衍生', '动漫衍生': '衍生',
        '二次元': '二次元', '轻小说': '轻小说', '系统': '系统',
        '无敌': '无敌', '穿越': '穿越', '都市高武': '都市',
        '都市异能': '都市', '都市脑洞': '都市', '奇幻': '奇幻',
        '神话': '神话', '西幻': '西幻', '玄幻言情': '玄幻言情',
        '冒险': '冒险',
    }

    female_categories = {
        '现代言情': '现代言情', '古风言情': '古风言情',
        '玄幻言情': '玄幻言情', '仙侠言情': '仙侠言情',
        '古代言情': '古代言情', '青春校园': '青春校园',
        '悬疑推理': '悬疑推理', '科幻空间': '科幻空间',
        '轻小说': '轻小说', '女频衍生': '衍生', '衍生': '衍生',
        '同人': '同人', '穿越': '穿越', '重生': '重生',
        '快穿': '快穿', '娱乐圈': '娱乐圈', '职场': '职场',
        '都市': '都市言情', '古代': '古代言情', '甜文': '甜文',
        '虐文': '虐文', '爽文': '爽文',
    }

    if int(gender) == 1:
        mapping = male_categories
        prefix = '男频·'
    else:
        mapping = female_categories
        prefix = '女频·'

    if raw_category in mapping:
        return prefix + mapping[raw_category]

    for key, value in mapping.items():
        if key in raw_category or raw_category in key:
            return prefix + value

    return prefix + raw_category if raw_category else '未分类'


def search_tomato_books(keyword, page=1, size=30):
    url = f"{TOMATO_API_BASE}/api/search"
    params = {"q": keyword, "page": page, "size": size}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])

            results = []
            for item in items:
                raw = item.get('raw', {})
                book_id = raw.get('book_id', '')
                cover_url = raw.get('thumb_url', '') or raw.get('expand_thumb_url', '')
                creation_status = raw.get('creation_status', '0')
                status = '已完结' if creation_status == '0' else '连载中'

                results.append({
                    'book_id': book_id,
                    'title': raw.get('book_name', ''),
                    'author': raw.get('author', ''),
                    'score': float(raw.get('score', 0)) if raw.get('score') else 0,
                    'cover': cover_url,
                    'abstract': raw.get('abstract', '')[:300],
                    'category': raw.get('category', ''),
                    'gender': raw.get('gender', 1),
                    'read_count': raw.get('read_cnt_text', ''),
                    'read_url': f"https://fanqienovel.com/page/{book_id}" if book_id else '',
                    'word_count': raw.get('word_number', ''),
                    'chapter_count': raw.get('serial_count', ''),
                    'status': status,
                })
            return results
        else:
            return []
    except Exception as e:
        print(f"搜索异常: {e}")
        return []


# ===== 创建数据库表 =====
with app.app_context():
    db.create_all()


# ===== 首页 =====
@app.route('/')
@cache.cached(timeout=300, unless=lambda: request.args.get('list') == 'want' or request.args.get('rating') != 'all')
def index():
    sort = request.args.get('sort', 'latest')
    rating_filter = request.args.get('rating', 'all')
    list_type = request.args.get('list', 'read')

    if list_type == 'want':
        novels = Novel.query.filter_by(want_to_read=True).all()
    else:
        novels = Novel.query.filter_by(want_to_read=False).all()

    if rating_filter == '9plus':
        novels = [n for n in novels if n.rating and n.rating >= 9]
    elif rating_filter == '8plus':
        novels = [n for n in novels if n.rating and n.rating >= 8]
    elif rating_filter == '7plus':
        novels = [n for n in novels if n.rating and n.rating >= 7]
    elif rating_filter == '6plus':
        novels = [n for n in novels if n.rating and n.rating >= 6]
    elif rating_filter == '5below':
        novels = [n for n in novels if n.rating and n.rating < 5]

    if sort == 'rating_high':
        novels = sorted(novels, key=lambda x: x.rating or 0, reverse=True)
    elif sort == 'rating_low':
        novels = sorted(novels, key=lambda x: x.rating or 0)
    elif sort == 'title_asc':
        novels = sorted(novels, key=lambda x: x.title)
    elif sort == 'title_desc':
        novels = sorted(novels, key=lambda x: x.title, reverse=True)
    else:
        novels = sorted(novels, key=lambda x: x.id, reverse=True)

    featured_novels = Novel.query.filter_by(featured=True).all()
    if not featured_novels:
        featured_novels = novels[:4] if novels else []

    today_recommendation = None
    if novels:
        custom_id = session.get('custom_today')
        if custom_id:
            today_recommendation = Novel.query.filter_by(id=custom_id, want_to_read=False).first()

        if not today_recommendation:
            today_seed = date.today().toordinal()
            random.seed(today_seed)
            today_recommendation = random.choice(novels)
            random.seed()

    all_books = Novel.query.all()
    category_counts = {}
    for novel in all_books:
        if novel.category and novel.category != '未分类':
            category_counts[novel.category] = category_counts.get(novel.category, 0) + 1

    all_categories = sorted(category_counts.keys())

    read_count = Novel.query.filter_by(want_to_read=False).count()
    want_count = Novel.query.filter_by(want_to_read=True).count()

    return render_template('index.html',
                           novels=novels,
                           featured_novels=featured_novels,
                           categories=all_categories,
                           category_counts=category_counts,
                           current_category='全部',
                           current_sort=sort,
                           rating_filter=rating_filter,
                           list_type=list_type,
                           today_recommendation=today_recommendation,
                           read_count=read_count,
                           want_count=want_count)


# ===== 按分类筛选 =====
@app.route('/category/<category_name>')
def category_filter(category_name):
    sort = request.args.get('sort', 'latest')
    rating_filter = request.args.get('rating', 'all')
    list_type = request.args.get('list', 'read')

    if category_name == '全部':
        if list_type == 'want':
            novels = Novel.query.filter_by(want_to_read=True).all()
        else:
            novels = Novel.query.filter_by(want_to_read=False).all()
    else:
        if list_type == 'want':
            novels = Novel.query.filter_by(category=category_name, want_to_read=True).all()
        else:
            novels = Novel.query.filter_by(category=category_name, want_to_read=False).all()

    if rating_filter == '9plus':
        novels = [n for n in novels if n.rating and n.rating >= 9]
    elif rating_filter == '8plus':
        novels = [n for n in novels if n.rating and n.rating >= 8]
    elif rating_filter == '7plus':
        novels = [n for n in novels if n.rating and n.rating >= 7]
    elif rating_filter == '6plus':
        novels = [n for n in novels if n.rating and n.rating >= 6]
    elif rating_filter == '5below':
        novels = [n for n in novels if n.rating and n.rating < 5]

    if sort == 'rating_high':
        novels = sorted(novels, key=lambda x: x.rating or 0, reverse=True)
    elif sort == 'rating_low':
        novels = sorted(novels, key=lambda x: x.rating or 0)
    elif sort == 'title_asc':
        novels = sorted(novels, key=lambda x: x.title)
    elif sort == 'title_desc':
        novels = sorted(novels, key=lambda x: x.title, reverse=True)
    else:
        novels = sorted(novels, key=lambda x: x.id, reverse=True)

    all_books = Novel.query.all()
    category_counts = {}
    for novel in all_books:
        if novel.category and novel.category != '未分类':
            category_counts[novel.category] = category_counts.get(novel.category, 0) + 1

    featured_novels = Novel.query.filter_by(featured=True).all()
    if not featured_novels:
        featured_novels = all_books[:4] if all_books else []

    all_categories = sorted(category_counts.keys())

    read_count = Novel.query.filter_by(want_to_read=False).count()
    want_count = Novel.query.filter_by(want_to_read=True).count()

    return render_template('index.html',
                           novels=novels,
                           featured_novels=featured_novels,
                           categories=all_categories,
                           category_counts=category_counts,
                           current_category=category_name,
                           current_sort=sort,
                           rating_filter=rating_filter,
                           list_type=list_type,
                           read_count=read_count,
                           want_count=want_count)


# ===== 仪表盘 =====
@app.route('/dashboard')
@cache.cached(timeout=300)
def dashboard():
    novels = Novel.query.all()

    total = len(novels)
    read_count = Novel.query.filter_by(want_to_read=False).count()
    want_count = Novel.query.filter_by(want_to_read=True).count()

    read_books = [n for n in novels if not n.want_to_read and n.rating]
    avg_rating = round(sum(n.rating for n in read_books) / len(read_books), 1) if read_books else 0

    category_data = {}
    for novel in novels:
        if novel.category:
            category_data[novel.category] = category_data.get(novel.category, 0) + 1

    rating_dist = {'0-5': 0, '5-6': 0, '6-7': 0, '7-8': 0, '8-9': 0, '9-10': 0}
    for novel in read_books:
        r = novel.rating or 0
        if r < 5:
            rating_dist['0-5'] += 1
        elif r < 6:
            rating_dist['5-6'] += 1
        elif r < 7:
            rating_dist['6-7'] += 1
        elif r < 8:
            rating_dist['7-8'] += 1
        elif r < 9:
            rating_dist['8-9'] += 1
        else:
            rating_dist['9-10'] += 1

    recent_books = sorted(novels, key=lambda x: x.id, reverse=True)[:5]

    return render_template('dashboard.html',
                           total=total,
                           read_count=read_count,
                           want_count=want_count,
                           avg_rating=avg_rating,
                           category_data=category_data,
                           rating_dist=rating_dist,
                           recent_books=recent_books,
                           novels=novels)


# ===== 评分趋势 API =====
@app.route('/api/rating_trend/<int:novel_id>')
def rating_trend_api(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    history = json.loads(novel.rating_history) if novel.rating_history else []

    if len(history) < 2:
        return jsonify({
            'labels': [],
            'data': [],
            'title': novel.title,
            'message': '暂无足够评分数据'
        })

    labels = [h['date'] for h in history]
    data = [h['rating'] for h in history]

    return jsonify({
        'labels': labels,
        'data': data,
        'title': novel.title,
        'current_rating': novel.rating
    })


# ===== 随机跳转 =====
@app.route('/random')
def random_book():
    books = Novel.query.all()
    if not books:
        return redirect(url_for('index'))
    book = random.choice(books)
    return redirect(url_for('detail', novel_id=book.id))


# ===== 搜索自动补全 =====
@app.route('/api/autocomplete')
def autocomplete():
    keyword = request.args.get('q', '').strip()
    if not keyword or len(keyword) < 1:
        return jsonify([])

    novels = Novel.query.filter(Novel.title.contains(keyword)).limit(10).all()
    suggestions = []
    for novel in novels:
        suggestions.append({
            'label': f"{novel.title} - {novel.author}",
            'value': novel.title,
            'id': novel.id
        })
    return jsonify(suggestions)


# ===== 切换轮播图标记 =====
@app.route('/toggle_featured/<int:novel_id>')
def toggle_featured(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    novel.featured = not novel.featured
    db.session.commit()
    cache.clear()
    referer = request.headers.get('Referer', '/')
    return redirect(referer)


# ===== 切换"想看"状态 =====
@app.route('/toggle_want/<int:novel_id>')
def toggle_want(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    novel.want_to_read = not novel.want_to_read
    db.session.commit()
    cache.clear()
    referer = request.headers.get('Referer', '/')
    return redirect(referer)


# ===== 从书单移除书籍 =====
@app.route('/remove_book/<int:novel_id>', methods=['POST'])
def remove_book(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    if novel.featured:
        novel.featured = False
    db.session.delete(novel)
    db.session.commit()
    cache.clear()
    referer = request.headers.get('Referer', '/')
    return redirect(referer)


# ===== 编辑推荐语 =====
@app.route('/edit_recommendation/<int:novel_id>', methods=['GET', 'POST'])
def edit_recommendation(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    if request.method == 'POST':
        recommendation = request.form.get('recommendation', '').strip()
        novel.recommendation = recommendation
        db.session.commit()
        return redirect(url_for('detail', novel_id=novel.id))
    return render_template('edit_recommendation.html', novel=novel)


# ===== 小说详情页 =====
@app.route('/novel/<int:novel_id>')
def detail(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    return render_template('detail.html', novel=novel)


# ===== 下载并保存封面到本地 =====
@app.route('/cover')
def get_cover():
    """获取封面图片，直接返回番茄图片"""
    url = request.args.get('url')
    if not url:
        return '', 400

    try:
        # 直接请求番茄的图片
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://fanqienovel.com/",
        }
        response = requests.get(url, headers=headers, timeout=10)

        # 如果番茄返回成功，直接返回图片
        if response.status_code == 200:
            return send_file(
                io.BytesIO(response.content),
                mimetype=response.headers.get('Content-Type', 'image/jpeg')
            )
        else:
            # 如果番茄返回失败，返回默认封面
            default = "https://img3.doubanio.com/f/shire/5522dd1f5b742d1b3ce3f0e1c1b7f1a8c0f2e3e8.jpg"
            return redirect(default)
    except Exception as e:
        print(f"封面获取错误: {e}")
        # 异常时返回默认封面
        default = "https://img3.doubanio.com/f/shire/5522dd1f5b742d1b3ce3f0e1c1b7f1a8c0f2e3e8.jpg"
        return redirect(default)


# ===== 更新评分 =====
@app.route('/update_ratings')
def update_ratings():
    novels = Novel.query.all()
    updated = 0
    for novel in novels:
        if novel.book_id:
            results = search_tomato_books(novel.title, page=1, size=5)
            for item in results:
                if item['book_id'] == novel.book_id:
                    new_score = item['score']
                    if new_score != novel.rating:
                        novel.rating = new_score
                        history = json.loads(novel.rating_history) if novel.rating_history else []
                        history.append({
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'rating': new_score
                        })
                        novel.rating_history = json.dumps(history[-30:])
                        updated += 1
                    break
    db.session.commit()
    return f"更新完成，{updated} 本书评分已更新"


# ===== 从番茄小说添加到书单（AJAX） =====
@app.route('/add_from_tomato_ajax', methods=['POST'])
def add_from_tomato_ajax():
    book_id = request.form.get('book_id')
    title = request.form.get('title')
    keyword = request.form.get('keyword', title)
    list_type = request.form.get('list_type', 'read')

    if not book_id or not title:
        return jsonify({'success': False, 'message': '参数错误'})

    existing = Novel.query.filter_by(title=title).first()

    if existing:
        if list_type == 'want':
            existing.want_to_read = True
            list_name = "想看"
        else:
            existing.want_to_read = False
            list_name = "已读推荐"
        db.session.commit()
        cache.clear()
        return jsonify({'success': True, 'message': f'✅ 已将《{title}》切换到「{list_name}」'})

    results = search_tomato_books(keyword)
    book_data = None
    for item in results:
        if item['book_id'] == book_id:
            book_data = item
            break

    if not book_data:
        return jsonify({'success': False, 'message': '未找到该书籍'})

    raw_category = book_data.get('category', '')
    gender = book_data.get('gender', 1)
    category_name = get_category_name(raw_category, gender)

    want_to_read = True if list_type == 'want' else False
    list_name = "想看" if list_type == 'want' else "已读推荐"

    rating_history = json.dumps([{
        'date': datetime.now().strftime('%Y-%m-%d'),
        'rating': book_data['score']
    }])

    novel = Novel(
        title=book_data['title'],
        author=book_data['author'],
        category=category_name,
        cover=book_data['cover'],
        summary=book_data['abstract'],
        rating=book_data['score'],
        recommendation="",
        platform="番茄小说",
        read_date="",
        book_id=book_data['book_id'],
        word_count=book_data.get('word_count', ''),
        chapter_count=book_data.get('chapter_count', ''),
        status=book_data.get('status', '连载中'),
        read_count=book_data.get('read_count', ''),
        want_to_read=want_to_read,
        rating_history=rating_history
    )

    db.session.add(novel)
    db.session.commit()
    cache.clear()

    return jsonify({'success': True, 'message': f'✅ 已成功添加《{title}》到「{list_name}」'})


# ===== 搜索番茄小说 =====
@app.route('/search')
def search():
    keyword = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 30, type=int)

    if keyword:
        history = session.get('search_history', [])
        if keyword in history:
            history.remove(keyword)
        history.insert(0, keyword)
        session['search_history'] = history[:10]

    results = []
    if keyword:
        results = search_tomato_books(keyword, page=page, size=size)
        existing_titles = set(novel.title for novel in Novel.query.all())
        for book in results:
            book['is_added'] = book['title'] in existing_titles

    return render_template('search.html',
                           keyword=keyword,
                           results=results,
                           page=page,
                           size=size)


# ===== 从番茄小说添加到书单（表单提交，保留兼容） =====
@app.route('/add_from_tomato', methods=['POST'])
def add_from_tomato():
    book_id = request.form.get('book_id')
    title = request.form.get('title')
    keyword = request.form.get('keyword', title)
    list_type = request.form.get('list_type', 'read')

    if not book_id or not title:
        return redirect(url_for('search'))

    existing = Novel.query.filter_by(title=title).first()

    if existing:
        if list_type == 'want':
            existing.want_to_read = True
            list_name = "想看"
        else:
            existing.want_to_read = False
            list_name = "已读推荐"
        db.session.commit()
        cache.clear()
        return redirect(url_for('search', q=keyword))

    results = search_tomato_books(keyword)
    book_data = None
    for item in results:
        if item['book_id'] == book_id:
            book_data = item
            break

    if not book_data:
        return "未找到该书籍", 404

    raw_category = book_data.get('category', '')
    gender = book_data.get('gender', 1)
    category_name = get_category_name(raw_category, gender)

    want_to_read = True if list_type == 'want' else False

    rating_history = json.dumps([{
        'date': datetime.now().strftime('%Y-%m-%d'),
        'rating': book_data['score']
    }])

    novel = Novel(
        title=book_data['title'],
        author=book_data['author'],
        category=category_name,
        cover=book_data['cover'],
        summary=book_data['abstract'],
        rating=book_data['score'],
        recommendation="",
        platform="番茄小说",
        read_date="",
        book_id=book_data['book_id'],
        word_count=book_data.get('word_count', ''),
        chapter_count=book_data.get('chapter_count', ''),
        status=book_data.get('status', '连载中'),
        read_count=book_data.get('read_count', ''),
        want_to_read=want_to_read,
        rating_history=rating_history
    )

    db.session.add(novel)
    db.session.commit()
    cache.clear()

    return redirect(url_for('search', q=keyword))


if __name__ == '__main__':
    app.run(debug=True)
# config.py
import os


class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///novels.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # 番茄小说 API 配置
    TOMATO_API_BASE = os.environ.get('TOMATO_API_BASE', 'http://127.0.0.1:18423')

    # 分类颜色配置
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
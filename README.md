# 📚 我的私人书单

> 一个基于 Flask 的个人小说推荐网站，支持从番茄小说搜索书籍、自动获取评分和封面、分类管理、阅读进度记录等功能。

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)

---

## ✨ 功能特点

### 📖 书籍管理
| 功能 | 说明 |
|------|------|
| 🔍 搜索添加 | 从番茄小说搜索书籍，自动获取书名、作者、评分、封面、简介 |
| 📋 双列表管理 | 支持「已读推荐」和「想看」两种状态，互不干扰 |
| 🏷️ 自动分类 | 根据番茄小说标签自动生成「男频·XX」或「女频·XX」分类 |
| 📊 阅读进度 | 在「想看」列表中记录读到第几章 |

### 🎨 展示功能
| 功能 | 说明 |
|------|------|
| 🎠 轮播图 | 首页轮播展示精选书籍，支持手动设置 |
| 📅 今日推荐 | 每天随机推荐一本书，支持「换一换」 |
| 🔖 分类筛选 | 按分类快速筛选书籍 |
| 📊 多维度排序 | 支持按最新添加、评分高低、书名排序 |
| ⭐ 评分筛选 | 按评分区间筛选（9分以上、8分以上等） |

### ✏️ 个性化
| 功能 | 说明 |
|------|------|
| 💬 推荐语编辑 | 为每本书写下你的阅读感受 |
| 🖼️ 封面自动下载 | 封面自动保存到本地，无需担心防盗链 |

### 🔧 数据管理
| 功能 | 说明 |
|------|------|
| 📤 导入/导出 | 一键导出书单为 JSON 文件，方便备份和迁移 |
| 🕐 搜索历史 | 自动保存最近搜索关键词 |

### 🎯 用户体验
| 功能 | 说明 |
|------|------|
| 📱 移动端适配 | 手机端自动适配，导航栏折叠 |
| ⌨️ 快捷键 | `Ctrl+K` 快速跳转搜索框，`ESC` 清空搜索框 |
| ⏳ 加载动画 | 页面切换平滑过渡 |
| 🔝 回到顶部 | 滚动后自动显示返回顶部按钮 |

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Flask + SQLAlchemy |
| 数据库 | SQLite |
| 前端 | Bootstrap 5 + Bootstrap Icons + jQuery UI |
| 部署 | PythonAnywhere |

---

## 📁 项目结构
```bash
personProject/
├── app.py # 主程序
├── models.py # 数据库模型
├── requirements.txt # 依赖清单
├── .gitignore # Git忽略文件
│
├── static/ # 静态文件
│ ├── css/
│ │ └── style.css # 自定义样式
│ ├── covers/ # 书籍封面（自动生成）
│ └── favicon.png # 网站图标
│
├── templates/ # HTML模板
│ ├── base.html # 基础模板
│ ├── index.html # 首页
│ ├── search.html # 搜索页
│ ├── detail.html # 详情页
│ ├── edit_recommendation.html # 编辑推荐语
│ └── import.html # 导入书单
│
├── instance/
│ └── novels.db # SQLite数据库
│
├── start.bat # 一键启动脚本（Windows）
└── stop.bat # 一键停止脚本（Windows）
```

---

## 🚀 快速开始

### 本地运行

#### 1. 克隆项目
```bash
git clone https://github.com/liang-yuan-yuan/novel-recommend.git
cd novel-recommend
```

#### 2. 创建虚拟环境
```
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 运行项目
```bash
python app.py
```

一键启动（Windows）
双击 start.bat 即可自动启动所有服务并打开浏览器。

📦 依赖清单
```bash
text
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
requests==2.31.0
Pillow==10.1.0
pillow-heif==1.4.0
gunicorn==21.2.0
```

🔗 在线演示
平台	          地址
PythonAnywhere	https://liang233.pythonanywhere.com

📝 注意事项
⚠️ 搜索功能
部署到云端后，由于番茄小说API限制，搜索功能可能不可用。推荐在本地添加书籍后，通过「导出/导入」功能同步数据到云端。

🖼️ 封面图片
封面图片会自动下载到 static/covers/ 目录，首次加载可能需要稍等片刻。

💾 数据备份
建议定期使用「导出」功能备份书单数据，防止数据丢失。

📄 开源协议
```bash
MIT License
Copyright (c) 2026 liang-yuan-yuan
```

👤 作者
```bash
liang-yuan-yuan
GitHub: @liang-yuan-yuan
```





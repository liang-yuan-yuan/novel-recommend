from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Novel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    cover = db.Column(db.String(200))
    summary = db.Column(db.Text)
    rating = db.Column(db.Float)
    recommendation = db.Column(db.Text)
    category = db.Column(db.String(50))
    platform = db.Column(db.String(50))
    read_date = db.Column(db.String(20))
    book_id = db.Column(db.String(50))
    featured = db.Column(db.Boolean, default=False)
    word_count = db.Column(db.String(50))
    chapter_count = db.Column(db.String(50))
    status = db.Column(db.String(20))
    read_count = db.Column(db.String(50))
    want_to_read = db.Column(db.Boolean, default=False)
    progress = db.Column(db.Integer, default=0)
    rating_history = db.Column(db.Text, default='')  # 评分历史 JSON
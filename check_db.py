from app import app
from models import Novel

with app.app_context():
    # 查看已读推荐列表
    read_books = Novel.query.filter_by(want_to_read=False).all()
    print("=== 已读推荐列表 ===")
    for n in read_books:
        print(f'ID:{n.id} 书名:{n.title}')

    print("\n=== 想看列表 ===")
    want_books = Novel.query.filter_by(want_to_read=True).all()
    for n in want_books:
        print(f'ID:{n.id} 书名:{n.title}')
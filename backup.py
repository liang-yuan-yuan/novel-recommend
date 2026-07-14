# backup.py
import os
import shutil
import datetime

BACKUP_DIR = 'backups/'


def do_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    db_path = 'instance/novels.db'
    if os.path.exists(db_path):
        filename = f"novels_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy(db_path, os.path.join(BACKUP_DIR, filename))

        # 删除30天前的备份
        for f in os.listdir(BACKUP_DIR):
            file_path = os.path.join(BACKUP_DIR, f)
            if os.path.isfile(file_path):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if (datetime.datetime.now() - mtime).days > 30:
                    os.remove(file_path)

        print(f"✅ 备份成功: {filename}")
        return True
    else:
        print("❌ 数据库文件不存在")
        return False


if __name__ == '__main__':
    do_backup()
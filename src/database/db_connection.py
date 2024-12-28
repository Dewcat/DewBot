import sqlite3

class DatabaseConnection:
    def __init__(self, db_file):
        self.connection = None
        self.db_file = db_file

    def connect(self):
        """创建数据库连接"""
        try:
            self.connection = sqlite3.connect(self.db_file)
            print("成功连接到数据库")
        except sqlite3.Error as e:
            print(f"数据库连接错误: {e}")

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("数据库连接已关闭")
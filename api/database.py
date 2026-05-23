import sqlite3

class Database:
    def __init__(self, db_name="bot_data.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # ইউজার টেবিল
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users 
            (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, balance REAL DEFAULT 0, referrals INTEGER DEFAULT 0)''')
        # টাস্ক টেবিল
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, link TEXT, reward REAL)''')
        # উইথড্র টেবিল
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS withdrawals 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, method TEXT, phone TEXT, status TEXT)''')
        # কমপ্লিটেড টাস্ক ট্র্যাকিং
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS completed_tasks 
            (user_id INTEGER, task_id INTEGER)''')
        self.conn.commit()

    def register_user(self, user_id, name, username, ref_id):
        self.cursor.execute("INSERT OR IGNORE INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_balance(self, user_id):
        self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        res = self.cursor.fetchone()
        return res[0] if res else 0.0

    def add_balance(self, user_id, amount):
        self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        self.conn.commit()

    def deduct_balance(self, user_id, amount):
        self.cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        self.conn.commit()

    def get_active_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        return [{"id": r[0], "title": r[1], "description": r[2], "link": r[3], "reward": r[4]} for r in self.cursor.fetchall()]

    def get_task(self, task_id):
        self.cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        res = self.cursor.fetchone()
        return {"id": res[0], "title": res[1], "description": res[2], "link": res[3], "reward": res[4]} if res else None

    def complete_task(self, user_id, task_id):
        self.cursor.execute("INSERT INTO completed_tasks (user_id, task_id) VALUES (?, ?)", (user_id, task_id))
        self.conn.commit()

    def is_task_completed(self, user_id, task_id):
        self.cursor.execute("SELECT * FROM completed_tasks WHERE user_id = ? AND task_id = ?", (user_id, task_id))
        return self.cursor.fetchone() is not None

    def create_withdrawal(self, user_id, amount, method, phone):
        self.cursor.execute("INSERT INTO withdrawals (user_id, amount, method, phone, status) VALUES (?, ?, ?, ?, 'pending')", (user_id, amount, method, phone))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_users(self):
        self.cursor.execute("SELECT user_id, name, balance FROM users")
        return [{"user_id": r[0], "name": r[1], "balance": r[2]} for r in self.cursor.fetchall()]

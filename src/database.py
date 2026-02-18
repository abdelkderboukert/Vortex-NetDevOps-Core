import sqlite3
import threading

class NetworkDB:
    def __init__(self, db_path="network_inventory.db"):
        self.db_path = db_path
        self.lock = threading.Lock() # Prevents database corruption
        self._init_db()

    def _init_db(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS Devices 
                (id INTEGER PRIMARY KEY, name TEXT, ip TEXT, mac TEXT, 
                 kind TEXT, status TEXT, last_ping TIMESTAMP)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS Topology 
                (parent_id INTEGER, child_id INTEGER)''')

    def get_device(self, device_id):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute("SELECT * FROM Devices WHERE id = ?", (device_id,)).fetchone()

    def get_children(self, parent_id):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT child_id FROM Topology WHERE parent_id = ?", (parent_id,))
            return [row[0] for row in cursor.fetchall()]

    def update_status(self, device_id, status):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE Devices SET status = ?, last_ping = datetime('now') WHERE id = ?", (status, device_id))
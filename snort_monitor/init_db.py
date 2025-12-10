import sqlite3

conn = sqlite3.connect('alerts.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    classification TEXT,
    priority INTEGER,
    protocol TEXT,
    src_ip TEXT,
    src_port TEXT,
    dest_ip TEXT,
    dest_port TEXT,
    message TEXT
)
''')

conn.commit()
conn.close()
print("✅ Database initialized: alerts.db created with table 'alerts'")

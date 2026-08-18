import sqlite3

def init_db():

    conn = sqlite3.connect('abc.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS txn_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            step INTEGER,
            type TEXT,
            amount REAL,
            oldbalanceOrg REAL,
            newbalanceOrig REAL,
            oldbalanceDest REAL,
            newbalanceDest REAL,
            fraud_probability REAL,
            prediction TEXT,
            risk_level TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Database 'abc.db' initialized successfully.")

if __name__ == "__main__":
    init_db()

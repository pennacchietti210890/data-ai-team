import sqlite3
import random
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a new SQLite database in memory
#conn = sqlite3.connect(":memory:")
conn = sqlite3.connect("mock_fin_app.sqlite")
cursor = conn.cursor()

# 1. USERS table
cursor.execute("""
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    age INTEGER,
    gender TEXT,
    country TEXT,
    registration_date DATE
)
""")

# 2. WALLETS table
cursor.execute("""
CREATE TABLE wallets (
    wallet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    currency TEXT,
    balance REAL,
    balance_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

# 3. TRANSACTIONS table
cursor.execute("""
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    transaction_type TEXT, -- top-up, purchase, p2p_transfer, bank_transfer
    amount REAL,
    currency TEXT,
    timestamp DATETIME,
    counterparty_user_id INTEGER, -- nullable for purchases/bank transfers
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (counterparty_user_id) REFERENCES users(user_id)
)
""")

# 4. PNL table
cursor.execute("""
CREATE TABLE pnl (
    pnl_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,
    revenue REAL,
    cost REAL,
    profit REAL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
)
""")

conn.commit()
logger.info("Tables created!")

# ---------------------------------------------------------
# Now let's populate some **mock data** for realism

# Insert mock users
users = [
    ("Alice Smith", "alice@example.com", 28, "F", "US", "2022-01-15"),
    ("Bob Johnson", "bob@example.com", 35, "M", "UK", "2021-06-30"),
    ("Charlie Lee", "charlie@example.com", 42, "M", "CA", "2020-11-20"),
    ("Diana Prince", "diana@example.com", 30, "F", "AU", "2023-03-01"),
    ("Eva Mendes", "eva@example.com", 25, "F", "ES", "2023-07-10")
]

cursor.executemany(
    "INSERT INTO users (name, email, age, gender, country, registration_date) VALUES (?, ?, ?, ?, ?, ?)",
    users
)
conn.commit()

# Insert mock wallets (balances)
currencies = ["USD", "EUR", "GBP"]

today = datetime.date.today().isoformat()
for user_id in range(1, 6):  # 5 users
    for currency in currencies:
        balance = round(random.uniform(100, 5000), 2)
        cursor.execute(
            "INSERT INTO wallets (user_id, currency, balance, balance_date) VALUES (?, ?, ?, ?)",
            (user_id, currency, balance, today)
        )
conn.commit()

# Insert mock transactions
transaction_types = ["top_up", "purchase", "p2p_transfer", "bank_transfer"]

for _ in range(50):  # 50 transactions
    user_id = random.randint(1, 5)
    t_type = random.choice(transaction_types)
    amount = round(random.uniform(5, 500), 2)
    currency = random.choice(currencies)
    timestamp = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365))

    if t_type == "p2p_transfer":
        counterparty_user_id = random.choice([uid for uid in range(1, 6) if uid != user_id])
        description = f"P2P transfer to user {counterparty_user_id}"
    else:
        counterparty_user_id = None
        description = f"{t_type.replace('_', ' ').title()}"

    cursor.execute(
        "INSERT INTO transactions (user_id, transaction_type, amount, currency, timestamp, counterparty_user_id, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, t_type, amount, currency, timestamp, counterparty_user_id, description)
    )
conn.commit()

# Insert mock PNL entries
cursor.execute("SELECT transaction_id FROM transactions")
transaction_ids = [row[0] for row in cursor.fetchall()]

for t_id in transaction_ids:
    revenue = round(random.uniform(0.5, 5.0), 2)
    cost = round(random.uniform(0.1, revenue), 2)
    profit = round(revenue - cost, 2)
    cursor.execute(
        "INSERT INTO pnl (transaction_id, revenue, cost, profit) VALUES (?, ?, ?, ?)",
        (t_id, revenue, cost, profit)
    )
conn.commit()

logger.info("Mock data inserted successfully!")
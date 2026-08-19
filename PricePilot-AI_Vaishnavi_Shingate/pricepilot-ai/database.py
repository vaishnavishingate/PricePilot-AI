import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DB_PATH = "pricepilot.db"
COMBINED_CSV_PATH = "C:\\Users\\HP\\.gemini\\antigravity\\scratch\\olist_combined_dataset.csv"
DATA_DIR = "data"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)
    
    # Create Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        product_category_name TEXT NOT NULL,
        product_weight_g INTEGER,
        product_length_cm INTEGER,
        product_height_cm INTEGER,
        product_width_cm INTEGER,
        cost REAL NOT NULL,
        base_price REAL NOT NULL
    )
    """)
    
    # Create Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        order_status TEXT NOT NULL,
        order_purchase_timestamp TEXT NOT NULL
    )
    """)
    
    # Create Order Items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        order_id TEXT NOT NULL,
        order_item_id INTEGER NOT NULL,
        product_id TEXT NOT NULL,
        seller_id TEXT NOT NULL,
        shipping_limit_date TEXT NOT NULL,
        price REAL NOT NULL,
        freight_value REAL NOT NULL,
        PRIMARY KEY (order_id, order_item_id),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)
    
    # Create Competitor Prices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitor_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT NOT NULL,
        competitor_name TEXT NOT NULL,
        price REAL NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)
    
    conn.commit()
    
    # Check if seed is needed
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)
        
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    
    # Seed default users (password: admin123, manager123, analyst123, exec123)
    import hashlib
    def hash_password(password: str) -> str:
        salt = b"pricepilot_salt_12893"
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return pwdhash.hex()
        
    cursor.executemany("""
    INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)
    """, [
        ("admin", hash_password("admin123"), "Admin"),
        ("manager", hash_password("manager123"), "Pricing Manager"),
        ("analyst", hash_password("analyst123"), "Business Analyst"),
        ("executive", hash_password("exec123"), "Executive")
    ])
    conn.commit()
    
    # Check if combined Olist CSV is available
    if not os.path.exists(COMBINED_CSV_PATH):
        print(f"Error: Combined dataset not found at {COMBINED_CSV_PATH}")
        return
        
    print(f"Reading combined dataset from {COMBINED_CSV_PATH}...")
    df = pd.read_csv(COMBINED_CSV_PATH)
    
    # Fill missing values to avoid SQLite errors
    df['product_category_name'] = df['product_category_name'].fillna('outros')
    df['product_weight_g'] = df['product_weight_g'].fillna(500).astype(int)
    df['product_length_cm'] = df['product_length_cm'].fillna(20).astype(int)
    df['product_height_cm'] = df['product_height_cm'].fillna(15).astype(int)
    df['product_width_cm'] = df['product_width_cm'].fillna(15).astype(int)
    df['order_status'] = df['order_status'].fillna('delivered')
    df['order_purchase_timestamp'] = df['order_purchase_timestamp'].fillna(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    df['freight_value'] = df['freight_value'].fillna(15.0)
    df['shipping_limit_date'] = df['shipping_limit_date'].fillna(df['order_purchase_timestamp'])
    
    print("Extracting unique products...")
    # Group by product_id to compute its average price and physical metrics
    prod_grouped = df.groupby('product_id').agg(
        product_category_name=('product_category_name', 'first'),
        product_weight_g=('product_weight_g', 'first'),
        product_length_cm=('product_length_cm', 'first'),
        product_height_cm=('product_height_cm', 'first'),
        product_width_cm=('product_width_cm', 'first'),
        base_price=('price', 'mean')
    ).reset_index()
    
    # Simulated Cost at 60% of base price
    prod_grouped['cost'] = (prod_grouped['base_price'] * 0.60).round(2)
    prod_grouped['base_price'] = prod_grouped['base_price'].round(2)
    
    # Bulk insert products
    print(f"Inserting {len(prod_grouped)} products...")
    products_list = prod_grouped[[
        'product_id', 'product_category_name', 'product_weight_g', 
        'product_length_cm', 'product_height_cm', 'product_width_cm', 
        'cost', 'base_price'
    ]].values.tolist()
    
    cursor.executemany("""
    INSERT OR REPLACE INTO products (product_id, product_category_name, product_weight_g, product_length_cm, product_height_cm, product_width_cm, cost, base_price)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, products_list)
    conn.commit()
    
    # Extract unique orders
    print("Extracting unique orders...")
    orders_df = df[['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp']].drop_duplicates('order_id')
    print(f"Inserting {len(orders_df)} orders...")
    orders_list = orders_df.values.tolist()
    
    cursor.executemany("""
    INSERT OR REPLACE INTO orders (order_id, customer_id, order_status, order_purchase_timestamp)
    VALUES (?, ?, ?, ?)
    """, orders_list)
    conn.commit()
    
    # Extract order items
    print("Extracting order items...")
    items_df = df[['order_id', 'order_item_id', 'product_id', 'seller_id', 'shipping_limit_date', 'price', 'freight_value']]
    print(f"Inserting {len(items_df)} order items...")
    items_list = items_df.values.tolist()
    
    cursor.executemany("""
    INSERT OR REPLACE INTO order_items (order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, items_list)
    conn.commit()
    
    # Generate competitor pricing benchmarks
    print("Simulating competitor prices...")
    competitor_prices_list = []
    
    # Select top 50 products by order frequency to populate competitor timeline charts neatly
    top_products = df['product_id'].value_counts().head(50).index.tolist()
    
    # For others, we generate a single benchmark price
    all_products = prod_grouped['product_id'].tolist()
    
    np.random.seed(42)
    
    # Create competitor records for top products
    for p_id in top_products:
        base_p = prod_grouped.loc[prod_grouped['product_id'] == p_id, 'base_price'].values[0]
        # Generate 15 price checks over time
        for i in range(15):
            date_check = (datetime.now() - timedelta(days=i*4)).strftime("%Y-%m-%d %H:%M:%S")
            comp_a = round(base_p * np.random.uniform(0.92, 1.05), 2)
            comp_b = round(base_p * np.random.uniform(0.95, 1.08), 2)
            competitor_prices_list.append((p_id, "CompStore_A", comp_a, date_check))
            competitor_prices_list.append((p_id, "CompStore_B", comp_b, date_check))
            
    # For remaining products, generate 1 benchmark
    for p_id in all_products:
        if p_id not in top_products:
            base_p = prod_grouped.loc[prod_grouped['product_id'] == p_id, 'base_price'].values[0]
            comp_a = round(base_p * np.random.uniform(0.94, 1.06), 2)
            competitor_prices_list.append((p_id, "CompStore_A", comp_a, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
    print(f"Inserting {len(competitor_prices_list)} competitor records...")
    cursor.executemany("""
    INSERT INTO competitor_prices (product_id, competitor_name, price, timestamp)
    VALUES (?, ?, ?, ?)
    """, competitor_prices_list)
    conn.commit()
    
    print("Database initialization with combined Olist dataset complete!")

if __name__ == "__main__":
    init_db()

import pandas as pd
import numpy as np
import datetime
import os
import random
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, DBProduct, DBSalesRecord, DBCompetitorPrice, DBUser, init_db, get_db
from backend.app.auth import get_password_hash

def seed_database():
    print("Initializing Database Schema...")
    init_db()
    
    db = SessionLocal()
    try:
        # Check if users already exist, if not seed default users
        if db.query(DBUser).count() == 0:
            print("Seeding default users...")
            users = [
                DBUser(username="admin", hashed_password=get_password_hash("admin123"), role="admin"),
                DBUser(username="manager", hashed_password=get_password_hash("manager123"), role="manager"),
                DBUser(username="analyst", hashed_password=get_password_hash("analyst123"), role="analyst")
            ]
            db.add_all(users)
            db.commit()
            print("Default users seeded: admin/admin123, manager/manager123, analyst/analyst123")
            
        # Check if products already exist
        if db.query(DBProduct).count() > 0:
            print("Database already contains product data. Skipping CSV import.")
            return

        # Path setup for Olist CSV
        dataset_path = "olist_combined_dataset.csv"
        if not os.path.exists(dataset_path):
            dataset_path = "../olist_combined_dataset.csv"
        if not os.path.exists(dataset_path):
            dataset_path = "Dataa/olist_combined_dataset.csv"
        if not os.path.exists(dataset_path):
            dataset_path = "../Dataa/olist_combined_dataset.csv"
            
        if not os.path.exists(dataset_path):
            print(f"Error: Could not find olist_combined_dataset.csv to seed data.")
            return
            
        print(f"Reading dataset from {dataset_path} for seeding...")
        df = pd.read_csv(dataset_path)
        
        # Clean null values
        df["price"] = df["price"].fillna(df["price"].mean())
        df["freight_value"] = df["freight_value"].fillna(df["freight_value"].mean())
        df["product_weight_g"] = df["product_weight_g"].fillna(df["product_weight_g"].mean())
        df["product_length_cm"] = df["product_length_cm"].fillna(df["product_length_cm"].mean())
        df["product_height_cm"] = df["product_height_cm"].fillna(df["product_height_cm"].mean())
        df["product_width_cm"] = df["product_width_cm"].fillna(df["product_width_cm"].mean())
        df["product_category_name"] = df["product_category_name"].fillna("misc")
        
        # Identify top selling products so we have rich sales history
        product_sales_counts = df["product_id"].value_counts()
        top_products = product_sales_counts.head(150).index.tolist()
        
        print(f"Importing {len(top_products)} top selling products...")
        
        # Parse dates
        df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
        df["order_date"] = df["order_purchase_timestamp"].dt.date
        
        # Process each top product
        for idx, prod_id in enumerate(top_products):
            prod_df = df[df["product_id"] == prod_id]
            first_row = prod_df.iloc[0]
            
            # Median price is the base price
            base_price = float(prod_df["price"].median())
            
            # Calculate volume
            volume = float(first_row["product_length_cm"] * first_row["product_width_cm"] * first_row["product_height_cm"])
            
            # Create DB product
            db_product = DBProduct(
                id=str(prod_id),
                category=str(first_row["product_category_name"]),
                weight_g=float(first_row["product_weight_g"]),
                length_cm=float(first_row["product_length_cm"]),
                height_cm=float(first_row["product_height_cm"]),
                width_cm=float(first_row["product_width_cm"]),
                freight_value=float(first_row["freight_value"]),
                base_price=base_price,
                recommended_price=round(base_price * random.uniform(0.95, 1.08), 2)
            )
            db.add(db_product)
            
            # Create sales history: group sales by date
            sales_by_date = prod_df.groupby("order_date").agg(
                units_sold=("order_id", "count"),
                revenue=("price", "sum"),
                avg_price=("price", "mean")
            ).reset_index()
            
            for _, sale_row in sales_by_date.iterrows():
                db_sale = DBSalesRecord(
                    product_id=str(prod_id),
                    price=float(sale_row["avg_price"]),
                    units_sold=int(sale_row["units_sold"]),
                    date=sale_row["order_date"],
                    revenue=float(sale_row["revenue"])
                )
                db.add(db_sale)
                
            # Create Competitors: Competitor A, B, C with randomized but realistic prices
            competitors = ["Alpha Pricing", "Beta Marketplace", "Delta Retail"]
            for comp_name in competitors:
                # Competitor price varies between -8% and +8% of base price
                comp_price = round(base_price * random.uniform(0.92, 1.08), 2)
                db_comp = DBCompetitorPrice(
                    product_id=str(prod_id),
                    competitor_name=comp_name,
                    price=comp_price,
                    last_updated=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 10))
                )
                db.add(db_comp)
                
            if (idx + 1) % 30 == 0:
                db.commit()
                print(f"Processed {idx + 1}/{len(top_products)} products...")
                
        db.commit()
        print("Database seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

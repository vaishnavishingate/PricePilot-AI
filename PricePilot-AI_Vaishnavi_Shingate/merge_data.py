import pandas as pd
import os

print("Step 1: Reading the 3 CSV files...")
# Load the datasets
orders = pd.read_csv('olist_orders_dataset.csv')
order_items = pd.read_csv('olist_order_items_dataset.csv')
products = pd.read_csv('olist_products_dataset.csv')

print("Step 2: Linking order items with general order information...")
# Connects items to orders using 'order_id'
merged_df = pd.merge(order_items, orders, on='order_id', how='left')

print("Step 3: Linking product details to the items...")
# Connects the resulting data to the products table using 'product_id'
final_df = pd.merge(merged_df, products, on='product_id', how='left')

print("Step 4: Exporting everything into one master CSV...")
output_filename = 'olist_combined_dataset.csv'
final_df.to_csv(output_filename, index=False)

print("\nSuccess! The files have been 100% successfully merged.")
print(f"New file created: {os.path.abspath(output_filename)}")
print(f"Dataset Dimensions: {final_df.shape[0]} rows and {final_df.shape[1]} columns.")
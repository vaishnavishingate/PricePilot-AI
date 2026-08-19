import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

def train_models():
    print("Starting model training pipeline...")
    
    # Path setup
    dataset_path = "olist_combined_dataset.csv"
    if not os.path.exists(dataset_path):
        dataset_path = "../olist_combined_dataset.csv"
    if not os.path.exists(dataset_path):
        dataset_path = "Dataa/olist_combined_dataset.csv"
    if not os.path.exists(dataset_path):
        dataset_path = "../Dataa/olist_combined_dataset.csv"
        
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Could not find olist_combined_dataset.csv in typical locations. Current dir: {os.getcwd()}")
        
    print(f"Reading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    print(f"Dataset shape: {df.shape}")
    
    # 1. Clean missing values
    df["price"] = df["price"].fillna(df["price"].mean())
    df["freight_value"] = df["freight_value"].fillna(df["freight_value"].mean())
    df["product_weight_g"] = df["product_weight_g"].fillna(df["product_weight_g"].mean())
    df["product_length_cm"] = df["product_length_cm"].fillna(df["product_length_cm"].mean())
    df["product_height_cm"] = df["product_height_cm"].fillna(df["product_height_cm"].mean())
    df["product_width_cm"] = df["product_width_cm"].fillna(df["product_width_cm"].mean())
    df["product_category_name"] = df["product_category_name"].fillna("misc")
    
    df["product_name_lenght"] = df["product_name_lenght"].fillna(df["product_name_lenght"].mean())
    df["product_description_lenght"] = df["product_description_lenght"].fillna(df["product_description_lenght"].mean())
    df["product_photos_qty"] = df["product_photos_qty"].fillna(df["product_photos_qty"].mean())
    
    # Feature Engineering
    df["product_volume"] = df["product_length_cm"] * df["product_width_cm"] * df["product_height_cm"]
    df["product_weight_g"] = df["product_weight_g"].replace(0, np.nan).fillna(df["product_weight_g"].mean())
    
    # Corrected (leakage-free) feature: freight per weight
    df["freight_per_weight"] = df["freight_value"] / df["product_weight_g"]
    df["freight_per_weight"] = df["freight_per_weight"].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Label encode category
    le_category = LabelEncoder()
    df["product_category_encoded"] = le_category.fit_transform(df["product_category_name"].astype(str))
    
    # Save encoders & categories
    os.makedirs("models", exist_ok=True)
    joblib.dump(le_category, "models/category_encoder.joblib")
    
    # Unique categories mapping for frontend selection
    categories_list = sorted(df["product_category_name"].unique().tolist())
    joblib.dump(categories_list, "models/categories_list.joblib")
    
    # ==========================================
    # MODEL 1: PRICE RECOMMENDATION ENGINE
    # ==========================================
    print("Training Model 1: Price Recommendation Engine...")
    price_features = [
        "product_category_encoded",
        "product_weight_g",
        "product_volume",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "freight_value",
        "freight_per_weight"
    ]
    
    X_price = df[price_features]
    y_price = df["price"]
    
    X_p_train, X_p_test, y_p_train, y_p_test = train_test_split(X_price, y_price, test_size=0.2, random_state=42)
    
    # Fit Model
    try:
        print("Using XGBoost Regressor for Price model...")
        price_model = xgb.XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
        price_model.fit(X_p_train, y_p_train)
    except Exception as e:
        print(f"XGBoost failed or not installed: {e}. Falling back to RandomForestRegressor...")
        price_model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
        price_model.fit(X_p_train, y_p_train)
        
    p_preds = price_model.predict(X_p_test)
    p_mse = mean_squared_error(y_p_test, p_preds)
    p_rmse = np.sqrt(p_mse)
    p_r2 = r2_score(y_p_test, p_preds)
    
    print(f"Price Model Results: RMSE={p_rmse:.2f}, R2={p_r2:.4f}")
    joblib.dump(price_model, "models/price_model.joblib")
    
    # ==========================================
    # MODEL 2: DEMAND FORECASTING ENGINE
    # ==========================================
    print("Training Model 2: Demand Forecasting Engine...")
    
    # Parse timestamp
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["year"] = df["order_purchase_timestamp"].dt.year
    df["month"] = df["order_purchase_timestamp"].dt.month
    df["year_month"] = df["order_purchase_timestamp"].dt.to_period("M")
    
    # Aggregate demand: group by product_id and month
    # Calculate monthly sales volume (units sold) and average price per month for each product
    demand_df = df.groupby(["product_id", "year_month", "product_category_encoded", "product_weight_g", "product_volume", "freight_value", "month"]).agg(
        units_sold=("order_id", "count"),
        avg_price=("price", "mean")
    ).reset_index()
    
    print(f"Aggregated demand dataset shape: {demand_df.shape}")
    
    demand_features = [
        "product_category_encoded",
        "product_weight_g",
        "product_volume",
        "freight_value",
        "month",
        "avg_price"
    ]
    
    X_demand = demand_df[demand_features]
    y_demand = demand_df["units_sold"]
    
    X_d_train, X_d_test, y_d_train, y_d_test = train_test_split(X_demand, y_demand, test_size=0.2, random_state=42)
    
    try:
        print("Using XGBoost Regressor for Demand model...")
        demand_model = xgb.XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
        demand_model.fit(X_d_train, y_d_train)
    except Exception as e:
        print(f"XGBoost failed or not installed: {e}. Falling back to RandomForestRegressor...")
        demand_model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
        demand_model.fit(X_d_train, y_d_train)
        
    d_preds = demand_model.predict(X_d_test)
    d_mse = mean_squared_error(y_d_test, d_preds)
    d_rmse = np.sqrt(d_mse)
    d_r2 = r2_score(y_d_test, d_preds)
    
    print(f"Demand Model Results: RMSE={d_rmse:.2f}, R2={d_r2:.4f}")
    joblib.dump(demand_model, "models/demand_model.joblib")
    print("Both models trained and saved successfully in models/ folder!")

if __name__ == "__main__":
    train_models()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
import joblib

# Step 1: Load dataset
df = pd.read_csv("olist_combined_dataset.csv")

# Step 2: Explore dataset
print(df.head())
print(df.shape)
print(df.columns)
print(df.isnull().sum())

# Step 3: Clean numeric missing values
df["price"] = df["price"].fillna(df["price"].mean())
df["product_weight_g"] = df["product_weight_g"].fillna(df["product_weight_g"].mean())
df["product_length_cm"] = df["product_length_cm"].fillna(df["product_length_cm"].mean())
df["product_height_cm"] = df["product_height_cm"].fillna(df["product_height_cm"].mean())
df["product_width_cm"] = df["product_width_cm"].fillna(df["product_width_cm"].mean())
df["product_name_lenght"] = df["product_name_lenght"].fillna(df["product_name_lenght"].mean())
df["product_description_lenght"] = df["product_description_lenght"].fillna(df["product_description_lenght"].mean())
df["product_photos_qty"] = df["product_photos_qty"].fillna(df["product_photos_qty"].mean())

# Step 4: Clean categorical missing values
df["product_category_name"] = df["product_category_name"].fillna(df["product_category_name"].mode()[0])

# Step 5: Drop irrelevant date columns
df = df.drop(columns=[
    "order_delivered_customer_date",
    "order_delivered_carrier_date",
    "order_approved_at",
    "shipping_limit_date",
    "order_purchase_timestamp",
    "order_estimated_delivery_date"
])

# Step 6: Drop ID columns
df = df.drop(columns=["order_id", "order_item_id", "product_id", "seller_id", "customer_id"])
print("Columns before encoding:", df.columns)

# Step 7: Encode categorical columns
categorical_cols = [col for col in ["product_category_name", "order_status"] if col in df.columns]
df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# Step 8: Define features and target
X = df.drop("price", axis=1)
y = df["price"]
print("Remaining NaNs:", df.isnull().sum().sum())

# Step 9: Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 10: Train LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)

# Step 11: Evaluate LinearRegression
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print("LinearRegression MSE:", mse)
print("LinearRegression RMSE:", rmse)

# Scatter plot: Actual vs Predicted
plt.scatter(y_test, y_pred, alpha=0.5)
plt.xlabel("Actual Price")
plt.ylabel("Predicted Price")
plt.title("Actual vs Predicted Prices")
plt.show()

# Error distribution
errors = y_test - y_pred
plt.hist(errors, bins=50)
plt.xlabel("Prediction Error")
plt.ylabel("Count")
plt.title("Error Distribution")
plt.show()

# Step 12: Train RandomForest
rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(X_train, y_train)

# Step 13: Evaluate RandomForest
rf_pred = rf_model.predict(X_test)
rf_mse = mean_squared_error(y_test, rf_pred)
rf_rmse = np.sqrt(rf_mse)
print("RandomForest MSE:", rf_mse)
print("RandomForest RMSE:", rf_rmse)

# Feature importance plot
importances = rf_model.feature_importances_
features = X.columns
indices = importances.argsort()[::-1]

plt.figure(figsize=(10, 6))
plt.bar(range(len(importances)), importances[indices], align="center")
plt.xticks(range(len(importances)), [features[i] for i in indices], rotation=90)
plt.xlabel("Features")
plt.ylabel("Importance Score")
plt.title("Feature Importance (RandomForest)")
plt.tight_layout()
# Scatter plot: Actual vs Predicted
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')  # ideal line
plt.xlabel("Actual Price")
plt.ylabel("Predicted Price")
plt.title("Actual vs Predicted Prices")
plt.show()

# Step 14: Save the better model (RandomForest usually performs better)
joblib.dump(rf_model, "price_model.pkl")

input("Press Enter to exit...")

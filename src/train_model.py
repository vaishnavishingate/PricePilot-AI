import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor

# 1. Load dataset
df = pd.read_csv("Dataa/olist_combined_dataset.csv")

# 2. Clean dataset
df["price"] = df["price"].fillna(df["price"].mean())
df["product_weight_g"] = df["product_weight_g"].fillna(df["product_weight_g"].mean())
df["product_length_cm"] = df["product_length_cm"].fillna(df["product_length_cm"].mean())
df["product_height_cm"] = df["product_height_cm"].fillna(df["product_height_cm"].mean())
df["product_width_cm"] = df["product_width_cm"].fillna(df["product_width_cm"].mean())

df["product_category_name"] = df["product_category_name"].fillna(df["product_category_name"].mode()[0])
df["order_status"] = df["order_status"].fillna(df["order_status"].mode()[0])

df = df.drop(columns=[
    "order_id", "order_item_id", "product_id", "seller_id", "customer_id",
    "shipping_limit_date", "order_purchase_timestamp", "order_approved_at",
    "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"
])

df = pd.get_dummies(df, columns=["product_category_name", "order_status"], drop_first=True)

# 3. Feature Engineering (safe handling)
df["product_volume"] = df["product_length_cm"] * df["product_width_cm"] * df["product_height_cm"]

# Replace zero weights with NaN then fill
df["product_weight_g"] = df["product_weight_g"].replace(0, np.nan)
df["product_weight_g"] = df["product_weight_g"].fillna(df["product_weight_g"].mean())

# Safe division for price_per_weight (no inplace warning)
df["price_per_weight"] = df["price"] / df["product_weight_g"]
df["price_per_weight"] = df["price_per_weight"].replace([np.inf, -np.inf], np.nan)
df["price_per_weight"] = df["price_per_weight"].fillna(df["price_per_weight"].mean())

# 4. Split features and target
X = df.drop(columns=["price"])
y = df["price"]

# Impute missing values
imputer = SimpleImputer(strategy="mean")
X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Hyperparameter tuning with XGBoost
params = {
    "n_estimators": [800],        # enough trees for stability
    "max_depth": [7, 10],         # balanced depth
    "learning_rate": [0.05],      # small learning rate for accuracy
    "subsample": [0.8],           # random sampling for robustness
    "colsample_bytree": [0.8]     # feature sampling
}


grid = GridSearchCV(
    XGBRegressor(random_state=42, n_jobs=-1),
    params,
    cv=3,
    scoring="r2",
    n_jobs=-1
)
grid.fit(X_train, y_train)
best_model = grid.best_estimator_

# 6. Evaluate tuned XGBoost
preds = best_model.predict(X_test)
mse = mean_squared_error(y_test, preds)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, preds)

print(f"Tuned XGBoost: MSE={mse:.2f}, RMSE={rmse:.2f}, R2={r2:.4f}")

# 7. Save tuned model
joblib.dump(best_model, "models/price_model.pkl")
print("✅ Tuned XGBoost model saved as price_model.pkl")

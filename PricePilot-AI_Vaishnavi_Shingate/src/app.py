from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os   # <-- yeh import missing tha, ab add kar diya

# Safe path handling: model file ek level upar hai (D:\ai project\price_model.pkl)
model = joblib.load("price_model.pkl")

app = FastAPI()

# Input schema
class ProductFeatures(BaseModel):
    product_weight_g: float
    product_length_cm: float
    product_height_cm: float
    product_width_cm: float
    freight_value: float

@app.get("/")
def home():
    return {"message": "Price Prediction API is running!"}

@app.post("/predict")
def predict(features: ProductFeatures):
    try:
        df = pd.DataFrame([features.dict()])

        # Feature engineering
        df["product_volume"] = (
            df["product_length_cm"] * df["product_width_cm"] * df["product_height_cm"]
        )
        df["product_weight_g"] = df["product_weight_g"].replace(0, np.nan)
        df["product_weight_g"] = df["product_weight_g"].fillna(df["product_weight_g"].mean())
        df["price_per_weight"] = df["freight_value"] / df["product_weight_g"]
        df["price_per_weight"] = df["price_per_weight"].replace([np.inf, -np.inf], np.nan)
        df["price_per_weight"] = df["price_per_weight"].fillna(df["price_per_weight"].mean())

        prediction = model.predict(df)
        return {"predicted_price": float(prediction[0])}
    except Exception as e:
        return {"error": str(e)}

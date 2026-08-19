import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import os

DB_PATH = "pricepilot.db"

class PricePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False
        
    def train(self, product_id: str):
        """
        Train a model on historical pricing, competitor pricing, and sales demand.
        """
        conn = sqlite3.connect(DB_PATH)
        
        # Query joined data: orders, order_items, competitor prices, and products
        query = f"""
        SELECT 
            oi.price as our_price,
            oi.freight_value,
            p.cost,
            p.product_weight_g,
            o.order_purchase_timestamp,
            (SELECT AVG(cp.price) FROM competitor_prices cp 
             WHERE cp.product_id = oi.product_id 
             AND date(cp.timestamp) <= date(o.order_purchase_timestamp)) as competitor_price
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.product_id = ?
        """
        df = pd.read_sql_query(query, conn, params=(product_id,))
        conn.close()
        
        if len(df) < 10:
            # Fallback if insufficient data
            self.is_trained = False
            return False
            
        # fill missing competitor prices with our base price
        df['competitor_price'] = df['competitor_price'].fillna(df['our_price'])
        
        # Parse datetime features
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        df['date'] = df['order_purchase_timestamp'].dt.date
        
        # Aggregate to daily sales quantity and average prices
        daily = df.groupby('date').agg(
            units_sold=('our_price', 'count'),
            avg_price=('our_price', 'mean'),
            avg_competitor_price=('competitor_price', 'mean'),
            cost=('cost', 'first'),
            freight=('freight_value', 'mean'),
            weight=('product_weight_g', 'first')
        ).reset_index()
        
        daily['day_of_week'] = pd.to_datetime(daily['date']).dt.dayofweek
        daily['month'] = pd.to_datetime(daily['date']).dt.month
        
        # Features & Target
        X = daily[['avg_price', 'avg_competitor_price', 'day_of_week', 'month', 'freight', 'weight']]
        y = daily['units_sold']
        
        self.model.fit(X, y)
        self.is_trained = True
        self.cost = daily['cost'].iloc[0]
        self.base_price = daily['avg_price'].mean()
        self.weight = daily['weight'].iloc[0]
        self.freight = daily['freight'].mean()
        return True

    def predict_demand(self, price: float, competitor_price: float, day_of_week: int, month: int) -> float:
        """
        Predict units sold for a given price point.
        """
        if not self.is_trained:
            # Fallback demand estimation if model isn't trained
            elasticity = 1.5
            base_demand = 5.0
            price_ratio = price / competitor_price if competitor_price > 0 else 1.0
            return max(0.1, base_demand * (price_ratio ** -elasticity))
            
        features = pd.DataFrame([{
            'avg_price': price,
            'avg_competitor_price': competitor_price,
            'day_of_week': day_of_week,
            'month': month,
            'freight': self.freight,
            'weight': self.weight
        }])
        
        prediction = self.model.predict(features)[0]
        return float(max(0.0, prediction))

    def optimize_price(self, competitor_price: float, day_of_week: int, month: int) -> dict:
        """
        Run grid search over a range of possible prices to find the profit-maximizing price.
        """
        if not self.is_trained:
            # Fallback optimization if not trained
            cost = 30.0
            suggested = round(competitor_price * 0.98, 2)
            return {
                "optimal_price": suggested,
                "expected_demand": 3.5,
                "expected_revenue": round(suggested * 3.5, 2),
                "expected_profit": round((suggested - cost) * 3.5, 2),
                "margin_percent": round(((suggested - cost) / suggested) * 100, 2) if suggested > 0 else 0
            }
            
        # Generate 100 candidate prices from cost to 2x base price
        min_price = max(self.cost + 1.0, self.base_price * 0.5)
        max_price = self.base_price * 2.0
        candidate_prices = np.linspace(min_price, max_price, 100)
        
        best_price = min_price
        max_profit = -float('inf')
        best_demand = 0.0
        
        for price in candidate_prices:
            demand = self.predict_demand(price, competitor_price, day_of_week, month)
            profit = (price - self.cost) * demand
            
            if profit > max_profit:
                max_profit = profit
                best_price = price
                best_demand = demand
                
        opt_price = round(best_price, 2)
        expected_demand = round(best_demand, 1)
        expected_revenue = round(opt_price * expected_demand, 2)
        expected_profit = round(max_profit, 2)
        margin_percent = round(((opt_price - self.cost) / opt_price) * 100, 2)
        
        return {
            "optimal_price": opt_price,
            "expected_demand": expected_demand,
            "expected_revenue": expected_revenue,
            "expected_profit": expected_profit,
            "margin_percent": margin_percent,
            "cost": self.cost
        }
        
    def simulate_curve(self, competitor_price: float, day_of_week: int, month: int) -> dict:
        """
        Generates lists of prices, expected revenues, and expected profits for visualization.
        """
        if not self.is_trained:
            # Fallback curve data
            prices = [round(x, 2) for x in np.linspace(15, 80, 20)]
            revenues = []
            profits = []
            demands = []
            cost = 30.0
            for p in prices:
                dem = max(0.5, 10 - 0.1 * p)
                demands.append(round(dem, 1))
                revenues.append(round(p * dem, 2))
                profits.append(round((p - cost) * dem, 2))
            return {
                "prices": prices,
                "demands": demands,
                "revenues": revenues,
                "profits": profits,
                "cost": cost
            }
            
        min_price = max(self.cost * 0.8, 1.0)
        max_price = self.base_price * 2.0
        candidate_prices = np.linspace(min_price, max_price, 25)
        
        prices = []
        demands = []
        revenues = []
        profits = []
        
        for price in candidate_prices:
            price_val = round(price, 2)
            demand = self.predict_demand(price_val, competitor_price, day_of_week, month)
            revenue = price_val * demand
            profit = (price_val - self.cost) * demand
            
            prices.append(price_val)
            demands.append(round(demand, 1))
            revenues.append(round(revenue, 2))
            profits.append(round(profit, 2))
            
        return {
            "prices": prices,
            "demands": demands,
            "revenues": revenues,
            "profits": profits,
            "cost": self.cost
        }

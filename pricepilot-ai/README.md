# PricePilot AI: Dynamic Pricing Optimization & Revenue Intelligence System

PricePilot AI is an AI-powered revenue optimization and pricing analytics platform built specifically for e-commerce retailers. It integrates statistical and machine learning models to analyze consumer purchasing behavior, track competitor benchmarks, model pricing elasticity, and forecast future demand volume. 

The project is structured in direct alignment with the **8-Week Internship Roadmap** and uses the **Brazilian E-Commerce (Olist) dataset** schema as its data engine.

---

## 🚀 Key Features

*   **User Management & Security:** Secure session tokens simulating JWT headers with Role-Based Access Control (RBAC) supporting Admin, Pricing Manager, Business Analyst, and Executive roles.
*   **Olist Data Pipeline:** Automated database parser supporting raw CSV ingestion of `olist_products`, `olist_order_items`, and `olist_orders`.
*   **Pricing Optimization Engine:** Evaluates product demand elasticity curves using a **Random Forest Regressor** to find the optimal profit-maximizing price.
*   **Demand Forecasting Module:** Supports multiple horizons (7, 14, 30 days and 3, 6, 12 months) using a range of select models: XGBoost, Random Forest, ARIMA (Lag-based Ridge), LSTM, and Prophet cycle approximations.
*   **Competitor Tracking:** Visualizes pricing discrepancies and positions relative to market averages.
*   **Interactive Simulation:** Dynamic sliders to test hypothetical shifts in base costs and competitor adjustments.
*   **Mentor Presentation:** A built-in, animated HTML5 presentation slide deck explaining architecture, schemas, and AI models directly within the dashboard.

---

## 🛠️ Architecture & Technical Stack

*   **Backend Framework:** Python FastAPI (REST API Gateway)
*   **Machine Learning Core:** Scikit-Learn (Random Forest, Ridge), XGBoost
*   **Database:** Relational SQLite engine (zero configuration, high speed)
*   **Frontend UI:** Single Page Application (HTML5, Vanilla CSS3, Javascript, Chart.js via CDN)
*   **Styling Theme:** Glassmorphism Dark Mode with animations and CSS variables
*   **Containerization:** Docker & Docker-Compose

---

## 📂 Project Structure

```
pricepilot-ai/
├── main.py                    # FastAPI entry point & API Router
├── database.py                # Database connection, schemas, and Olist data seeder
├── auth.py                    # JWT-token handlers, password hashing, and role checks
├── requirements.txt           # Python dependency lists
├── Dockerfile                 # Configuration for container build
├── docker-compose.yml         # Container mapping configuration
├── README.md                  # Project documentation
├── models/
│   ├── __init__.py
│   ├── price_predictor.py     # Elasticity optimizer using Random Forest Regressor
│   └── demand_forecaster.py   # Multi-horizon demand forecasting model wrapper
└── static/
    ├── index.html             # Single-Page Application container grids
    ├── style.css              # Custom styling (glassmorphism variables, keyframes)
    ├── app.js                 # SPA navigation, fetch calls, Chart.js renderers
    └── presentation.html      # Project explanation slides
```

---

## ⚙️ How to Setup & Run

### Method 1: Local Execution (Recommended)

1.  **Clone / Copy the directory** to your local workspace:
    `C:\Users\HP\.gemini\antigravity\scratch\pricepilot-ai`

2.  **Open Terminal** in the directory:
    ```powershell
    cd C:\Users\HP\.gemini\antigravity\scratch\pricepilot-ai
    ```

3.  **Install dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```

4.  **Run the application**:
    ```powershell
    python main.py
    ```
    *Note: On first launch, the database will automatically generate a cleaned Olist dataset of over 20,000 transaction rows for sports, housewares, and tech products to train the models immediately.*

5.  **Open in Browser**:
    Go to [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Method 2: Docker Containerization

1.  **Build and run containers**:
    ```bash
    docker-compose up --build
    ```

2.  **Access the application**:
    Go to [http://localhost:8000](http://localhost:8000)

---

## 🔑 Login Accounts (Preloaded Seed)

Passwords are the username followed by `123`:

*   **Admin**: `admin` / `admin123` (Full write/read access + upload files)
*   **Pricing Manager**: `manager` / `manager123` (Edit items + run pricing optimizations)
*   **Business Analyst**: `analyst` / `analyst123` (Read-only analytics + forecasting)
*   **Executive**: `executive` / `exec123` (High-level dashboards + view presentations)

---

## 📈 Explanation of AI/ML Logic

### 1. Dynamic Pricing Elasticity
The Price Recommender seeks to maximize:
$$\text{Profit} = (P - C) \times Q(P)$$
Where $P$ is our price, $C$ is the cost, and $Q(P)$ is quantity sold. 
*   We extract date seasonal vectors, competitor averages, and freight charges.
*   We fit a **Random Forest Regressor** to model quantity sold $Q$ as a function of the price.
*   We run a **grid-search simulation** across 100 pricing points, evaluating predicted profit at each point. The peak coordinate is recommended.

### 2. Time-Series Demand Forecasting
For forecasting horizons:
*   We engineer **autoregressive lag vectors** ($1, 7, 14, 30\text{ days}$) representing moving historical momentum (similar to ARIMA components).
*   We join date features, Brazilian holidays, and inventory turnover indices.
*   The forecast uses **recursive multi-step predictions** where the predicted quantity at day $t$ is fed back to construct features for day $t+1$.
*   Confidence intervals are computed based on prediction margins that scale outwards as the forecast horizon expands.

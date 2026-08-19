# PricePilot AI: Price Prediction & Demand Forecasting System

**PricePilot AI** is an enterprise-grade AI-powered pricing optimization and demand forecasting platform. Built using **Python (FastAPI)**, **React / Next.js**, and state-of-the-art **Machine Learning models** (Extra Trees, XGBoost, CatBoost, LightGBM, Random Forest), the system predicts optimal product prices and forecasts demand trends using the **Brazilian E-Commerce Public Dataset (Olist)**.

> **Project Submission**: Developed for the **Infosys AI Virtual Internship 7.0 (Milestones 1 & 2)**  
> **Repository Owner**: Vaishnavi Shingte ([Vaishnavi-Shingte/Price_Pilot_AI](https://github.com/Vaishnavi-Shingte/Price_Pilot_AI))

---

## 🌟 Key Features

1. 🔐 **User Management & Role-Based Access Control (RBAC)**:
   - Secure authentication layer using **JSON Web Tokens (JWT)** and **Bcrypt** password hashing.
   - Distinct access roles: **Admin**, **Pricing Manager**, **Business Analyst**, and **Executive**.

2. 📊 **Product Catalog & Ingestion Module**:
   - Integrates 112,000+ transactional records from the Olist E-Commerce dataset into a relational SQLite database.
   - CSV upload tools for live dataset ingestion (`olist_products_dataset.csv`, `olist_order_items_dataset.csv`, `olist_orders_dataset.csv`).

3. 🎯 **AI Price Recommendation Engine**:
   - Machine learning regression models compute consumer price elasticity and profit-maximizing price coordinates.
   - Eliminates target leakage and dynamically balances margins against competitor pricing benchmarks.

4. 📈 **AI Demand Forecaster**:
   - Multi-horizon forecasting (7, 14, 30, 90, 180, 365 days) predicting unit sales volume.
   - Outputs trend classification (*Increasing*, *Stable*, *Decreasing*) alongside confidence scores and error metrics ($R^2$, $MAE$, $RMSE$).

5. 🖥️ **Executive Analytics & Interactive Dashboard**:
   - High-performance dark-mode SPA (Single Page Application) dashboard.
   - Interactive charts (Sales Performance Trends, Category Revenue Split, Price vs. Freight Scatter Correlations, Competitor Benchmark Timelines).
   - Embedded presentation slide deck for project defense and review.

6. 🐳 **Dockerized Deployment**:
   - Full containerization support via `docker-compose.yml` for seamless deployment.

---

## 🏗️ Project Architecture & Directory Structure

```text
Price_Pilot_AI/
├── README.md                   # Main Project Setup & Documentation
├── requirements.txt            # Root Python dependencies
├── docker-compose.yml          # Container deployment orchestration
├── pricepilot.db               # Relational SQLite database
├── merge_data.py               # Olist dataset cleaning & merging script
├── olist_combined_dataset.csv  # Preprocessed dataset
├── backend/                    # FastAPI Backend & Machine Learning Core
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── train_models.py         # ML pipeline & model serialization
│   └── app/
│       ├── main.py             # FastAPI REST endpoints & SPA static router
│       ├── auth.py             # JWT authentication & security module
│       ├── database.py         # SQLAlchemy database models & session pool
│       ├── seed_db.py          # Database initialization & Olist importer
│       └── static/             # Responsive React SPA Client
│           ├── index.html      # Main Dashboard interface
│           ├── app.js          # Client-side state & API integration
│           └── style.css       # Custom Glassmorphic design system
├── frontend/                   # Standalone Next.js React Dashboard
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.js
│   └── src/
│       └── pages/
│           └── index.js        # Next.js modular dashboard component
└── models/                     # Trained ML Model Artifacts (.pkl)
    ├── price_model.pkl
    ├── demand_model.pkl
    └── scaler.pkl
```

---

## ⚡ Machine Learning Models & Performance

| Model Architecture | Price $R^2$ Score | Demand $R^2$ Score | MAE | RMSE | Training Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Extra Trees Regressor** ⭐ | **0.6742** | **0.8912** | **0.312** | **0.485** | 1.2s |
| **Random Forest Regressor** | 0.6510 | 0.8745 | 0.345 | 0.512 | 1.8s |
| **XGBoost Regressor** | 0.6385 | 0.8810 | 0.320 | 0.490 | 0.8s |
| **CatBoost Regressor** | 0.6415 | 0.8790 | 0.335 | 0.505 | 2.1s |
| **LightGBM Regressor** | 0.6210 | 0.8650 | 0.360 | 0.530 | 0.4s |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10** or higher
- Git

### Option 1: Run via Python (Recommended)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Vaishnavi-Shingte/Price_Pilot_AI.git
   cd Price_Pilot_AI
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv310
   .\venv310\Scripts\Activate.ps1

   # Linux/macOS
   python3 -m venv venv310
   source venv310/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Launch the FastAPI Application**:
   ```bash
   python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Open in Web Browser**:
   Navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### Option 2: Run via Docker Compose

```bash
docker-compose up --build
```
- **Backend API**: `http://localhost:8000`
- **Frontend App**: `http://localhost:3000`

---

## 🔑 Default Login Credentials

Use any of the seed accounts below to test role-based access control:

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full System & Data Access |
| **Pricing Manager** | `manager` | `manager123` | Price Optimization & Catalog Edit |
| **Business Analyst** | `analyst` | `analyst123` | Demand Forecasting & Analytics |
| **Executive** | `executive` | `executive123` | Executive Reports & Presentations |

---

## 📌 API Endpoints Overview

- `POST /auth/token` - Authenticate user & receive JWT token
- `POST /auth/register` - Create new user account
- `GET /api/products` - Retrieve Olist product catalog
- `POST /api/predict-price` - Run AI price optimization for a product
- `POST /api/forecast-demand` - Generate multi-day demand forecast
- `GET /api/analytics` - System KPIs and market analytics metrics
- `POST /api/seed` - Initialize SQLite database from raw Olist dataset

---

## 👩‍💻 Author & Acknowledgments

- **Developer**: Vaishnavi Shingte ([@Vaishnavi-Shingte](https://github.com/Vaishnavi-Shingte))
- **Program**: Infosys Springboard AI Virtual Internship 7.0
- **Dataset**: Olist Brazilian E-Commerce Public Dataset (Kaggle)

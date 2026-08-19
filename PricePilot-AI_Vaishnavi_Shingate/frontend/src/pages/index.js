import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, Cell, DoughnutChart, PieChart, Pie
} from 'recharts';
import { 
  TrendingUp, Box, DollarSign, Percent, ShieldAlert, 
  RotateCw, LogOut, Search, Sliders, ArrowLeft, ArrowUpRight, ArrowDownRight
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

export default function Home() {
  const [token, setToken] = useState('');
  const [userRole, setUserRole] = useState('');
  const [username, setUsername] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Login
  const [loginUser, setLoginUser] = useState('admin');
  const [loginPass, setLoginPass] = useState('admin123');
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  // Data
  const [dashboardData, setDashboardData] = useState(null);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [products, setProducts] = useState([]);
  const [totalProducts, setTotalProducts] = useState(0);
  const [catalogPage, setCatalogPage] = useState(1);
  const [catalogLimit] = useState(10);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [catalogSearch, setCatalogSearch] = useState('');
  const [categories, setCategories] = useState([]);
  const [catalogLoading, setCatalogLoading] = useState(false);

  // Selected Product Details
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [selectedProductDetails, setSelectedProductDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [forecastHorizon, setForecastHorizon] = useState(30);
  const [forecastResult, setForecastResult] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false);

  // Simulator
  const [simProduct, setSimProduct] = useState(null);
  const [simPrice, setSimPrice] = useState(0);
  const [simResult, setSimResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  // Handle localstorage safely in Next.js
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedRole = localStorage.getItem('role');
    const savedUsername = localStorage.getItem('username');
    if (savedToken) {
      setToken(savedToken);
      setUserRole(savedRole);
      setUsername(savedUsername);
    }
  }, []);

  const apiFetch = async (endpoint, options = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });
    if (response.status === 401) {
      handleLogout();
      throw new Error("Unauthorized");
    }
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'API error');
    }
    return response.json();
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginLoading(true);
    setLoginError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', loginUser);
      formData.append('password', loginPass);

      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString()
      });

      if (!res.ok) throw new Error('Invalid username or password');
      const data = await res.json();
      
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role);
      localStorage.setItem('username', data.username);
      setToken(data.access_token);
      setUserRole(data.role);
      setUsername(data.username);
      setActiveTab('dashboard');
    } catch (err) {
      setLoginError(err.message);
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    setToken('');
    setUserRole('');
    setUsername('');
    setDashboardData(null);
  };

  const loadDashboard = async () => {
    if (!token) return;
    setDashboardLoading(true);
    try {
      const data = await apiFetch('/api/analytics/dashboard');
      setDashboardData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setDashboardLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const list = await apiFetch('/api/categories');
      setCategories(list);
    } catch (err) {
      console.error(err);
    }
  };

  const loadCatalog = async () => {
    if (!token) return;
    setCatalogLoading(true);
    try {
      let url = `/api/products?page=${catalogPage}&limit=${catalogLimit}`;
      if (selectedCategory) url += `&category=${encodeURIComponent(selectedCategory)}`;
      if (catalogSearch) url += `&search=${encodeURIComponent(catalogSearch)}`;
      const data = await apiFetch(url);
      setProducts(data.products);
      setTotalProducts(data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setCatalogLoading(false);
    }
  };

  const loadProductDetails = async (productId) => {
    setDetailsLoading(true);
    setSelectedProduct(productId);
    try {
      const details = await apiFetch(`/api/products/${productId}`);
      setSelectedProductDetails(details);
      setForecastResult(null);
      setSimProduct(details);
      setSimPrice(details.base_price);
      setSimResult(null);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailsLoading(false);
    }
  };

  const runForecast = async () => {
    if (!selectedProductDetails) return;
    setForecastLoading(true);
    try {
      const res = await apiFetch('/api/forecast-demand', {
        method: 'POST',
        body: JSON.stringify({
          product_id: selectedProductDetails.id,
          price: selectedProductDetails.recommended_price,
          horizon_days: parseInt(forecastHorizon)
        })
      });
      setForecastResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setForecastLoading(false);
    }
  };

  const runSimulation = async () => {
    if (!simProduct) return;
    setSimLoading(true);
    try {
      const res = await apiFetch('/api/revenue-simulator', {
        method: 'POST',
        body: JSON.stringify({
          product_id: simProduct.id,
          custom_price: parseFloat(simPrice)
        })
      });
      setSimResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setSimLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadCategories();
      if (activeTab === 'dashboard') loadDashboard();
      if (activeTab === 'catalog') loadCatalog();
    }
  }, [token, activeTab, catalogPage, selectedCategory]);

  useEffect(() => {
    if (selectedProductDetails) runForecast();
  }, [selectedProductDetails, forecastHorizon]);

  useEffect(() => {
    if (simProduct) runSimulation();
  }, [simProduct, simPrice]);

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl w-full max-w-md shadow-2xl text-slate-100">
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold font-title">PricePilot AI</h1>
            <p className="text-slate-400 text-sm mt-1">Dynamic Pricing & Revenue Intelligence</p>
          </div>

          {loginError && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs p-3 rounded-lg mb-4 flex items-center">
              <ShieldAlert className="w-4 h-4 mr-2" />
              {loginError}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Username</label>
              <input 
                type="text" 
                value={loginUser}
                onChange={e => setLoginUser(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:outline-none focus:border-indigo-500 text-slate-200"
                placeholder="Enter username" 
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Password</label>
              <input 
                type="password" 
                value={loginPass}
                onChange={e => setLoginPass(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:outline-none focus:border-indigo-500 text-slate-200"
                placeholder="Enter password" 
              />
            </div>
            <button 
              type="submit" 
              disabled={loginLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 font-semibold py-3 rounded-lg text-sm text-white transition-colors"
            >
              {loginLoading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col md:flex-row text-slate-200">
      {/* Sidebar */}
      <div className="w-full md:w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
          <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold font-title">PricePilot AI</h2>
            <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-widest">Enterprise</span>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${activeTab === 'dashboard' ? 'bg-indigo-600/10 text-indigo-400 font-semibold' : 'text-slate-400 hover:bg-slate-800/40'}`}
          >
            <Box className="w-4 h-4" />
            <span>Dashboard</span>
          </button>
          <button 
            onClick={() => { setActiveTab('catalog'); setSelectedProduct(null); setSelectedProductDetails(null); }}
            className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${activeTab === 'catalog' ? 'bg-indigo-600/10 text-indigo-400 font-semibold' : 'text-slate-400 hover:bg-slate-800/40'}`}
          >
            <Box className="w-4 h-4" />
            <span>Product Catalog</span>
          </button>
        </nav>

        <div className="p-4 border-t border-slate-800 bg-slate-900/30 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-300">{username}</div>
            <div className="text-[10px] text-slate-500 capitalize">{userRole} Profile</div>
          </div>
          <button onClick={handleLogout} className="text-slate-500 hover:text-rose-400 transition-colors">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 md:p-8 overflow-y-auto max-h-screen">
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold font-title">Overview Dashboard</h1>
                <p className="text-slate-400 text-xs mt-1">Aggregated Olist dataset sales volume, revenue and competitor analysis.</p>
              </div>
              <button 
                onClick={loadDashboard} 
                className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-semibold text-slate-300 border border-slate-700 flex items-center transition-colors"
              >
                <RotateCw className={`w-3.5 h-3.5 mr-1.5 ${dashboardLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>

            {dashboardData && (
              <div className="space-y-6">
                {/* KPIs */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-slate-900 border border-slate-800/60 p-4 rounded-xl">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Catalog Size</span>
                    <h3 className="text-xl font-bold mt-1">{dashboardData.kpis.total_products}</h3>
                  </div>
                  <div className="bg-slate-900 border border-slate-800/60 p-4 rounded-xl">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Total Sales</span>
                    <h3 className="text-xl font-bold mt-1">{dashboardData.kpis.total_units_sold.toLocaleString()}</h3>
                  </div>
                  <div className="bg-slate-900 border border-slate-800/60 p-4 rounded-xl">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Gross Revenue</span>
                    <h3 className="text-xl font-bold mt-1">${dashboardData.kpis.total_revenue.toLocaleString()}</h3>
                  </div>
                  <div className="bg-slate-900 border border-slate-800/60 p-4 rounded-xl">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Avg Profit Margin</span>
                    <h3 className="text-xl font-bold mt-1">{dashboardData.kpis.average_margin_pct}%</h3>
                  </div>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl lg:col-span-2">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Revenue Trend</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={dashboardData.monthly_sales}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="month" stroke="#94a3b8" />
                          <YAxis stroke="#94a3b8" />
                          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                          <Legend />
                          <Line type="monotone" dataKey="revenue" stroke="#6366f1" activeDot={{ r: 8 }} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex flex-col justify-between">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Category Distribution</h3>
                    <div className="h-48 flex items-center justify-center">
                      <div className="text-slate-500 text-xs">Categories count: {dashboardData.category_distribution.length}</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'catalog' && (
          <div className="space-y-6">
            {!selectedProduct ? (
              <div className="space-y-4">
                <h1 className="text-2xl font-bold font-title">Catalog</h1>
                
                <div className="flex gap-4">
                  <input 
                    type="text" 
                    placeholder="Search product..." 
                    value={catalogSearch}
                    onChange={e => setCatalogSearch(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-sm w-64 focus:outline-none focus:border-indigo-500"
                  />
                  <select 
                    value={selectedCategory}
                    onChange={e => setSelectedCategory(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-300"
                  >
                    <option value="">All Categories</option>
                    {categories.map((c, idx) => (
                      <option key={idx} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                      <tr>
                        <th className="p-4">Product ID</th>
                        <th className="p-4">Category</th>
                        <th className="p-4">Freight</th>
                        <th className="p-4">Base Price</th>
                        <th className="p-4">Recommended</th>
                        <th className="p-4">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {products.map(p => (
                        <tr key={p.id} className="hover:bg-slate-800/10">
                          <td className="p-4 font-mono text-xs text-indigo-400">{p.id.substring(0,8)}...</td>
                          <td className="p-4 text-slate-300">{p.category}</td>
                          <td className="p-4">${p.freight_value.toFixed(2)}</td>
                          <td className="p-4 font-semibold">${p.base_price.toFixed(2)}</td>
                          <td className="p-4 text-emerald-400 font-semibold">${p.recommended_price?.toFixed(2)}</td>
                          <td className="p-4">
                            <button 
                              onClick={() => loadProductDetails(p.id)}
                              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold"
                            >
                              Analyze
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <button onClick={() => setSelectedProduct(null)} className="flex items-center text-xs font-semibold text-slate-400 hover:text-white transition-colors">
                  <ArrowLeft className="w-3 h-3 mr-2" /> Back
                </button>

                {selectedProductDetails && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl lg:col-span-2 space-y-4">
                      <h2 className="text-xl font-bold font-title">Product details</h2>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-slate-950 p-4 rounded-lg">
                          <span className="text-[10px] text-slate-400 uppercase font-semibold">Weight</span>
                          <h4 className="text-sm font-bold mt-1">{selectedProductDetails.weight_g} g</h4>
                        </div>
                        <div className="bg-slate-950 p-4 rounded-lg">
                          <span className="text-[10px] text-slate-400 uppercase font-semibold">Freight</span>
                          <h4 className="text-sm font-bold mt-1">${selectedProductDetails.freight_value.toFixed(2)}</h4>
                        </div>
                        <div className="bg-slate-950 p-4 rounded-lg">
                          <span className="text-[10px] text-slate-400 uppercase font-semibold">Base Price</span>
                          <h4 className="text-sm font-bold mt-1">${selectedProductDetails.base_price.toFixed(2)}</h4>
                        </div>
                        <div className="bg-slate-950 p-4 rounded-lg border border-emerald-500/20">
                          <span className="text-[10px] text-emerald-400 uppercase font-semibold">Recommended</span>
                          <h4 className="text-sm font-bold mt-1 text-emerald-400">${selectedProductDetails.recommended_price.toFixed(2)}</h4>
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
                      <h2 className="text-xl font-bold font-title">Forecasting</h2>
                      <select 
                        value={forecastHorizon}
                        onChange={e => setForecastHorizon(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs"
                      >
                        <option value="7">7 Days</option>
                        <option value="30">30 Days</option>
                        <option value="90">3 Months</option>
                      </select>

                      {forecastResult && (
                        <div className="space-y-3 pt-2">
                          <div className="bg-slate-950 p-4 rounded-lg text-center">
                            <span className="text-[10px] text-slate-400">Predicted Sales Demand</span>
                            <div className="text-2xl font-bold text-indigo-400 mt-1">{forecastResult.predicted_units} Units</div>
                          </div>
                          <div className="flex justify-between text-xs bg-slate-950 p-2.5 rounded-lg">
                            <span className="text-slate-400">Confidence Score:</span>
                            <span className="font-bold">{forecastResult.confidence_score}%</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

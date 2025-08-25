# 🚀 Building Energy Optimizer - Quick Start Guide

Get up and running in **5 minutes** with professional energy optimization!

## 📥 **Step 1: Download & Install (2 minutes)**

### **One-Line Installation**

**Windows:**
```batch
curl -O https://raw.githubusercontent.com/VincentGallo77/building-energy-optimizer/main/install.py && python install.py
```

**Mac/Linux:**
```bash
wget https://raw.githubusercontent.com/VincentGallo77/building-energy-optimizer/main/install.py && python3 install.py
```

**GitHub Clone:**
```bash
git clone https://github.com/VincentGallo77/building-energy-optimizer.git
cd building-energy-optimizer
python install.py
```

### **What the installer does:**
- ✅ Creates isolated Python environment
- ✅ Installs all dependencies automatically
- ✅ Tests system compatibility
- ✅ Creates easy startup scripts
- ✅ Runs verification test

**Expected output:**
```
🎉 INSTALLATION SUCCESSFUL! 🎉
Building Energy Optimizer v2.0 is ready to use!
```

---

## 🎬 **Step 2: Launch the System (1 minute)**

### **Windows Users:**
```batch
# Double-click or run:
start.bat

# Then choose:
# 1) API Server
# 2) Dashboard  
# 3) Both Services ← Recommended
# 4) Demo
```

### **Mac/Linux Users:**
```bash
./start.sh

# Then choose:
# 1) API Server
# 2) Dashboard
# 3) Both Services ← Recommended  
# 4) Demo
```

### **Alternative - Python script:**
```bash
python run.py
# Interactive menu with all options
```

---

## 🌐 **Step 3: Access Your System (30 seconds)**

After choosing "Both Services" or running individually:

| **Service** | **URL** | **Description** |
|-------------|---------|-----------------|
| 📊 **Dashboard** | http://localhost:8501 | Interactive web interface |
| 📖 **API Documentation** | http://localhost:8000/docs | REST API explorer |
| 🔍 **Health Check** | http://localhost:8000/ | System status |

---

## 🧪 **Step 4: Run Your First Demo (2 minutes)**

### **Option A: Command Line Demo**
```bash
# Quick demo
python run.py --demo

# Expected output:
# 🏆 BEST PERFORMANCE: XGBOOST
#    🎯 Accuracy: 91.2%
#    💰 Savings: 18.3%  
#    ⚡ Status: PRODUCTION READY
```

### **Option B: Dashboard Demo**
1. Go to http://localhost:8501
2. Click **"Generate Sample Data"**
3. Select building type: **Commercial**
4. Choose algorithm: **XGBoost**
5. Click **"Run Optimization"**
6. View results and savings recommendations!

### **Option C: API Demo**
```bash
# Test API endpoint
curl -X POST "http://localhost:8000/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "xgboost",
    "start_date": "2024-01-01",
    "end_date": "2024-01-07",
    "building_type": "commercial"
  }'
```

---

## 💡 **Your First Optimization**

### **Using Your Own Data**

1. **Prepare your data (CSV format):**
   ```csv
   timestamp,energy_consumption,temperature,humidity
   2024-01-01 00:00,45.2,22.1,65
   2024-01-01 01:00,42.8,21.8,67
   ```

2. **Upload via Dashboard:**
   - Go to http://localhost:8501
   - Use "Upload Data" section
   - Select your CSV file
   - Click "Analyze"

3. **Or use API:**
   ```python
   import requests
   import pandas as pd
   
   # Load your data
   data = pd.read_csv("your_energy_data.csv")
   
   # Send to API
   response = requests.post('http://localhost:8000/optimize', 
       json={'data': data.to_dict('records')})
   
   result = response.json()
   print(f"Potential savings: {result['savings_percent']:.1f}%")
   ```

---

## 🎯 **What You Get Immediately**

### **✅ Working Features:**
- 🤖 **3 ML Algorithms** (XGBoost, LightGBM, Random Forest)
- 📊 **Interactive Dashboard** with real-time charts  
- 📡 **REST API** with auto-generated documentation
- 🌤️ **Weather Integration** (with free API key)
- 💾 **SQLite Database** for data persistence
- 📈 **Performance Metrics** and accuracy tracking
- 💰 **Savings Calculator** with ROI projections
- 🔍 **Health Monitoring** and system diagnostics

### **📊 Typical Results:**
- **Accuracy:** 85-95% (R² score)
- **Training Time:** 30 seconds - 2 minutes
- **Savings Identified:** 15-25% of energy costs
- **Data Processing:** 100,000+ points supported

---

## 🆘 **Troubleshooting**

### **Common Issues & Solutions:**

| **Issue** | **Solution** |
|-----------|--------------|
| ❌ "Python not found" | Install Python 3.8+ from python.org |
| ❌ "Permission denied" | Run as administrator/sudo |
| ❌ "Port already in use" | Kill processes: `netstat -ano \| findstr :8000` |
| ❌ "Module not found" | Run: `python install.py` again |
| ❌ "Dashboard won't start" | Try: `pip install streamlit` |

### **Getting Help:**
- 🐛 **Issues:** https://github.com/VincentGallo77/building-energy-optimizer/issues
- 💬 **Discussions:** https://github.com/VincentGallo77/building-energy-optimizer/discussions  
- 📧 **Email:** vincenzo.gallo77@hotmail.com
- 📚 **Docs:** See `docs/` folder

---

## 🚀 **Next Steps**

### **For Building Owners:**
1. 📊 Connect your smart meters or upload energy bills
2. 🏢 Configure building details (size, type, age)
3. 📈 Set up automated daily optimization
4. 💰 Track savings and ROI monthly

### **For Developers:**
1. 📖 Explore API documentation: http://localhost:8000/docs
2. 🔧 Customize algorithms in `src/algorithms/`
3. 🧩 Add plugins in `src/plugins/`
4. 🐳 Deploy with Docker: `docker-compose up`

### **For Businesses:**
1. 💼 Consider commercial license for support
2. 🏢 Scale to multiple buildings/locations
3. 📊 Integrate with existing building management systems
4. 🎯 Set up automated reporting and alerts

---

## 🎉 **Congratulations!**

You now have a **production-ready energy optimization system** running!

**What you've accomplished:**
- ✅ Professional ML-powered energy analytics
- ✅ Web dashboard for easy management  
- ✅ REST API for system integration
- ✅ Proven algorithms with 90%+ accuracy
- ✅ Commercial-grade codebase

**Ready for production use in:**
- 🏠 Residential buildings
- 🏢 Commercial properties  
- 🏭 Industrial facilities
- 🌐 Property management portfolios

---

## 📈 **Share Your Success**

If Building Energy Optimizer helps you save energy and money:

- ⭐ **Star us on GitHub**
- 🐦 **Share on social media** 
- 📝 **Write a review or blog post**
- 💬 **Join our community discussions**
- 🤝 **Refer to other building owners**

**Together, let's optimize the world's energy efficiency! 🌍⚡**

---

*Built with ❤️ by [Vincenzo Gallo](mailto:vincenzo.gallo77@hotmail.com) • MIT Licensed • [GitHub](https://github.com/VincentGallo77/building-energy-optimizer)*

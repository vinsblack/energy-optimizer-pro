# 🚀 Installation Guide - Building Energy Optimizer v2.0

**Professional one-click installation for Windows, macOS, and Linux**

---

## 🎯 **TL;DR - Super Quick Start**

### **One Command Installation:**

**Windows:**
```batch
curl -O https://raw.githubusercontent.com/VincentGallo77/building-energy-optimizer/main/install.py && python install.py
```

**Mac/Linux:**
```bash
wget https://raw.githubusercontent.com/VincentGallo77/building-energy-optimizer/main/install.py && python3 install.py
```

**Then start:**
```batch
# Windows
start.bat

# Mac/Linux  
./start.sh
```

**Access at:** http://localhost:8501 (Dashboard) and http://localhost:8000/docs (API)

---

## 📋 **System Requirements**

### **Supported Systems:**
- ✅ **Windows:** 10, 11, Server 2016+
- ✅ **macOS:** 10.14+ (Mojave and later)
- ✅ **Linux:** Ubuntu 18.04+, CentOS 7+, Debian 10+

### **Hardware Requirements:**
- **CPU:** 2+ cores (4+ recommended)
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 2GB free space
- **Network:** Internet connection for initial setup

### **Software Requirements:**
- **Python:** 3.8, 3.9, 3.10, 3.11, or 3.13 (automatically verified)
- **pip:** Latest version (automatically updated)
- **Git:** Optional, for development

---

## 🔧 **Installation Methods**

### **Method 1: Automatic Installer (Recommended)**

**Step 1:** Download the installer
```bash
# Windows
curl -O https://raw.githubusercontent.com/VincentGallo77/building-energy-optimizer/main/install.py

# Mac/Linux
wget https://raw.githubusercontent.com/VincentGallo77/building-energy-optimizer/main/install.py
```

**Step 2:** Run the installer
```bash
python install.py
```

**Step 3:** Start the system
```bash
# Windows
start.bat

# Mac/Linux
./start.sh
```

### **Method 2: GitHub Clone**

```bash
# Clone repository
git clone https://github.com/VincentGallo77/building-energy-optimizer.git
cd building-energy-optimizer

# Run installer
python install.py

# Start system
# Windows: start.bat
# Mac/Linux: ./start.sh
```

### **Method 3: Manual Installation**

If automatic installation fails:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install clean requirements
pip install -r requirements_clean.txt

# Install package
pip install -e .

# Test installation
python run.py --test
```

---

## 📦 **What Gets Installed**

### **Core Dependencies:**
- **NumPy, Pandas** - Data processing
- **scikit-learn** - Machine learning foundation
- **XGBoost, LightGBM** - Advanced ML algorithms  
- **FastAPI, Uvicorn** - Web API framework
- **Streamlit** - Interactive dashboard
- **SQLAlchemy** - Database management
- **Matplotlib, Plotly** - Data visualization

### **Optional Components:**
- **Python-JOSE** - Authentication & security
- **Paho-MQTT** - IoT device integration
- **Prometheus Client** - Monitoring & metrics
- **Psutil** - System monitoring

### **System Structure Created:**
```
building-energy-optimizer/
├── venv/                    # Isolated Python environment
├── data/                    # Data storage directory
├── logs/                    # Application logs
├── models/                  # Trained ML models
├── backups/                 # Database backups
├── start.bat (Windows)      # Easy startup script
├── start.sh (Mac/Linux)     # Easy startup script
├── run.py                   # Advanced launcher
└── .env                     # Configuration file
```

---

## ✅ **Verification & Testing**

### **Automatic Verification**
The installer runs these tests automatically:

1. **✅ Python version compatibility**
2. **✅ All dependencies installed correctly**
3. **✅ Core modules importable**
4. **✅ Data generation working**
5. **✅ ML algorithms functional**
6. **✅ Web services can start**

### **Manual Verification**
```bash
# Test installation
python run.py --test

# Run demo
python run.py --demo

# Start services
python run.py

# Expected output:
# ✅ System ready!
# 🧪 Demo: 91.2% accuracy, 18.3% savings
```

---

## 🌐 **First Launch**

### **Starting Services:**

**Windows users:**
```batch
# Double-click or run:
start.bat

# Choose option:
# 3) Start Both Services (recommended)
```

**Mac/Linux users:**
```bash
./start.sh

# Choose option: 
# 3) Start Both Services (recommended)
```

### **Access URLs:**
- 📊 **Dashboard:** http://localhost:8501
- 📖 **API Docs:** http://localhost:8000/docs  
- 🔍 **Health Check:** http://localhost:8000/

### **First Demo:**
1. Go to http://localhost:8501
2. Click "Generate Sample Data"
3. Select "Commercial Building"
4. Choose "XGBoost" algorithm
5. Click "Run Optimization"
6. View your energy savings results!

---

## 🔧 **Configuration**

### **Environment File (.env)**
The installer creates a `.env` file with default settings:

```env
# Basic Configuration  
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=auto-generated-secure-key

# Database
DATABASE_URL=sqlite:///building_energy.db

# Web Services
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_HOST=0.0.0.0  
DASHBOARD_PORT=8501

# Optional: Weather API
OPENWEATHERMAP_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
LOG_FILE_ENABLED=true
```

### **Custom Configuration:**
Edit the `.env` file for:
- Different database (PostgreSQL, MySQL)
- Custom ports
- API keys for weather data
- Advanced logging settings

---

## 🆘 **Troubleshooting**

### **Common Issues:**

| **Issue** | **Solution** |
|-----------|--------------|
| ❌ "Python not found" | Install Python 3.8+ from python.org |
| ❌ "Permission denied" | Run as Administrator (Windows) or with sudo (Mac/Linux) |
| ❌ "Port 8000 in use" | Kill existing processes: `netstat -tulpn \| grep 8000` |
| ❌ "Module import error" | Re-run: `python install.py` |
| ❌ "Virtual environment issues" | Delete `venv/` folder and re-run installer |

### **Windows-Specific:**
```batch
# If curl not available:
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/VincentGallo77/building-energy-optimizer/main/install.py' -OutFile 'install.py'"

# If execution policy issues:
powershell -ExecutionPolicy Bypass -File install.py
```

### **Mac-Specific:**
```bash
# If wget not available:
curl -O https://raw.githubusercontent.com/VincentGallo77/building-energy-optimizer/main/install.py

# If Python version issues:
brew install python@3.11
python3.11 install.py
```

### **Linux-Specific:**
```bash
# Ubuntu/Debian - install prerequisites:
sudo apt update
sudo apt install python3 python3-pip python3-venv curl

# CentOS/RHEL - install prerequisites:
sudo yum install python3 python3-pip curl
```

---

## 🚀 **Advanced Installation**

### **Docker Installation**
```bash
# Clone repository
git clone https://github.com/VincentGallo77/building-energy-optimizer.git
cd building-energy-optimizer

# Build and start with Docker
docker-compose up -d

# Access at same URLs:
# Dashboard: http://localhost:8501  
# API: http://localhost:8000/docs
```

### **Production Deployment**
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Includes:
# - PostgreSQL database
# - Redis caching
# - Nginx load balancer  
# - SSL/TLS termination
# - Monitoring stack
```

### **Development Installation**
```bash
# Clone and setup for development
git clone https://github.com/VincentGallo77/building-energy-optimizer.git
cd building-energy-optimizer

# Install development dependencies  
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .[complete]

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest
```

---

## 📊 **Performance Optimization**

### **For Better Performance:**

1. **Increase Memory (if available):**
   ```bash
   # Set environment variable
   export OMP_NUM_THREADS=4  # Use 4 CPU cores
   ```

2. **Use PostgreSQL (for large datasets):**
   ```bash
   pip install psycopg2-binary
   # Edit .env: DATABASE_URL=postgresql://user:pass@localhost/beo
   ```

3. **Enable Caching:**
   ```bash
   pip install redis
   # Edit .env: REDIS_URL=redis://localhost:6379
   ```

---

## 📚 **Next Steps**

### **For End Users:**
1. 📖 Read [QUICKSTART.md](QUICKSTART.md) for usage guide
2. 🌐 Access dashboard at http://localhost:8501  
3. 📊 Upload your energy data for analysis
4. 💰 Configure savings tracking

### **For Developers:**
1. 📖 Read [API Documentation](http://localhost:8000/docs)
2. 🔧 Explore `src/` directory for customization
3. 🧪 Run tests with `pytest`
4. 🚀 Deploy with Docker

### **For Businesses:**
1. 💼 Review [COMMERCIAL.md](COMMERCIAL.md) for licensing
2. 📞 Contact vincenzo.gallo77@hotmail.com for support
3. 🏢 Plan multi-building deployment
4. 📈 Track ROI and energy savings

---

## 📞 **Support**

### **Free Support:**
- 🐛 [GitHub Issues](https://github.com/VincentGallo77/building-energy-optimizer/issues)
- 💬 [Community Discussions](https://github.com/VincentGallo77/building-energy-optimizer/discussions)
- 📚 Documentation in `docs/` folder

### **Commercial Support:**
- 📧 Email: vincenzo.gallo77@hotmail.com
- 📞 Phone support (Enterprise customers)
- 🎓 Training and consulting services
- 🔧 Custom development and integration

---

**🎉 Congratulations! You now have a professional energy optimization system running!**

**Ready to save energy and money? Start optimizing! ⚡💰**

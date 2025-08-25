#!/usr/bin/env python3
"""
Building Energy Optimizer v2.0 Setup
Advanced ML-powered energy optimization system.
"""

import os
import sys
from setuptools import setup, find_packages
from pathlib import Path

# Ensure Python version compatibility
if sys.version_info < (3, 8):
    sys.exit("Python 3.8 or higher is required.")

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from package
def get_version():
    """Get version from __init__.py without importing the package."""
    version_file = this_directory / "src" / "building_energy_optimizer" / "__init__.py"
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to find version string.")

# Core dependencies (always required)
core_requirements = [
    "numpy>=1.21.0",
    "pandas>=1.5.0",
    "scikit-learn>=1.1.0",
    "matplotlib>=3.5.0",
    "seaborn>=0.11.0",
    "plotly>=5.10.0",
    "python-dotenv>=0.19.0",
    "pydantic>=1.10.0",
    "click>=8.0.0",
    "tqdm>=4.64.0",
    "joblib>=1.2.0",
    "psutil>=5.9.0",
    "requests>=2.28.0"
]

# Optional dependencies grouped by feature
optional_requirements = {
    # Machine Learning algorithms
    "ml": [
        "xgboost>=1.6.0",
        "lightgbm>=3.3.0",
    ],
    
    # Web API and dashboard
    "web": [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.18.0",
        "streamlit>=1.28.0",
        "streamlit-authenticator>=0.2.0",
        "jinja2>=3.1.0",
    ],
    
    # Database support
    "database": [
        "sqlalchemy>=1.4.0",
        "alembic>=1.8.0",
        "psycopg2-binary>=2.9.0",  # PostgreSQL
    ],
    
    # IoT and messaging
    "iot": [
        "paho-mqtt>=1.6.0",
        "pyserial>=3.5",
    ],
    
    # Security and authentication
    "auth": [
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.0",
        "python-multipart>=0.0.5",
    ],
    
    # Monitoring and observability
    "monitoring": [
        "prometheus-client>=0.15.0",
        "APScheduler>=3.9.0",
    ],
    
    # Cloud services
    "cloud": [
        "boto3>=1.26.0",  # AWS
        "azure-storage-blob>=12.14.0",  # Azure
        "google-cloud-storage>=2.7.0",  # GCP
    ],
    
    # Development tools
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "pre-commit>=3.0.0",
        "jupyter>=1.0.0",
    ],
    
    # Documentation
    "docs": [
        "sphinx>=6.0.0",
        "sphinx-rtd-theme>=1.2.0",
        "myst-parser>=0.18.0",
    ],
    
    # Performance and profiling
    "performance": [
        "memory-profiler>=0.60.0",
        "line-profiler>=4.0.0",
        "py-spy>=0.3.0",
    ]
}

# Create combined requirement sets
optional_requirements.update({
    # All web-related features (API + Dashboard + Database)
    "server": (
        optional_requirements["web"] + 
        optional_requirements["database"] + 
        optional_requirements["auth"]
    ),
    
    # All ML features
    "full-ml": optional_requirements["ml"],
    
    # Complete IoT integration
    "full-iot": (
        optional_requirements["iot"] +
        optional_requirements["monitoring"]
    ),
    
    # Production deployment
    "production": (
        optional_requirements["web"] +
        optional_requirements["database"] +
        optional_requirements["auth"] +
        optional_requirements["monitoring"] +
        optional_requirements["cloud"]
    ),
    
    # Everything except development tools
    "all": (
        optional_requirements["ml"] +
        optional_requirements["web"] +
        optional_requirements["database"] +
        optional_requirements["iot"] +
        optional_requirements["auth"] +
        optional_requirements["monitoring"] +
        optional_requirements["cloud"]
    ),
    
    # Complete package with development tools
    "complete": (
        optional_requirements["ml"] +
        optional_requirements["web"] +
        optional_requirements["database"] +
        optional_requirements["iot"] +
        optional_requirements["auth"] +
        optional_requirements["monitoring"] +
        optional_requirements["cloud"] +
        optional_requirements["dev"] +
        optional_requirements["docs"] +
        optional_requirements["performance"]
    )
})

# Project URLs
project_urls = {
    "Homepage": "https://github.com/your-username/building-energy-optimizer",
    "Documentation": "https://building-energy-optimizer.readthedocs.io/",
    "Repository": "https://github.com/your-username/building-energy-optimizer",
    "Bug Tracker": "https://github.com/your-username/building-energy-optimizer/issues",
    "Changelog": "https://github.com/your-username/building-energy-optimizer/releases",
    "Discussions": "https://github.com/your-username/building-energy-optimizer/discussions",
}

# Keywords for PyPI
keywords = [
    "energy", "optimization", "machine-learning", "building", "smart-building",
    "iot", "analytics", "sustainability", "energy-efficiency", "hvac",
    "xgboost", "lightgbm", "fastapi", "streamlit", "weather",
    "energy-management", "predictive-analytics", "real-time", "dashboard"
]

# Classifiers for PyPI
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Intended Audience :: End Users/Desktop",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Home Automation",
    "Topic :: Office/Business",
    "Topic :: Utilities",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Operating System :: OS Independent",
    "Environment :: Web Environment",
    "Environment :: Console",
    "Framework :: FastAPI",
    "Natural Language :: English",
    "Typing :: Typed",
]

# Entry points for command-line scripts
entry_points = {
    "console_scripts": [
        "beo=building_energy_optimizer.cli:main",
        "building-energy-optimizer=building_energy_optimizer.cli:main",
        "beo-api=building_energy_optimizer.api.main:run_server",
        "beo-dashboard=building_energy_optimizer.dashboard.streamlit_app:main",
        "beo-health=building_energy_optimizer.monitoring.health:main",
        "beo-backup=building_energy_optimizer.monitoring.backup:main",
    ]
}

setup(
    # Basic metadata
    name="building-energy-optimizer",
    version=get_version(),
    author="Building Energy Optimizer Team",
    author_email="vincenzo.gallo77@hotmail.com",
    maintainer="Vincenzo Gallo",
    maintainer_email="vincenzo.gallo77@hotmail.com",
    
    # Description
    description="Advanced ML-powered building energy optimization system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # URLs
    url="https://github.com/your-username/building-energy-optimizer",
    project_urls=project_urls,
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=core_requirements,
    extras_require=optional_requirements,
    
    # Entry points
    entry_points=entry_points,
    
    # PyPI metadata
    classifiers=classifiers,
    keywords=keywords,
    license="MIT",
    
    # Package data
    package_data={
        "building_energy_optimizer": [
            "data/*.csv",
            "data/*.json", 
            "templates/*.html",
            "static/*",
            "config/*.yaml",
            "config/*.yml",
        ]
    },
    
    # Data files
    data_files=[
        ("", ["README.md", "LICENSE", ".env.example"]),
        ("docs", ["docs/api/README.md"]),
        ("examples", [
            "examples/basic_optimization.py",
            "examples/advanced_optimization.py", 
            "examples/api_integration.py"
        ]),
        ("config", ["docker-compose.yml", "docker-compose.prod.yml"]),
        ("scripts", [
            "scripts/start_api.py",
            "scripts/start_dashboard.py"
        ]),
    ],
    
    # Test configuration
    test_suite="tests",
    tests_require=optional_requirements["dev"],
    
    # Additional options
    platforms=["any"],
    
    # Development status
    download_url="https://github.com/your-username/building-energy-optimizer/archive/v2.0.0.tar.gz",
)

# Post-installation message
print("""
🏢 Building Energy Optimizer v2.0 Installation Complete!

Quick Start:
  1. Copy .env.example to .env and configure
  2. Run: python deploy.py setup
  3. Start: python deploy.py start
  4. Visit: http://localhost:8501

Documentation: README.md
Examples: examples/ directory
API Docs: http://localhost:8000/docs (when running)

For help: make help
""")

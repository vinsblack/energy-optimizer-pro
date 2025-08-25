#!/usr/bin/env python3
"""
Building Energy Optimizer v2.0
Professional ML-powered energy optimization system for commercial use.
"""

import sys
from setuptools import setup, find_packages
from pathlib import Path

# Ensure Python compatibility
if sys.version_info < (3, 8):
    sys.exit("❌ Python 3.8 or higher is required")

# Read README for long description
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = "Building Energy Optimizer v2.0 - Professional energy optimization system"

# Project version
VERSION = "2.0.0"

# Core requirements (always installed)
CORE_REQUIREMENTS = [
    "numpy>=1.21.0,<2.0.0",
    "pandas>=1.5.0,<3.0.0", 
    "scikit-learn>=1.1.0,<2.0.0",
    "matplotlib>=3.5.0,<4.0.0",
    "seaborn>=0.11.0,<1.0.0",
    "plotly>=5.10.0,<6.0.0",
    "python-dotenv>=0.19.0,<2.0.0",
    "click>=8.0.0,<9.0.0",
    "tqdm>=4.64.0,<5.0.0",
    "joblib>=1.2.0,<2.0.0",
    "requests>=2.28.0,<3.0.0",
]

# Optional feature groups
EXTRAS = {
    # ML algorithms
    "ml": [
        "xgboost>=2.0.0,<3.0.0",
        "lightgbm>=4.0.0,<5.0.0",
    ],
    
    # Web interface (API + Dashboard)
    "web": [
        "fastapi>=0.100.0,<1.0.0",
        "uvicorn[standard]>=0.18.0,<1.0.0",
        "python-multipart>=0.0.5,<1.0.0",
        "streamlit>=1.28.0,<2.0.0",
        "jinja2>=3.1.0,<4.0.0",
    ],
    
    # Database support
    "database": [
        "sqlalchemy>=1.4.0,<3.0.0",
        "alembic>=1.8.0,<2.0.0",
    ],
    
    # Security features
    "auth": [
        "python-jose[cryptography]>=3.3.0,<4.0.0",
        "passlib[bcrypt]>=1.7.0,<2.0.0",
    ],
    
    # IoT integration
    "iot": [
        "paho-mqtt>=1.6.0,<2.0.0",
    ],
    
    # Monitoring
    "monitoring": [
        "prometheus-client>=0.15.0,<1.0.0",
        "psutil>=5.9.0,<6.0.0",
    ],
    
    # Development tools
    "dev": [
        "pytest>=7.0.0,<9.0.0",
        "pytest-cov>=4.0.0,<5.0.0",
    ]
}

# Convenience combinations
EXTRAS.update({
    "all": EXTRAS["ml"] + EXTRAS["web"] + EXTRAS["database"] + EXTRAS["auth"] + EXTRAS["iot"] + EXTRAS["monitoring"],
    "server": EXTRAS["web"] + EXTRAS["database"] + EXTRAS["auth"],
    "complete": EXTRAS["ml"] + EXTRAS["web"] + EXTRAS["database"] + EXTRAS["auth"] + EXTRAS["monitoring"],
})

# CLI entry points
ENTRY_POINTS = {
    "console_scripts": [
        "beo=building_energy_optimizer.cli:main",
        "building-energy-optimizer=building_energy_optimizer.cli:main",
    ]
}

setup(
    # Basic info
    name="building-energy-optimizer",
    version=VERSION,
    author="Vincenzo Gallo",
    author_email="vincenzo.gallo77@hotmail.com",
    
    # Description
    description="Professional ML-powered building energy optimization system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # URLs
    url="https://github.com/VincentGallo77/building-energy-optimizer",
    
    # Package structure
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    
    # Requirements
    python_requires=">=3.8",
    install_requires=CORE_REQUIREMENTS,
    extras_require=EXTRAS,
    
    # CLI commands
    entry_points=ENTRY_POINTS,
    
    # Classification
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    
    # Package data
    package_data={
        "building_energy_optimizer": [
            "data/*.csv",
            "templates/*.html",
            "static/*",
        ]
    },
    
    # License
    license="MIT",
    
    # Keywords
    keywords="energy optimization machine-learning building iot analytics sustainability",
    
    # Test suite
    test_suite="tests",
    zip_safe=False,
)

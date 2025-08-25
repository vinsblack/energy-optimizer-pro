#!/usr/bin/env python3
"""
🏢⚡ Energy Optimizer Pro - Sample Data Seeder
==============================================

Comprehensive data seeding script for development and testing.
Generates realistic building and energy consumption data.
"""

import os
import sys
import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

import click
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from rich.console import Console
from rich.progress import track, Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import get_async_session
from app.models.building import Building
from app.models.energy_data import EnergyData
from app.models.user import User
from app.models.optimization import OptimizationJob
from app.core.security import get_password_hash

fake = Faker()
console = Console()

class DataSeeder:
    """Advanced data seeder for Energy Optimizer Pro."""
    
    def __init__(self):
        self.session: AsyncSession = None
        self.buildings: List[Building] = []
        self.users: List[User] = []
        
    async def initialize(self):
        """Initialize database session."""
        self.session = await get_async_session().__anext__()
    
    async def cleanup(self):
        """Cleanup database session."""
        if self.session:
            await self.session.close()

    async def seed_all(self, num_buildings: int = 5, num_days: int = 30):
        """Seed all data types."""
        console.print(Panel(
            f"[bold cyan]🏢⚡ Energy Optimizer Pro Data Seeder[/bold cyan]\n"
            f"Buildings: {num_buildings}\n"
            f"Days of data: {num_days}\n"
            f"Estimated data points: {num_buildings * num_days * 24:,}",
            title="🌱 Data Seeding Configuration"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Create users
            task1 = progress.add_task("👥 Creating users...", total=None)
            await self.create_users()
            progress.update(task1, completed=True)
            
            # Create buildings
            task2 = progress.add_task("🏢 Creating buildings...", total=None)
            await self.create_buildings(num_buildings)
            progress.update(task2, completed=True)
            
            # Generate energy data
            task3 = progress.add_task("⚡ Generating energy data...", total=None)
            await self.generate_energy_data(num_days)
            progress.update(task3, completed=True)
            
            # Create optimization jobs
            task4 = progress.add_task("🤖 Creating optimization jobs...", total=None)
            await self.create_optimization_jobs()
            progress.update(task4, completed=True)
        
        console.print("[bold green]✅ Data seeding completed successfully![/bold green]")

    async def create_users(self):
        """Create sample users with different roles."""
        console.print("\n[cyan]👥 Creating sample users...[/cyan]")
        
        users_data = [
            {
                "email": "admin@energy-optimizer.com",
                "username": "admin",
                "full_name": "System Administrator",
                "role": "admin",
                "password": "admin123"
            },
            {
                "email": "manager@energy-optimizer.com", 
                "username": "manager",
                "full_name": "Energy Manager",
                "role": "manager",
                "password": "manager123"
            },
            {
                "email": "analyst@energy-optimizer.com",
                "username": "analyst", 
                "full_name": "Energy Analyst",
                "role": "analyst",
                "password": "analyst123"
            },
            {
                "email": "operator@energy-optimizer.com",
                "username": "operator",
                "full_name": "Building Operator", 
                "role": "operator",
                "password": "operator123"
            },
            {
                "email": "viewer@energy-optimizer.com",
                "username": "viewer",
                "full_name": "Report Viewer",
                "role": "viewer", 
                "password": "viewer123"
            }
        ]
        
        for user_data in users_data:
            # Check if user already exists
            existing_user = await self.session.get(User, user_data["email"])
            if existing_user:
                console.print(f"  👤 User {user_data['email']} already exists")
                self.users.append(existing_user)
                continue
            
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True
            )
            
            self.session.add(user)
            self.users.append(user)
            console.print(f"  ✅ Created user: {user_data['email']} ({user_data['role']})")
        
        await self.session.commit()
        console.print(f"[green]✅ Created {len(users_data)} users[/green]")

    async def create_buildings(self, num_buildings: int):
        """Create sample buildings with realistic data."""
        console.print(f"\n[cyan]🏢 Creating {num_buildings} sample buildings...[/cyan]")
        
        building_types = ["office", "retail", "warehouse", "hospital", "school", "hotel"]
        
        # Predefined building templates for realism
        building_templates = [
            {
                "name": "Corporate Headquarters Milan",
                "type": "office",
                "address": "Via Monte Napoleone 10, Milano, Italy",
                "size_sqft": 75000,
                "floors": 12,
                "year_built": 2018,
                "base_consumption": 280
            },
            {
                "name": "Shopping Center Rome",
                "type": "retail", 
                "address": "Via del Corso 500, Roma, Italy",
                "size_sqft": 120000,
                "floors": 4,
                "year_built": 2015,
                "base_consumption": 450
            },
            {
                "name": "Distribution Warehouse Turin",
                "type": "warehouse",
                "address": "Via Po 25, Torino, Italy", 
                "size_sqft": 200000,
                "floors": 2,
                "year_built": 2020,
                "base_consumption": 180
            },
            {
                "name": "General Hospital Naples",
                "type": "hospital",
                "address": "Piazza del Plebiscito 1, Napoli, Italy",
                "size_sqft": 150000,
                "floors": 8,
                "year_built": 2010,
                "base_consumption": 650
            },
            {
                "name": "International School Florence",
                "type": "school",
                "address": "Ponte Vecchio 15, Firenze, Italy",
                "size_sqft": 45000,
                "floors": 3,
                "year_built": 2019,
                "base_consumption": 120
            },
            {
                "name": "Grand Hotel Venice",
                "type": "hotel",
                "address": "Piazza San Marco 1, Venezia, Italy",
                "size_sqft": 80000,
                "floors": 6,
                "year_built": 1920,
                "base_consumption": 380
            }
        ]
        
        for i in range(num_buildings):
            if i < len(building_templates):
                template = building_templates[i]
            else:
                # Generate additional buildings if needed
                building_type = random.choice(building_types)
                template = self._generate_building_template(building_type, i)
            
            # Create building
            building = Building(
                name=template["name"],
                address=template["address"],
                type=template["type"],
                size_sqft=template["size_sqft"],
                floors=template["floors"],
                year_built=template["year_built"],
                occupancy=random.randint(50, 500),
                efficiency_score=round(random.uniform(0.65, 0.95), 2),
                is_active=True
            )
            
            # Store base consumption for energy data generation
            building._base_consumption = template["base_consumption"]
            
            self.session.add(building)
            self.buildings.append(building)
            
            console.print(f"  🏢 Created: {building.name} ({building.type})")
        
        await self.session.commit()
        console.print(f"[green]✅ Created {num_buildings} buildings[/green]")

    def _generate_building_template(self, building_type: str, index: int) -> Dict:
        """Generate building template for additional buildings."""
        type_configs = {
            "office": {
                "size_range": (30000, 100000),
                "floors_range": (5, 20),
                "consumption_base": 250
            },
            "retail": {
                "size_range": (50000, 150000),
                "floors_range": (2, 6),
                "consumption_base": 400
            },
            "warehouse": {
                "size_range": (100000, 300000),
                "floors_range": (1, 3),
                "consumption_base": 150
            },
            "hospital": {
                "size_range": (80000, 200000),
                "floors_range": (4, 12),
                "consumption_base": 600
            },
            "school": {
                "size_range": (25000, 80000),
                "floors_range": (2, 5),
                "consumption_base": 100
            },
            "hotel": {
                "size_range": (40000, 120000),
                "floors_range": (3, 15),
                "consumption_base": 350
            }
        }
        
        config = type_configs[building_type]
        
        return {
            "name": f"{building_type.title()} Building {index + 1}",
            "type": building_type,
            "address": fake.address(),
            "size_sqft": random.randint(*config["size_range"]),
            "floors": random.randint(*config["floors_range"]),
            "year_built": random.randint(1990, 2024),
            "base_consumption": config["consumption_base"]
        }

    async def generate_energy_data(self, num_days: int):
        """Generate realistic energy consumption data."""
        console.print(f"\n[cyan]⚡ Generating {num_days} days of energy data...[/cyan]")
        
        total_data_points = len(self.buildings) * num_days * 24
        console.print(f"  📊 Total data points to generate: {total_data_points:,}")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=num_days)
        
        all_energy_data = []
        
        for building in track(self.buildings, description="🏢 Processing buildings..."):
            building_data = await self._generate_building_energy_data(
                building, start_date, end_date
            )
            all_energy_data.extend(building_data)
        
        # Batch insert for performance
        console.print("  💾 Inserting data into database...")
        self.session.add_all(all_energy_data)
        await self.session.commit()
        
        console.print(f"[green]✅ Generated {len(all_energy_data):,} energy data points[/green]")

    async def _generate_building_energy_data(
        self, building: Building, start_date: datetime, end_date: datetime
    ) -> List[EnergyData]:
        """Generate energy data for a specific building."""
        data_points = []
        base_consumption = getattr(building, '_base_consumption', 250)
        
        current_date = start_date
        while current_date < end_date:
            for hour in range(24):
                timestamp = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                # Generate realistic patterns
                consumption = self._calculate_realistic_consumption(
                    base_consumption, building.type, hour, timestamp
                )
                
                # Environmental factors
                temperature = self._calculate_temperature(hour, timestamp)
                humidity = self._calculate_humidity(hour, timestamp)
                occupancy = self._calculate_occupancy(building.type, hour, timestamp)
                
                # Cost calculation (EUR per kWh)
                cost_per_kwh = self._calculate_energy_cost(hour, timestamp)
                cost = consumption * cost_per_kwh
                
                # Power factor and demand
                power_factor = random.uniform(0.85, 0.98)
                demand_kw = consumption / power_factor
                
                energy_data = EnergyData(
                    building_id=building.id,
                    timestamp=timestamp,
                    energy_consumption=round(consumption, 2),
                    temperature=round(temperature, 1),
                    humidity=round(humidity, 1),
                    occupancy=round(occupancy, 1),
                    cost=round(cost, 2),
                    power_factor=round(power_factor, 3),
                    demand_kw=round(demand_kw, 2)
                )
                
                data_points.append(energy_data)
            
            current_date += timedelta(days=1)
        
        return data_points

    def _calculate_realistic_consumption(
        self, base_consumption: float, building_type: str, hour: int, timestamp: datetime
    ) -> float:
        """Calculate realistic energy consumption with patterns."""
        
        # Base consumption multipliers by hour for different building types
        hourly_patterns = {
            "office": {
                6: 0.4, 7: 0.6, 8: 0.8, 9: 1.0, 10: 1.0, 11: 1.0, 12: 0.9,
                13: 1.0, 14: 1.0, 15: 1.0, 16: 1.0, 17: 0.8, 18: 0.6, 19: 0.4,
                20: 0.3, 21: 0.2, 22: 0.2, 23: 0.2, 0: 0.2, 1: 0.2, 2: 0.2,
                3: 0.2, 4: 0.2, 5: 0.3
            },
            "retail": {
                8: 0.6, 9: 0.8, 10: 1.0, 11: 1.0, 12: 1.0, 13: 1.0, 14: 1.0,
                15: 1.0, 16: 1.0, 17: 1.0, 18: 1.0, 19: 1.0, 20: 0.8, 21: 0.6,
                22: 0.3, 23: 0.2, 0: 0.2, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2,
                5: 0.2, 6: 0.3, 7: 0.4
            },
            "warehouse": {
                6: 0.8, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 11: 1.0, 12: 0.9,
                13: 1.0, 14: 1.0, 15: 1.0, 16: 1.0, 17: 1.0, 18: 0.8, 19: 0.6,
                20: 0.4, 21: 0.3, 22: 0.3, 23: 0.3, 0: 0.3, 1: 0.3, 2: 0.3,
                3: 0.3, 4: 0.3, 5: 0.6
            },
            "hospital": {
                # Hospitals have consistent high usage 24/7
                **{h: random.uniform(0.85, 1.0) for h in range(24)}
            },
            "school": {
                6: 0.3, 7: 0.5, 8: 0.8, 9: 1.0, 10: 1.0, 11: 1.0, 12: 0.8,
                13: 1.0, 14: 1.0, 15: 1.0, 16: 0.8, 17: 0.5, 18: 0.3, 19: 0.2,
                20: 0.2, 21: 0.2, 22: 0.2, 23: 0.2, 0: 0.2, 1: 0.2, 2: 0.2,
                3: 0.2, 4: 0.2, 5: 0.2
            },
            "hotel": {
                6: 0.6, 7: 0.7, 8: 0.8, 9: 0.9, 10: 0.9, 11: 0.9, 12: 0.9,
                13: 0.9, 14: 0.9, 15: 0.9, 16: 0.9, 17: 0.9, 18: 1.0, 19: 1.0,
                20: 1.0, 21: 1.0, 22: 0.9, 23: 0.8, 0: 0.7, 1: 0.6, 2: 0.6,
                3: 0.6, 4: 0.6, 5: 0.6
            }
        }
        
        # Get hourly multiplier
        pattern = hourly_patterns.get(building_type, hourly_patterns["office"])
        hourly_multiplier = pattern.get(hour, 0.5)
        
        # Weekend reduction for non-24/7 buildings
        is_weekend = timestamp.weekday() >= 5
        weekend_multiplier = 0.3 if is_weekend and building_type in ["office", "school"] else 1.0
        
        # Seasonal variations
        month = timestamp.month
        seasonal_multiplier = self._get_seasonal_multiplier(month)
        
        # Random variation (±10%)
        random_variation = random.uniform(0.9, 1.1)
        
        # Calculate final consumption
        consumption = (
            base_consumption * 
            hourly_multiplier * 
            weekend_multiplier * 
            seasonal_multiplier * 
            random_variation
        )
        
        return max(consumption, 10)  # Minimum 10 kWh

    def _get_seasonal_multiplier(self, month: int) -> float:
        """Get seasonal energy consumption multiplier."""
        # Higher consumption in winter (heating) and summer (cooling)
        seasonal_multipliers = {
            1: 1.4,   # January - winter heating
            2: 1.3,   # February 
            3: 1.1,   # March - transition
            4: 0.9,   # April - mild weather
            5: 0.8,   # May
            6: 1.0,   # June - AC starts
            7: 1.3,   # July - peak summer cooling
            8: 1.3,   # August - peak summer cooling
            9: 1.0,   # September - AC reduces
            10: 0.9,  # October - mild weather
            11: 1.1,  # November - heating starts
            12: 1.4   # December - winter heating
        }
        return seasonal_multipliers.get(month, 1.0)

    def _calculate_temperature(self, hour: int, timestamp: datetime) -> float:
        """Calculate realistic building temperature."""
        # Base temperature varies by season
        month = timestamp.month
        base_temps = {
            1: 20, 2: 20, 3: 21, 4: 22, 5: 23, 6: 24,
            7: 24, 8: 24, 9: 23, 10: 22, 11: 21, 12: 20
        }
        base_temp = base_temps.get(month, 22)
        
        # Daily temperature variation
        daily_variation = 2 * random.sin((hour - 6) * 3.14159 / 12)
        
        # Random variation
        random_variation = random.uniform(-1, 1)
        
        return base_temp + daily_variation + random_variation

    def _calculate_humidity(self, hour: int, timestamp: datetime) -> float:
        """Calculate realistic building humidity."""
        # Base humidity varies by season
        month = timestamp.month
        base_humidity = 40 + 10 * random.sin(month * 3.14159 / 6)
        
        # Daily variation (higher at night)
        daily_variation = 5 * random.sin((hour + 6) * 3.14159 / 12)
        
        # Random variation
        random_variation = random.uniform(-5, 5)
        
        humidity = base_humidity + daily_variation + random_variation
        return max(30, min(70, humidity))

    def _calculate_occupancy(self, building_type: str, hour: int, timestamp: datetime) -> float:
        """Calculate realistic building occupancy."""
        # Different occupancy patterns by building type
        occupancy_patterns = {
            "office": {
                6: 5, 7: 15, 8: 60, 9: 90, 10: 95, 11: 95, 12: 80,
                13: 95, 14: 95, 15: 95, 16: 90, 17: 70, 18: 40, 19: 20,
                20: 10, 21: 5, 22: 5, 23: 5, 0: 5, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5
            },
            "retail": {
                8: 20, 9: 40, 10: 70, 11: 80, 12: 85, 13: 85, 14: 85,
                15: 85, 16: 85, 17: 90, 18: 95, 19: 90, 20: 70, 21: 40,
                22: 20, 23: 10, 0: 5, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 10
            },
            "hospital": {
                **{h: random.uniform(70, 95) for h in range(24)}  # 24/7 operation
            },
            "school": {
                7: 10, 8: 60, 9: 90, 10: 95, 11: 95, 12: 85, 13: 95,
                14: 95, 15: 95, 16: 90, 17: 70, 18: 30, 19: 10, 20: 5,
                21: 5, 22: 5, 23: 5, 0: 5, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5
            }
        }
        
        pattern = occupancy_patterns.get(building_type, occupancy_patterns["office"])
        base_occupancy = pattern.get(hour, 50)
        
        # Weekend reduction for applicable buildings
        is_weekend = timestamp.weekday() >= 5
        if is_weekend and building_type in ["office", "school"]:
            base_occupancy *= 0.2
        
        # Random variation
        variation = random.uniform(0.8, 1.2)
        
        return max(0, min(100, base_occupancy * variation))

    def _calculate_energy_cost(self, hour: int, timestamp: datetime) -> float:
        """Calculate realistic energy cost per kWh."""
        # Base cost in EUR per kWh
        base_cost = 0.15
        
        # Time-of-use pricing (peak hours cost more)
        peak_hours = [17, 18, 19, 20]  # Evening peak
        morning_peak = [7, 8, 9]       # Morning peak
        
        if hour in peak_hours:
            multiplier = 1.5  # Peak pricing
        elif hour in morning_peak:
            multiplier = 1.2  # Shoulder pricing
        elif hour in [22, 23, 0, 1, 2, 3, 4, 5]:
            multiplier = 0.8  # Off-peak pricing
        else:
            multiplier = 1.0  # Standard pricing
        
        # Weekend discount
        is_weekend = timestamp.weekday() >= 5
        if is_weekend:
            multiplier *= 0.9
        
        # Seasonal variation
        month = timestamp.month
        if month in [12, 1, 2, 6, 7, 8]:  # Winter and summer
            multiplier *= 1.1
        
        # Random market variation
        market_variation = random.uniform(0.95, 1.05)
        
        return round(base_cost * multiplier * market_variation, 4)

    async def create_optimization_jobs(self):
        """Create sample optimization jobs."""
        console.print("\n[cyan]🤖 Creating optimization jobs...[/cyan]")
        
        algorithms = ["xgboost", "lightgbm", "random_forest"]
        statuses = ["completed", "running", "pending", "failed"]
        
        for building in self.buildings[:3]:  # Create jobs for first 3 buildings
            for i in range(random.randint(1, 3)):
                algorithm = random.choice(algorithms)
                status = random.choice(statuses)
                
                # Generate realistic results for completed jobs
                if status == "completed":
                    energy_savings = round(random.uniform(15, 35), 1)
                    cost_savings = round(random.uniform(5000, 25000), 2)
                    carbon_reduction = round(random.uniform(5, 20), 1)
                    confidence = round(random.uniform(0.85, 0.98), 3)
                    
                    recommendations = self._generate_recommendations(building.type)
                    completed_at = datetime.now() - timedelta(days=random.randint(1, 7))
                else:
                    energy_savings = None
                    cost_savings = None
                    carbon_reduction = None
                    confidence = None
                    recommendations = None
                    completed_at = None
                
                optimization_job = OptimizationJob(
                    building_id=building.id,
                    algorithm=algorithm,
                    status=status,
                    energy_savings_percent=energy_savings,
                    cost_savings_annual=cost_savings,
                    carbon_reduction_tons=carbon_reduction,
                    confidence_score=confidence,
                    recommendations=recommendations,
                    completed_at=completed_at,
                    error_message="Insufficient data" if status == "failed" else None
                )
                
                self.session.add(optimization_job)
                console.print(f"  🤖 Created optimization job: {algorithm} for {building.name} ({status})")
        
        await self.session.commit()
        console.print("[green]✅ Created optimization jobs[/green]")

    def _generate_recommendations(self, building_type: str) -> List[str]:
        """Generate realistic optimization recommendations."""
        base_recommendations = [
            "Optimize HVAC scheduling based on occupancy patterns",
            "Implement smart lighting controls with motion sensors",
            "Upgrade to high-efficiency LED lighting systems",
            "Install programmable thermostats in all zones",
            "Optimize equipment runtime schedules",
            "Implement demand response automation",
            "Upgrade to variable frequency drives for motors",
            "Install smart power strips to reduce phantom loads",
        ]
        
        type_specific = {
            "office": [
                "Implement workspace hoteling to reduce conditioned space",
                "Optimize elevator scheduling during peak hours",
                "Install smart window blinds for solar heat gain control",
            ],
            "retail": [
                "Optimize refrigeration case scheduling",
                "Implement smart signage controls",
                "Install daylight harvesting controls",
            ],
            "warehouse": [
                "Optimize conveyor belt scheduling",
                "Implement smart ventilation controls",
                "Install high-bay LED lighting with controls",
            ],
            "hospital": [
                "Optimize medical equipment scheduling",
                "Implement smart isolation room controls",
                "Install energy recovery ventilation",
            ],
            "school": [
                "Implement classroom scheduling optimization",
                "Install smart gymnasium controls",
                "Optimize kitchen equipment scheduling",
            ],
            "hotel": [
                "Implement guest room occupancy controls",
                "Optimize pool and spa equipment scheduling",
                "Install smart laundry room controls",
            ]
        }
        
        # Select random recommendations
        all_recommendations = base_recommendations + type_specific.get(building_type, [])
        return random.sample(all_recommendations, k=random.randint(3, 6))

    async def generate_advanced_scenarios(self):
        """Generate advanced test scenarios."""
        console.print("\n[cyan]🎯 Generating advanced test scenarios...[/cyan]")
        
        # Scenario 1: Peak demand event
        await self._create_peak_demand_scenario()
        
        # Scenario 2: Equipment failure simulation
        await self._create_equipment_failure_scenario()
        
        # Scenario 3: Optimization success story
        await self._create_optimization_success_scenario()
        
        console.print("[green]✅ Advanced scenarios created[/green]")

    async def _create_peak_demand_scenario(self):
        """Create peak demand event scenario."""
        building = random.choice(self.buildings)
        base_consumption = getattr(building, '_base_consumption', 250)
        
        # Create spike in consumption
        for hour_offset in range(3):
            timestamp = datetime.now() - timedelta(hours=hour_offset)
            spike_consumption = base_consumption * random.uniform(2.0, 3.5)
            
            energy_data = EnergyData(
                building_id=building.id,
                timestamp=timestamp,
                energy_consumption=spike_consumption,
                temperature=28.5,  # High temperature causing AC overuse
                humidity=65.0,
                occupancy=95.0,
                cost=spike_consumption * 0.25,  # Peak pricing
                power_factor=0.75,  # Poor power factor during peak
                demand_kw=spike_consumption / 0.75
            )
            self.session.add(energy_data)
        
        console.print(f"  ⚡ Peak demand scenario created for {building.name}")

    async def _create_equipment_failure_scenario(self):
        """Create equipment failure scenario."""
        building = random.choice(self.buildings)
        base_consumption = getattr(building, '_base_consumption', 250)
        
        # Simulate equipment failure with erratic consumption
        for hour_offset in range(6):
            timestamp = datetime.now() - timedelta(hours=hour_offset)
            failure_consumption = base_consumption * random.uniform(0.3, 1.8)
            
            energy_data = EnergyData(
                building_id=building.id,
                timestamp=timestamp,
                energy_consumption=failure_consumption,
                temperature=random.uniform(16, 30),  # Erratic temperature
                humidity=random.uniform(30, 80),     # Erratic humidity
                occupancy=70.0,
                cost=failure_consumption * 0.18,
                power_factor=random.uniform(0.6, 0.9),  # Poor power factor
                demand_kw=failure_consumption / random.uniform(0.6, 0.9)
            )
            self.session.add(energy_data)
        
        console.print(f"  🔧 Equipment failure scenario created for {building.name}")

    async def _create_optimization_success_scenario(self):
        """Create optimization success story."""
        building = random.choice(self.buildings)
        
        # Create a successful optimization job with great results
        optimization_job = OptimizationJob(
            building_id=building.id,
            algorithm="xgboost",
            status="completed",
            energy_savings_percent=32.5,
            cost_savings_annual=28750.00,
            carbon_reduction_tons=15.8,
            confidence_score=0.96,
            recommendations=[
                "Implemented smart HVAC scheduling - achieved 25% reduction",
                "Upgraded to LED lighting with smart controls - 15% reduction", 
                "Optimized equipment runtime schedules - 12% reduction",
                "Implemented demand response automation - 8% reduction",
                "Installed smart power management system - 5% reduction"
            ],
            completed_at=datetime.now() - timedelta(days=2)
        )
        
        self.session.add(optimization_job)
        console.print(f"  🎉 Optimization success scenario created for {building.name}")

# ================================
# 🎯 CLI Interface
# ================================

@click.command()
@click.option('--buildings', default=5, help='Number of buildings to create')
@click.option('--days', default=30, help='Number of days of energy data')
@click.option('--advanced', is_flag=True, help='Generate advanced test scenarios')
@click.option('--reset', is_flag=True, help='Reset database before seeding')
def main(buildings: int, days: int, advanced: bool, reset: bool):
    """🌱 Seed the Energy Optimizer Pro database with sample data."""
    
    async def run_seeding():
        seeder = DataSeeder()
        
        try:
            await seeder.initialize()
            
            if reset:
                console.print("[red]⚠️  Resetting database...[/red]")
                # Implementation would drop and recreate tables
                console.print("[yellow]Database reset completed[/yellow]")
            
            await seeder.seed_all(buildings, days)
            
            if advanced:
                await seeder.generate_advanced_scenarios()
            
            console.print("\n[bold green]🎉 Data seeding completed successfully![/bold green]")
            console.print(f"[cyan]📊 Generated data for {buildings} buildings over {days} days[/cyan]")
            console.print("[cyan]🔑 Login credentials:[/cyan]")
            console.print("  Admin: admin@energy-optimizer.com / admin123")
            console.print("  Analyst: analyst@energy-optimizer.com / analyst123")
            
        except Exception as e:
            console.print(f"[red]❌ Error during seeding: {e}[/red]")
            sys.exit(1)
        finally:
            await seeder.cleanup()
    
    # Run the async function
    asyncio.run(run_seeding())

if __name__ == "__main__":
    main()

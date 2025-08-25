"""
Database utilities for Building Energy Optimizer.
"""
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.sqlite import JSON
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class Building(Base):
    """Building configuration table."""
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    building_type = Column(String(50), nullable=False)
    floor_area = Column(Float, nullable=False)
    building_age = Column(Integer, nullable=False)
    insulation_level = Column(Float, nullable=False)
    hvac_efficiency = Column(Float, nullable=False)
    occupancy_max = Column(Integer, nullable=False)
    renewable_energy = Column(Boolean, default=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    energy_records = relationship("EnergyRecord", back_populates="building")
    optimization_results = relationship("OptimizationResult", back_populates="building")

class EnergyRecord(Base):
    """Energy consumption records table."""
    __tablename__ = "energy_records"
    
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    energy_consumption = Column(Float, nullable=False)
    
    # Weather data
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    solar_radiation = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)
    
    # Occupancy data
    occupancy = Column(Float, nullable=True)
    
    # Predicted values
    predicted_consumption = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    building = relationship("Building", back_populates="energy_records")

class OptimizationResult(Base):
    """Optimization results table."""
    __tablename__ = "optimization_results"
    
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    algorithm = Column(String(50), nullable=False)
    
    # Metrics
    validation_r2 = Column(Float, nullable=False)
    validation_mae = Column(Float, nullable=False)
    training_samples = Column(Integer, nullable=False)
    
    # Results
    total_consumption_kwh = Column(Float, nullable=False)
    potential_savings_kwh = Column(Float, nullable=False)
    potential_savings_percent = Column(Float, nullable=False)
    cost_savings_eur = Column(Float, nullable=False)
    
    # Detailed results as JSON
    suggestions = Column(JSON, nullable=True)
    feature_importance = Column(JSON, nullable=True)
    full_report = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    building = relationship("Building", back_populates="optimization_results")

class DatabaseManager:
    """Database management class."""
    
    def __init__(self, database_url: str = "sqlite:///building_energy.db"):
        """Initialize database connection."""
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Database initialized: {database_url}")
    
    def get_db(self) -> Session:
        """Get database session."""
        db = self.SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise
    
    def create_building(self, building_config: Dict) -> Building:
        """Create new building record."""
        db = self.get_db()
        try:
            building = Building(**building_config)
            db.add(building)
            db.commit()
            db.refresh(building)
            return building
        finally:
            db.close()
    
    def get_building(self, building_id: int) -> Optional[Building]:
        """Get building by ID."""
        db = self.get_db()
        try:
            return db.query(Building).filter(Building.id == building_id).first()
        finally:
            db.close()
    
    def get_buildings(self) -> List[Building]:
        """Get all buildings."""
        db = self.get_db()
        try:
            return db.query(Building).all()
        finally:
            db.close()
    
    def save_energy_data(self, building_id: int, data: pd.DataFrame) -> int:
        """
        Save energy consumption data to database.
        
        Args:
            building_id (int): Building ID
            data (pd.DataFrame): Energy data
            
        Returns:
            int: Number of records saved
        """
        db = self.get_db()
        try:
            records = []
            for _, row in data.iterrows():
                record = EnergyRecord(
                    building_id=building_id,
                    timestamp=row['timestamp'],
                    energy_consumption=row['energy_consumption'],
                    temperature=row.get('temperature'),
                    humidity=row.get('humidity'),
                    solar_radiation=row.get('solar_radiation'),
                    wind_speed=row.get('wind_speed'),
                    precipitation=row.get('precipitation'),
                    pressure=row.get('pressure'),
                    cloud_cover=row.get('cloud_cover'),
                    occupancy=row.get('occupancy'),
                    predicted_consumption=row.get('predicted_consumption')
                )
                records.append(record)
            
            db.add_all(records)
            db.commit()
            
            logger.info(f"Saved {len(records)} energy records for building {building_id}")
            return len(records)
            
        finally:
            db.close()
    
    def get_energy_data(self, building_id: int, 
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Get energy data for a building.
        
        Args:
            building_id (int): Building ID
            start_date (datetime): Start date filter
            end_date (datetime): End date filter
            
        Returns:
            pd.DataFrame: Energy data
        """
        db = self.get_db()
        try:
            query = db.query(EnergyRecord).filter(EnergyRecord.building_id == building_id)
            
            if start_date:
                query = query.filter(EnergyRecord.timestamp >= start_date)
            if end_date:
                query = query.filter(EnergyRecord.timestamp <= end_date)
            
            records = query.order_by(EnergyRecord.timestamp).all()
            
            # Convert to DataFrame
            data = []
            for record in records:
                data.append({
                    'timestamp': record.timestamp,
                    'energy_consumption': record.energy_consumption,
                    'temperature': record.temperature,
                    'humidity': record.humidity,
                    'solar_radiation': record.solar_radiation,
                    'wind_speed': record.wind_speed,
                    'precipitation': record.precipitation,
                    'pressure': record.pressure,
                    'cloud_cover': record.cloud_cover,
                    'occupancy': record.occupancy,
                    'predicted_consumption': record.predicted_consumption
                })
            
            return pd.DataFrame(data)
            
        finally:
            db.close()
    
    def save_optimization_result(self, building_id: int, algorithm: str,
                               metrics: Dict, report: Dict, 
                               suggestions: List[Dict],
                               feature_importance: Dict) -> OptimizationResult:
        """Save optimization results to database."""
        db = self.get_db()
        try:
            result = OptimizationResult(
                building_id=building_id,
                algorithm=algorithm,
                validation_r2=metrics['val_r2'],
                validation_mae=metrics['val_mae'],
                training_samples=metrics['training_samples'],
                total_consumption_kwh=report['summary']['total_consumption_kwh'],
                potential_savings_kwh=report['summary']['total_potential_savings_kwh'],
                potential_savings_percent=report['summary']['potential_savings_percent'],
                cost_savings_eur=report['summary']['cost_savings_estimate_eur'],
                suggestions=suggestions,
                feature_importance=feature_importance,
                full_report=report
            )
            
            db.add(result)
            db.commit()
            db.refresh(result)
            
            logger.info(f"Saved optimization result for building {building_id}")
            return result
            
        finally:
            db.close()
    
    def get_optimization_history(self, building_id: int) -> List[OptimizationResult]:
        """Get optimization history for a building."""
        db = self.get_db()
        try:
            return db.query(OptimizationResult).filter(
                OptimizationResult.building_id == building_id
            ).order_by(OptimizationResult.created_at.desc()).all()
        finally:
            db.close()
    
    def get_buildings_summary(self) -> List[Dict]:
        """Get summary of all buildings with latest optimization results."""
        db = self.get_db()
        try:
            buildings = db.query(Building).all()
            summary = []
            
            for building in buildings:
                latest_result = db.query(OptimizationResult).filter(
                    OptimizationResult.building_id == building.id
                ).order_by(OptimizationResult.created_at.desc()).first()
                
                building_summary = {
                    'id': building.id,
                    'name': building.name,
                    'building_type': building.building_type,
                    'floor_area': building.floor_area,
                    'latest_optimization': None
                }
                
                if latest_result:
                    building_summary['latest_optimization'] = {
                        'algorithm': latest_result.algorithm,
                        'potential_savings_percent': latest_result.potential_savings_percent,
                        'cost_savings_eur': latest_result.cost_savings_eur,
                        'date': latest_result.created_at.isoformat()
                    }
                
                summary.append(building_summary)
            
            return summary
            
        finally:
            db.close()

# Utility functions
def init_database(database_url: str = "sqlite:///building_energy.db") -> DatabaseManager:
    """Initialize database with sample data."""
    db_manager = DatabaseManager(database_url)
    
    # Create sample building if none exist
    db = db_manager.get_db()
    try:
        if db.query(Building).count() == 0:
            sample_building = Building(
                name="Sample Commercial Building",
                building_type="commercial",
                floor_area=2500,
                building_age=8,
                insulation_level=0.75,
                hvac_efficiency=0.85,
                occupancy_max=150,
                renewable_energy=True,
                latitude=41.9028,  # Rome
                longitude=12.4964
            )
            db.add(sample_building)
            db.commit()
            logger.info("Created sample building")
    finally:
        db.close()
    
    return db_manager

if __name__ == "__main__":
    # Demo database operations
    print("🗄️ Database Integration Demo")
    
    # Initialize database
    db_manager = init_database()
    
    # Get buildings summary
    summary = db_manager.get_buildings_summary()
    print(f"Buildings in database: {len(summary)}")
    
    for building in summary:
        print(f"- {building['name']}: {building['floor_area']}m², {building['building_type']}")

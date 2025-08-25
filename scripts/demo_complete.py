"""
Complete demonstration of Building Energy Optimizer v2.0
"""
import sys
import os
from datetime import datetime, timedelta
import json

# Add project to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from building_energy_optimizer import (
    BuildingEnergyOptimizer,
    BuildingConfig,
    create_enhanced_example_data,
    quick_optimize,
    init_database,
    WeatherIntegrator,
    OpenWeatherMapProvider
)

def demo_complete_workflow():
    """Demonstrate complete workflow with all new features."""
    
    print("🏢" + "="*60)
    print("  BUILDING ENERGY OPTIMIZER v2.0 - COMPLETE DEMO")
    print("="*62)
    
    # 1. Database Setup
    print("\n1️⃣ Setting up database...")
    db_manager = init_database()
    buildings = db_manager.get_buildings()
    
    if buildings:
        building = buildings[0]
        print(f"✅ Using existing building: {building.name}")
    else:
        print("❌ No buildings found in database")
        return
    
    # 2. Weather Integration Demo
    print("\n2️⃣ Demonstrating weather integration...")
    weather_provider = OpenWeatherMapProvider()  # Will use synthetic data without API key
    weather_integrator = WeatherIntegrator(weather_provider)
    
    current_weather = weather_provider.get_current_weather(
        building.latitude or 41.9028, 
        building.longitude or 12.4964
    )
    print(f"✅ Current weather: {current_weather.temperature:.1f}°C, {current_weather.humidity:.0f}% humidity")
    
    # 3. Generate Enhanced Dataset
    print("\n3️⃣ Generating enhanced dataset...")
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    building_config = BuildingConfig(
        building_type=building.building_type,
        floor_area=building.floor_area,
        building_age=building.building_age,
        insulation_level=building.insulation_level,
        hvac_efficiency=building.hvac_efficiency,
        occupancy_max=building.occupancy_max,
        renewable_energy=building.renewable_energy
    )
    
    data = create_enhanced_example_data(start_date, end_date, building_config)
    print(f"✅ Generated {len(data)} hourly records with {len(data.columns)} features")
    
    # 4. Save data to database
    print("\n4️⃣ Saving data to database...")
    records_saved = db_manager.save_energy_data(building.id, data)
    print(f"✅ Saved {records_saved} energy records")
    
    # 5. Algorithm Comparison
    print("\n5️⃣ Comparing ML algorithms...")
    algorithms = ['random_forest', 'xgboost', 'lightgbm']
    results = {}
    
    for algorithm in algorithms:
        print(f"\n🧠 Testing {algorithm.upper()}...")
        try:
            result = quick_optimize(data, algorithm=algorithm, building_type=building.building_type)
            results[algorithm] = result
            
            metrics = result['training_metrics']
            report = result['report']
            
            print(f"   ✅ R² Score: {metrics['val_r2']:.3f}")
            print(f"   ✅ Potential Savings: {report['summary']['potential_savings_percent']:.1f}%")
            print(f"   ✅ Cost Savings: €{report['summary']['cost_savings_estimate_eur']:.2f}")
            
            # Save results to database
            db_manager.save_optimization_result(
                building_id=building.id,
                algorithm=algorithm,
                metrics=metrics,
                report=report,
                suggestions=result['suggestions'],
                feature_importance=result['optimizer'].get_feature_importance()
            )
            
        except Exception as e:
            print(f"   ❌ {algorithm} failed: {e}")
    
    # 6. Best Algorithm Analysis
    if results:
        best_algorithm = max(results.keys(), key=lambda k: results[k]['training_metrics']['val_r2'])
        best_result = results[best_algorithm]
        
        print(f"\n6️⃣ Best performing algorithm: {best_algorithm.upper()}")
        print(f"   🎯 Validation R²: {best_result['training_metrics']['val_r2']:.3f}")
        print(f"   💰 Potential Savings: €{best_result['report']['summary']['cost_savings_estimate_eur']:.2f}")
        
        # Top suggestions
        suggestions = best_result['suggestions'][:5]
        print(f"\n   🔧 Top {len(suggestions)} Optimization Suggestions:")
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n   #{i} - {suggestion['priority'].title()} Priority")
            print(f"      💡 Savings: {suggestion['potential_savings']:.1f} kWh")
            
            for action in suggestion['suggestions'][:2]:
                print(f"      • {action['category']}: {action['action']}")
    
    # 7. Feature Importance Analysis
    if results:
        print("\n7️⃣ Feature importance analysis...")
        importance = best_result['optimizer'].get_feature_importance()
        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("   📈 Top 10 most important features:")
        for feature, score in top_features:
            print(f"      {feature}: {score:.3f}")
    
    # 8. Export Complete Report
    print("\n8️⃣ Exporting comprehensive report...")
    
    comprehensive_report = {
        'building_info': {
            'id': building.id,
            'name': building.name,
            'config': building_config.__dict__
        },
        'analysis_period': {
            'start_date': start_date,
            'end_date': end_date,
            'total_hours': len(data)
        },
        'algorithm_comparison': {
            alg: {
                'metrics': res['training_metrics'],
                'savings_percent': res['report']['summary']['potential_savings_percent'],
                'cost_savings': res['report']['summary']['cost_savings_estimate_eur']
            }
            for alg, res in results.items()
        },
        'best_algorithm': best_algorithm,
        'detailed_results': best_result['report'] if results else {},
        'optimization_suggestions': suggestions if results else [],
        'feature_importance': dict(top_features) if results else {},
        'generated_at': datetime.now().isoformat()
    }
    
    # Save to file
    report_filename = f"complete_energy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(comprehensive_report, f, indent=2, default=str)
    
    print(f"✅ Complete report saved to: {report_filename}")
    
    # 9. Usage Instructions
    print("\n9️⃣ Next Steps:")
    print("   🌐 Start API: python scripts/start_api.py")
    print("   📊 Start Dashboard: python scripts/start_dashboard.py")
    print("   🧪 Run Tests: pytest tests/")
    print("   📄 View API Docs: http://localhost:8000/docs")
    print("   📱 View Dashboard: http://localhost:8501")
    
    print("\n🎉 Complete demonstration finished!")
    print("   Your building energy optimizer is ready for production use!")

if __name__ == "__main__":
    demo_complete_workflow()

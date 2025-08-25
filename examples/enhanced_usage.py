"""
Enhanced example showing advanced Building Energy Optimizer capabilities.
"""
from src.building_energy_optimizer.optimizer import (
    BuildingEnergyOptimizer, 
    BuildingConfig, 
    create_enhanced_example_data,
    quick_optimize
)
from datetime import datetime, timedelta
import json

def main():
    """Enhanced example demonstrating new features."""
    
    print("🏢 Building Energy Optimizer v2.0 - Enhanced Demo")
    print("=" * 60)
    
    # 1. Create building configuration
    print("\n1️⃣ Creating building configuration...")
    building_config = BuildingConfig(
        building_type='commercial',
        floor_area=2500,  # m²
        building_age=8,   # years
        insulation_level=0.75,  # Good insulation
        hvac_efficiency=0.85,   # Efficient HVAC
        occupancy_max=150,      # max people
        renewable_energy=True   # Has solar panels
    )
    print(f"✅ Configuration: {building_config.building_type} building, {building_config.floor_area}m²")
    
    # 2. Generate realistic data
    print("\n2️⃣ Generating enhanced dataset...")
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    data = create_enhanced_example_data(start_date, end_date, building_config)
    print(f"✅ Generated {len(data)} hourly records with {len(data.columns)} features")
    print(f"   Features: {', '.join(data.columns[:8])}...")
    
    # 3. Compare different algorithms
    algorithms = ['random_forest', 'xgboost', 'lightgbm']
    results = {}
    
    print("\n3️⃣ Testing multiple ML algorithms...")
    for algorithm in algorithms:
        print(f"\n🧠 Training {algorithm.upper()}...")
        try:
            optimizer = BuildingEnergyOptimizer(
                algorithm=algorithm, 
                building_config=building_config
            )
            
            # Preprocess and train
            X_scaled, y = optimizer.preprocess_data(data.copy())
            metrics = optimizer.train(X_scaled, y)
            
            # Generate predictions and suggestions
            predictions, suggestions = optimizer.predict(X_scaled)
            
            results[algorithm] = {
                'optimizer': optimizer,
                'metrics': metrics,
                'predictions': predictions,
                'suggestions': suggestions
            }
            
            print(f"   ✅ R² Score: {metrics['val_r2']:.3f}")
            print(f"   ✅ Validation MAE: {metrics['val_mae']:.2f} kWh")
            print(f"   ✅ Generated {len(suggestions)} optimization suggestions")
            
        except Exception as e:
            print(f"   ❌ {algorithm} failed: {e}")
            continue
    
    # 4. Use best performing algorithm
    best_algorithm = max(results.keys(), key=lambda k: results[k]['metrics']['val_r2'])
    best_optimizer = results[best_algorithm]['optimizer']
    best_predictions = results[best_algorithm]['predictions']
    best_suggestions = results[best_algorithm]['suggestions']
    
    print(f"\n4️⃣ Best algorithm: {best_algorithm.upper()}")
    
    # 5. Generate comprehensive report
    print("\n5️⃣ Generating comprehensive energy report...")
    report = best_optimizer.generate_energy_report(data, best_predictions, best_suggestions)
    
    print("\n📊 ENERGY CONSUMPTION SUMMARY:")
    summary = report['summary']
    print(f"   Total Consumption: {summary['total_consumption_kwh']:.1f} kWh")
    print(f"   Average Hourly: {summary['average_hourly_consumption_kwh']:.1f} kWh")
    print(f"   Peak Consumption: {summary['peak_consumption_kwh']:.1f} kWh")
    print(f"   Potential Savings: {summary['total_potential_savings_kwh']:.1f} kWh ({summary['potential_savings_percent']:.1f}%)")
    print(f"   Cost Savings: €{summary['cost_savings_estimate_eur']:.2f}")
    
    # 6. Show feature importance
    print("\n6️⃣ Most important features:")
    feature_importance = best_optimizer.get_feature_importance()
    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:8]
    
    for feature, importance in top_features:
        print(f"   📈 {feature}: {importance:.3f}")
    
    # 7. Show top optimization suggestions
    print("\n7️⃣ TOP OPTIMIZATION SUGGESTIONS:")
    for i, suggestion in enumerate(best_suggestions[:3], 1):
        print(f"\n   🔧 Suggestion #{i} (Priority: {suggestion['priority'].upper()})")
        print(f"      Current consumption: {suggestion['current_consumption']:.1f} kWh")
        print(f"      Potential savings: {suggestion['potential_savings']:.1f} kWh")
        
        for action in suggestion['suggestions'][:2]:  # Show top 2 actions
            print(f"      • {action['category']}: {action['action']}")
            print(f"        💰 Savings: {action['estimated_savings_kwh']} kWh ({action['estimated_savings_percent']})")
    
    # 8. Show suggestions by category
    print("\n8️⃣ SUGGESTIONS BY CATEGORY:")
    categories = report['suggestions_by_category']
    for category, actions in categories.items():
        print(f"   🏷️ {category}: {len(actions)} suggestions")
    
    # 9. Save enhanced model
    print("\n9️⃣ Saving enhanced model...")
    model_path = f"enhanced_model_{best_algorithm}.joblib"
    best_optimizer.save_model(model_path)
    print(f"✅ Model saved as: {model_path}")
    
    # 10. Export report to JSON
    print("\n🔟 Exporting detailed report...")
    # Convert numpy arrays to lists for JSON serialization
    json_report = report.copy()
    json_report['predictions'] = best_predictions.tolist()
    json_report['raw_suggestions'] = best_suggestions
    
    with open('energy_optimization_report.json', 'w') as f:
        json.dump(json_report, f, indent=2, default=str)
    print("✅ Report exported to: energy_optimization_report.json")
    
    print("\n🎉 Enhanced optimization complete!")
    print("Next steps: Implement web dashboard and real-time monitoring")

def demo_quick_optimize():
    """Demonstrate the quick_optimize convenience function."""
    print("\n" + "="*50)
    print("🚀 QUICK OPTIMIZE DEMO")
    print("="*50)
    
    # Generate sample data
    data = create_enhanced_example_data('2024-12-01', '2024-12-07')
    
    # Quick optimization
    result = quick_optimize(data, algorithm='xgboost', building_type='commercial')
    
    report = result['report']
    print(f"\n💡 Quick Optimization Results:")
    print(f"   Algorithm: XGBoost")
    print(f"   R² Score: {result['training_metrics']['val_r2']:.3f}")
    print(f"   Potential Savings: {report['summary']['potential_savings_percent']:.1f}%")
    print(f"   Cost Savings: €{report['summary']['cost_savings_estimate_eur']:.2f}")

if __name__ == "__main__":
    main()
    demo_quick_optimize()

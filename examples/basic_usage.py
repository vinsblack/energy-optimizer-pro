from src.building_energy_optimizer.optimizer import BuildingEnergyOptimizer, create_example_data
from datetime import datetime, timedelta

def main():
    """Example of how to use the Building Energy Optimizer."""
    
    # Initialize the optimizer
    optimizer = BuildingEnergyOptimizer()
    
    # Create sample data (in real use, you would load your own data)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)  # One month of data
    data = create_example_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Preprocess the data
    print("Preprocessing data...")
    X_scaled, y = optimizer.preprocess_data(data)
    
    # Train the model
    print("\nTraining model...")
    optimizer.train(X_scaled, y)
    
    # Make predictions and get optimization suggestions
    print("\nGenerating predictions and suggestions...")
    predictions, suggestions = optimizer.predict(X_scaled)
    
    # Print some statistics
    print(f"\nAverage predicted consumption: {predictions.mean():.2f} kWh")
    print(f"Number of optimization suggestions: {len(suggestions)}")
    
    # Print some example suggestions
    print("\nExample optimization suggestions:")
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"\nSuggestion {i}:")
        print(f"Timestamp: {data['timestamp'].iloc[suggestion['timestamp']]}")
        print(f"Current consumption: {suggestion['current_consumption']:.2f} kWh")
        for action in suggestion['suggestions']:
            print(f"- {action['type']}: {action['action']}")
            print(f"  Estimated savings: {action['estimated_savings']}")
    
    # Save the trained model
    print("\nSaving model...")
    optimizer.save_model("trained_model.joblib")
    print("Model saved successfully!")

if __name__ == "__main__":
    main()
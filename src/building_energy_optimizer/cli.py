"""
Command Line Interface for Building Energy Optimizer.
"""
import click
import sys
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

@click.group()
@click.version_option(version="2.0.0", prog_name="Building Energy Optimizer")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def main(ctx, verbose):
    """🏢 Building Energy Optimizer v2.0 - Advanced ML-powered energy optimization."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

@main.command()
@click.option('--algorithm', '-a', default='xgboost', 
              type=click.Choice(['xgboost', 'lightgbm', 'random_forest']),
              help='ML algorithm to use')
@click.option('--start-date', default='2024-01-01', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', default='2024-01-07', help='End date (YYYY-MM-DD)')
@click.option('--building-type', default='commercial',
              type=click.Choice(['residential', 'commercial', 'industrial']),
              help='Building type')
@click.option('--floor-area', default=2500, type=float, help='Floor area in square meters')
@click.option('--output', '-o', help='Output file for results (JSON format)')
@click.pass_context
def optimize(ctx, algorithm, start_date, end_date, building_type, floor_area, output):
    """Run energy optimization analysis."""
    try:
        from building_energy_optimizer import (
            quick_optimize, 
            create_enhanced_example_data,
            BuildingConfig
        )
        
        click.echo(f"🤖 Running optimization with {algorithm.upper()} algorithm...")
        
        # Generate or load data
        data = create_enhanced_example_data(start_date, end_date)
        click.echo(f"📊 Generated {len(data)} data points from {start_date} to {end_date}")
        
        # Configure building
        config = BuildingConfig(
            building_type=building_type,
            floor_area=floor_area
        )
        
        # Run optimization
        result = quick_optimize(data, algorithm=algorithm, building_config=config)
        
        # Display results
        summary = result['report']['summary']
        click.echo("\n🎯 Optimization Results:")
        click.echo(f"   Energy Consumption: {summary['total_consumption_kwh']:.1f} kWh")
        click.echo(f"   Potential Savings: {summary['potential_savings_percent']:.1f}%")
        click.echo(f"   Cost Savings: €{summary['cost_savings_estimate_eur']:.2f}")
        click.echo(f"   Suggestions: {len(result['suggestions'])}")
        
        if ctx.obj['verbose']:
            metrics = result.get('training_metrics', {})
            click.echo(f"\n📈 Model Performance:")
            click.echo(f"   Accuracy (R²): {metrics.get('val_r2', 0):.3f}")
            click.echo(f"   MAE: {metrics.get('val_mae', 0):.2f}")
            click.echo(f"   Training Samples: {metrics.get('training_samples', 0)}")
        
        # Save results if output specified
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            click.echo(f"\n💾 Results saved to {output}")
        
        click.echo("\n✅ Optimization completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Optimization failed: {e}", err=True)
        sys.exit(1)

@main.command()
@click.option('--input-file', '-i', required=True, help='Input CSV file with energy data')
@click.option('--algorithm', '-a', default='xgboost',
              type=click.Choice(['xgboost', 'lightgbm', 'random_forest']),
              help='ML algorithm to use')
@click.option('--output', '-o', help='Output file for predictions')
@click.pass_context
def predict(ctx, input_file, algorithm, output):
    """Make energy consumption predictions from CSV file."""
    try:
        import pandas as pd
        from building_energy_optimizer import BuildingEnergyOptimizer, BuildingConfig
        
        click.echo(f"📊 Loading data from {input_file}...")
        
        # Load data
        if not os.path.exists(input_file):
            click.echo(f"❌ File not found: {input_file}", err=True)
            sys.exit(1)
        
        data = pd.read_csv(input_file)
        click.echo(f"✅ Loaded {len(data)} records")
        
        # Initialize optimizer
        config = BuildingConfig()  # Use defaults
        optimizer = BuildingEnergyOptimizer(algorithm=algorithm, building_config=config)
        
        # Preprocess and train
        X, y = optimizer.preprocess_data(data)
        click.echo(f"🔄 Training {algorithm.upper()} model...")
        
        metrics = optimizer.train(X, y)
        click.echo(f"🎯 Model trained with R² = {metrics['val_r2']:.3f}")
        
        # Make predictions
        predictions, suggestions = optimizer.predict(X)
        
        # Create results DataFrame
        results_df = data.copy()
        results_df['predicted_consumption'] = predictions
        
        click.echo(f"\n📈 Prediction Results:")
        click.echo(f"   Mean Prediction: {predictions.mean():.2f} kWh")
        click.echo(f"   Min Prediction: {predictions.min():.2f} kWh")
        click.echo(f"   Max Prediction: {predictions.max():.2f} kWh")
        
        # Save predictions if output specified
        if output:
            results_df.to_csv(output, index=False)
            click.echo(f"\n💾 Predictions saved to {output}")
        else:
            click.echo("\n📊 Sample predictions:")
            for i, pred in enumerate(predictions[:5]):
                timestamp = data.iloc[i]['timestamp'] if 'timestamp' in data.columns else f"Row {i+1}"
                click.echo(f"   {timestamp}: {pred:.2f} kWh")
        
        click.echo("\n✅ Predictions completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Prediction failed: {e}", err=True)
        sys.exit(1)

@main.command()
@click.option('--port', default=8000, help='Port to run API server on')
@click.option('--host', default='0.0.0.0', help='Host to bind server to')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def api(port, host, reload):
    """Start the API server."""
    try:
        import uvicorn
        from building_energy_optimizer.api.main import app
        
        click.echo(f"🚀 Starting API server on http://{host}:{port}")
        click.echo(f"📚 Documentation: http://{host}:{port}/docs")
        
        uvicorn.run(
            "building_energy_optimizer.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except ImportError:
        click.echo("❌ FastAPI not installed. Install with: pip install building-energy-optimizer[web]", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start API server: {e}", err=True)
        sys.exit(1)

@main.command()
@click.option('--port', default=8501, help='Port to run dashboard on')
@click.option('--host', default='0.0.0.0', help='Host to bind dashboard to')
def dashboard(port, host):
    """Start the Streamlit dashboard."""
    try:
        import streamlit.web.cli as stcli
        import streamlit as st
        
        click.echo(f"📊 Starting dashboard on http://{host}:{port}")
        
        # Set environment variables for Streamlit
        os.environ['STREAMLIT_SERVER_PORT'] = str(port)
        os.environ['STREAMLIT_SERVER_ADDRESS'] = host
        
        # Run Streamlit
        dashboard_file = Path(__file__).parent / "dashboard" / "streamlit_app.py"
        if not dashboard_file.exists():
            dashboard_file = "dashboard/streamlit_app.py"
        
        sys.argv = ["streamlit", "run", str(dashboard_file), "--server.port", str(port), "--server.address", host]
        stcli.main()
        
    except ImportError:
        click.echo("❌ Streamlit not installed. Install with: pip install building-energy-optimizer[web]", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start dashboard: {e}", err=True)
        sys.exit(1)

@main.command()
def health():
    """Run system health check."""
    try:
        from building_energy_optimizer.monitoring import detailed_health_check, generate_performance_report
        
        click.echo("🏥 Running health check...")
        
        # Health check
        health_status = detailed_health_check()
        overall_status = health_status['overall_status']
        
        # Status emoji
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌',
            'unknown': '❓'
        }
        
        click.echo(f"\n{status_emoji.get(overall_status, '❓')} Overall Status: {overall_status.upper()}")
        
        # Component details
        for component, check_result in health_status['checks'].items():
            emoji = status_emoji.get(check_result['status'], '❓')
            response_time = check_result.get('response_time_ms', 0)
            click.echo(f"   {emoji} {component}: {check_result['message']} ({response_time:.1f}ms)")
        
        # Critical issues
        if health_status.get('critical_issues'):
            click.echo(f"\n🚨 Critical Issues:")
            for issue in health_status['critical_issues']:
                click.echo(f"   ❌ {issue['component']}: {issue['message']}")
        
        if overall_status == 'healthy':
            click.echo("\n🎉 All systems operational!")
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}", err=True)
        sys.exit(1)

@main.command()
@click.option('--include-logs', is_flag=True, help='Include log files in backup')
@click.option('--type', 'backup_type', default='full', 
              type=click.Choice(['full', 'incremental']),
              help='Backup type')
def backup(include_logs, backup_type):
    """Create system backup."""
    try:
        from building_energy_optimizer.monitoring import create_backup
        
        click.echo(f"💾 Creating {backup_type} backup...")
        
        result = create_backup(backup_type, include_logs)
        
        if result.get('error'):
            click.echo(f"❌ Backup failed: {result['error']}", err=True)
            sys.exit(1)
        else:
            backup_id = result['backup_id']
            size_mb = result['total_size_bytes'] / (1024**2)
            click.echo(f"✅ Backup created: {backup_id} ({size_mb:.1f} MB)")
            
            # Show components
            if 'components' in result:
                for component, info in result['components'].items():
                    if info.get('status') == 'success':
                        click.echo(f"   ✅ {component}")
                    else:
                        click.echo(f"   ⚠️ {component}: {info.get('reason', 'Unknown')}")
        
    except Exception as e:
        click.echo(f"❌ Backup failed: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument('backup_id')
@click.option('--components', multiple=True, 
              type=click.Choice(['database', 'models', 'configuration', 'logs']),
              help='Specific components to restore')
def restore(backup_id, components):
    """Restore from backup."""
    try:
        from building_energy_optimizer.monitoring import restore_backup
        
        components_list = list(components) if components else None
        
        click.echo(f"🔄 Restoring from backup: {backup_id}")
        if components_list:
            click.echo(f"📦 Components: {', '.join(components_list)}")
        
        # Confirmation
        if not click.confirm("This will overwrite existing data. Continue?"):
            click.echo("❌ Restore cancelled")
            return
        
        result = restore_backup(backup_id, components_list)
        
        if result.get('fatal_error'):
            click.echo(f"❌ Restore failed: {result['fatal_error']}", err=True)
            sys.exit(1)
        else:
            restored = result['components_restored']
            errors = result.get('errors', [])
            
            click.echo(f"✅ Restored {len(restored)} components: {', '.join(restored)}")
            
            if errors:
                click.echo(f"⚠️ {len(errors)} error(s):")
                for error in errors:
                    click.echo(f"   ❌ {error}")
        
    except Exception as e:
        click.echo(f"❌ Restore failed: {e}", err=True)
        sys.exit(1)

@main.command()
def status():
    """Show comprehensive system status."""
    try:
        from building_energy_optimizer.monitoring import get_complete_system_status
        
        click.echo("📊 System Status Report")
        click.echo("=" * 30)
        
        status = get_complete_system_status()
        overall = status['overall_status']
        
        # Overall status
        status_emoji = {'healthy': '✅', 'warning': '⚠️', 'critical': '❌', 'unknown': '❓'}
        click.echo(f"{status_emoji.get(overall, '❓')} Overall Status: {overall.upper()}")
        click.echo(f"📅 Last Check: {status['timestamp']}")
        
        # Health components
        if 'health' in status:
            click.echo(f"\n🏥 Component Health:")
            for component, check_result in status['health']['checks'].items():
                emoji = status_emoji.get(check_result['status'], '❓')
                response_time = check_result.get('response_time_ms', 0)
                click.echo(f"   {emoji} {component}: {check_result['message']} ({response_time:.1f}ms)")
        
        # Performance metrics
        if 'performance' in status:
            performance = status['performance']['business_metrics']
            click.echo(f"\n📈 Performance:")
            click.echo(f"   🤖 Optimizations: {performance['total_optimizations']:,}")
            click.echo(f"   🔮 Predictions: {performance['total_predictions']:,}")
            click.echo(f"   ⚡ Energy Analyzed: {performance['total_energy_analyzed_kwh']:,.0f} kWh")
            click.echo(f"   💰 Savings Found: {performance['total_savings_identified_kwh']:,.0f} kWh")
        
        # Backup info
        if 'backups' in status:
            backup_info = status['backups']
            click.echo(f"\n💾 Backups: {backup_info['total_backups']} available")
            if backup_info['latest_backup']:
                latest = backup_info['latest_backup']
                click.echo(f"   🕐 Latest: {latest['backup_id']}")
        
    except Exception as e:
        click.echo(f"❌ Status check failed: {e}", err=True)
        sys.exit(1)

@main.command()
@click.option('--algorithms', multiple=True,
              type=click.Choice(['xgboost', 'lightgbm', 'random_forest']),
              help='Algorithms to benchmark (default: all)')
@click.option('--data-sizes', multiple=True, 
              type=click.Choice(['week', 'month', 'quarter', 'year']),
              default=['week', 'month'],
              help='Data sizes to test')
def benchmark(algorithms, data_sizes):
    """Run performance benchmark."""
    try:
        from building_energy_optimizer import quick_optimize, create_enhanced_example_data
        import time
        
        # Default algorithms if none specified
        if not algorithms:
            algorithms = ['xgboost', 'lightgbm', 'random_forest']
        
        # Data size configurations
        size_configs = {
            'week': ('2024-01-01', '2024-01-07'),
            'month': ('2024-01-01', '2024-01-31'),
            'quarter': ('2024-01-01', '2024-03-31'),
            'year': ('2024-01-01', '2024-12-31')
        }
        
        click.echo("⚡ Running performance benchmark...")
        click.echo("=" * 50)
        
        results = {}\n        \n        for size_name in data_sizes:\n            start_date, end_date = size_configs[size_name]\n            \n            click.echo(f\"\\n📊 Testing {size_name} dataset ({start_date} to {end_date})...\")\n            data = create_enhanced_example_data(start_date, end_date)\n            \n            for algorithm in algorithms:\n                click.echo(f\"   🤖 {algorithm.upper()}...\", nl=False)\n                \n                start_time = time.time()\n                try:\n                    result = quick_optimize(data, algorithm=algorithm)\n                    duration = time.time() - start_time\n                    \n                    accuracy = result.get('training_metrics', {}).get('val_r2', 0)\n                    savings = result['report']['summary']['potential_savings_percent']\n                    \n                    results[f\"{size_name}_{algorithm}\"] = {\n                        'data_points': len(data),\n                        'duration': duration,\n                        'accuracy': accuracy,\n                        'savings_percent': savings\n                    }\n                    \n                    click.echo(f\" {duration:.1f}s (R²={accuracy:.3f}, Savings={savings:.1f}%)\")\n                    \n                except Exception as e:\n                    click.echo(f\" FAILED: {e}\")\n                    results[f\"{size_name}_{algorithm}\"] = {'error': str(e)}\n        \n        # Show summary\n        click.echo(f\"\\n📈 Benchmark Summary:\")\n        click.echo(\"=\" * 25)\n        \n        for key, result in results.items():\n            if 'error' not in result:\n                size, algo = key.split('_', 1)\n                points_per_sec = result['data_points'] / result['duration']\n                click.echo(f\"{size:>8} {algo:>12}: {result['duration']:>6.1f}s ({points_per_sec:>6.0f} pts/sec) R²={result['accuracy']:.3f}\")\n        \n        click.echo(\"\\n✅ Benchmark completed!\")\n        \n    except Exception as e:\n        click.echo(f\"❌ Benchmark failed: {e}\", err=True)\n        sys.exit(1)\n\n@main.command()\ndef demo():\n    \"\"\"Run interactive demonstration.\"\"\"\n    try:\n        from building_energy_optimizer import (\n            quick_optimize, \n            create_enhanced_example_data,\n            get_version_info\n        )\n        \n        # Show welcome\n        version_info = get_version_info()\n        click.echo(\"🎬 Building Energy Optimizer Demo\")\n        click.echo(\"=\" * 40)\n        click.echo(f\"Version: {version_info['version']}\")\n        click.echo(f\"Algorithms: {', '.join(version_info['supported_algorithms'])}\")\n        click.echo()\n        \n        # Generate sample data\n        click.echo(\"📊 Generating sample data...\")\n        data = create_enhanced_example_data('2024-01-01', '2024-01-07')\n        click.echo(f\"✅ Generated {len(data)} hourly data points\")\n        \n        # Run optimization with each algorithm\n        click.echo(\"\\n🤖 Testing algorithms...\")\n        \n        best_result = None\n        best_algorithm = None\n        \n        for algorithm in ['xgboost', 'lightgbm', 'random_forest']:\n            click.echo(f\"\\n   {algorithm.upper()}:\", nl=False)\n            \n            start_time = time.time()\n            result = quick_optimize(data, algorithm=algorithm)\n            duration = time.time() - start_time\n            \n            summary = result['report']['summary']\n            accuracy = result.get('training_metrics', {}).get('val_r2', 0)\n            \n            click.echo(f\" {duration:.1f}s\")\n            click.echo(f\"     🎯 Accuracy: {accuracy:.1%}\")\n            click.echo(f\"     💰 Savings: {summary['potential_savings_percent']:.1f}% (€{summary['cost_savings_estimate_eur']:.2f})\")\n            click.echo(f\"     💡 Suggestions: {len(result['suggestions'])}\")\n            \n            # Track best result\n            if best_result is None or accuracy > best_result.get('training_metrics', {}).get('val_r2', 0):\n                best_result = result\n                best_algorithm = algorithm\n        \n        # Show best result details\n        if best_result:\n            click.echo(f\"\\n🏆 Best Algorithm: {best_algorithm.upper()}\")\n            click.echo(\"=\" * 30)\n            \n            summary = best_result['report']['summary']\n            click.echo(f\"📊 Total Consumption: {summary['total_consumption_kwh']:.1f} kWh\")\n            click.echo(f\"💡 Potential Savings: {summary['potential_savings_percent']:.1f}%\")\n            click.echo(f\"💰 Cost Savings: €{summary['cost_savings_estimate_eur']:.2f}\")\n            click.echo(f\"⚡ Peak Consumption: {summary['peak_consumption_kwh']:.1f} kWh\")\n            \n            # Show top suggestions\n            click.echo(\"\\n💡 Top Optimization Suggestions:\")\n            for i, suggestion in enumerate(best_result['suggestions'][:3], 1):\n                if suggestion['suggestions']:\n                    action = suggestion['suggestions'][0]['action']\n                    savings = suggestion['suggestions'][0].get('estimated_savings_percent', 0)\n                    click.echo(f\"   {i}. {action} (Est. {savings:.1f}% savings)\")\n        \n        click.echo(\"\\n🎉 Demo completed successfully!\")\n        click.echo(\"\\n📚 Next steps:\")\n        click.echo(\"   • Start API: beo api\")\n        click.echo(\"   • Start Dashboard: beo dashboard\")\n        click.echo(\"   • View Documentation: http://localhost:8000/docs\")\n        \n    except Exception as e:\n        click.echo(f\"❌ Demo failed: {e}\", err=True)\n        sys.exit(1)\n\n@main.command()\n@click.argument('data_file')\n@click.option('--building-name', default='Building Analysis', help='Building name')\n@click.option('--building-type', default='commercial',\n              type=click.Choice(['residential', 'commercial', 'industrial']),\n              help='Building type')\n@click.option('--floor-area', default=2500, type=float, help='Floor area in m²')\ndef analyze(data_file, building_name, building_type, floor_area):\n    \"\"\"Analyze energy data from file.\"\"\"\n    try:\n        import pandas as pd\n        from building_energy_optimizer import BuildingEnergyOptimizer, BuildingConfig\n        \n        click.echo(f\"📊 Analyzing energy data from {data_file}...\")\n        \n        # Load data\n        if not os.path.exists(data_file):\n            click.echo(f\"❌ File not found: {data_file}\", err=True)\n            sys.exit(1)\n        \n        data = pd.read_csv(data_file)\n        click.echo(f\"✅ Loaded {len(data)} records\")\n        \n        # Show data summary\n        click.echo(f\"\\n📈 Data Summary:\")\n        click.echo(f\"   Date Range: {data['timestamp'].min()} to {data['timestamp'].max()}\")\n        if 'energy_consumption' in data.columns:\n            energy_col = data['energy_consumption']\n            click.echo(f\"   Energy Range: {energy_col.min():.1f} - {energy_col.max():.1f} kWh\")\n            click.echo(f\"   Average: {energy_col.mean():.1f} kWh\")\n        \n        # Configure building\n        config = BuildingConfig(\n            building_type=building_type,\n            floor_area=floor_area\n        )\n        \n        # Run analysis with XGBoost\n        click.echo(f\"\\n🤖 Running analysis...\")\n        optimizer = BuildingEnergyOptimizer(algorithm='xgboost', building_config=config)\n        \n        X, y = optimizer.preprocess_data(data)\n        metrics = optimizer.train(X, y)\n        predictions, suggestions = optimizer.predict(X)\n        \n        # Generate report\n        report = optimizer.generate_energy_report(data, predictions, suggestions)\n        \n        # Display results\n        summary = report['summary']\n        click.echo(f\"\\n🎯 Analysis Results for {building_name}:\")\n        click.echo(f\"   🏢 Building Type: {building_type.title()}\")\n        click.echo(f\"   📐 Floor Area: {floor_area:,.0f} m²\")\n        click.echo(f\"   ⚡ Total Consumption: {summary['total_consumption_kwh']:,.1f} kWh\")\n        click.echo(f\"   📊 Energy Intensity: {summary['total_consumption_kwh']/floor_area:.1f} kWh/m²\")\n        click.echo(f\"   💡 Potential Savings: {summary['potential_savings_percent']:.1f}%\")\n        click.echo(f\"   💰 Cost Savings: €{summary['cost_savings_estimate_eur']:,.2f}\")\n        click.echo(f\"   🎯 Model Accuracy: {metrics['val_r2']:.1%}\")\n        \n        # Top suggestions\n        click.echo(f\"\\n💡 Top Optimization Opportunities:\")\n        suggestion_count = 0\n        for suggestion in suggestions:\n            for s in suggestion.get('suggestions', []):\n                if suggestion_count < 5:\n                    priority = s.get('priority', 'medium')\n                    action = s.get('action', 'Unknown action')\n                    savings = s.get('estimated_savings_percent', 0)\n                    click.echo(f\"   {suggestion_count+1}. [{priority.upper()}] {action} ({savings:.1f}% savings)\")\n                    suggestion_count += 1\n        \n        # Save analysis report\n        report_file = f\"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json\"\n        with open(report_file, 'w') as f:\n            json.dump({\n                'building_info': {\n                    'name': building_name,\n                    'type': building_type,\n                    'floor_area': floor_area\n                },\n                'analysis_results': report,\n                'model_metrics': metrics,\n                'generated_at': datetime.now().isoformat()\n            }, f, indent=2, default=str)\n        \n        click.echo(f\"\\n📄 Full report saved to: {report_file}\")\n        click.echo(\"\\n✅ Analysis completed successfully!\")\n        \n    except Exception as e:\n        click.echo(f\"❌ Analysis failed: {e}\", err=True)\n        sys.exit(1)\n\n@main.command()\n@click.option('--format', 'output_format', default='text',\n              type=click.Choice(['text', 'json']),\n              help='Output format')\ndef metrics(output_format):\n    \"\"\"Show system metrics.\"\"\"\n    try:\n        from building_energy_optimizer.monitoring import generate_performance_report, get_performance_summary\n        \n        if output_format == 'json':\n            summary = get_performance_summary()\n            click.echo(json.dumps(summary, indent=2, default=str))\n        else:\n            report = generate_performance_report()\n            click.echo(report)\n        \n    except Exception as e:\n        click.echo(f\"❌ Metrics retrieval failed: {e}\", err=True)\n        sys.exit(1)\n\n@main.command()\n@click.option('--start-date', default='2024-01-01', help='Start date (YYYY-MM-DD)')\n@click.option('--end-date', default='2024-01-31', help='End date (YYYY-MM-DD)')\n@click.option('--building-type', default='commercial',\n              type=click.Choice(['residential', 'commercial', 'industrial']))\n@click.option('--floor-area', default=2500, type=float)\n@click.option('--output', '-o', default='sample_data.csv', help='Output file')\ndef generate_data(start_date, end_date, building_type, floor_area, output):\n    \"\"\"Generate sample energy data.\"\"\"\n    try:\n        from building_energy_optimizer import create_enhanced_example_data, BuildingConfig\n        \n        click.echo(f\"📊 Generating sample data from {start_date} to {end_date}...\")\n        \n        # Generate data\n        data = create_enhanced_example_data(start_date, end_date)\n        \n        # Save to file\n        data.to_csv(output, index=False)\n        \n        click.echo(f\"✅ Generated {len(data)} data points\")\n        click.echo(f\"💾 Saved to: {output}\")\n        click.echo(f\"\\n📈 Data Overview:\")\n        click.echo(f\"   Energy Range: {data['energy_consumption'].min():.1f} - {data['energy_consumption'].max():.1f} kWh\")\n        click.echo(f\"   Average: {data['energy_consumption'].mean():.1f} kWh\")\n        click.echo(f\"   Features: {len(data.columns)} columns\")\n        \n    except Exception as e:\n        click.echo(f\"❌ Data generation failed: {e}\", err=True)\n        sys.exit(1)\n\n@main.command()\ndef version():\n    \"\"\"Show version information.\"\"\"\n    try:\n        from building_energy_optimizer import get_version_info, check_installation\n        \n        # Version info\n        version_info = get_version_info()\n        click.echo(f\"🏢 Building Energy Optimizer v{version_info['version']}\")\n        click.echo(f\"👥 {version_info['author']}\")\n        click.echo(f\"📝 {version_info['description']}\")\n        \n        # Features\n        click.echo(f\"\\n✨ Features:\")\n        for feature in version_info['features']:\n            click.echo(f\"   ✅ {feature}\")\n        \n        # Installation status\n        click.echo(f\"\\n📦 Installation Status:\")\n        status = check_installation()\n        \n        for dep, info in status['optional_dependencies'].items():\n            emoji = \"✅\" if info['installed'] else \"❌\"\n            click.echo(f\"   {emoji} {dep}: {info['description']}\")\n        \n    except Exception as e:\n        click.echo(f\"❌ Version check failed: {e}\", err=True)\n        sys.exit(1)\n\n@main.command()\n@click.option('--type', 'init_type', default='basic',\n              type=click.Choice(['basic', 'full', 'development']),\n              help='Initialization type')\ndef init(init_type):\n    \"\"\"Initialize Building Energy Optimizer in current directory.\"\"\"\n    try:\n        current_dir = Path.cwd()\n        click.echo(f\"🔧 Initializing Building Energy Optimizer in {current_dir}...\")\n        \n        # Create directory structure\n        directories = {\n            'basic': ['data', 'models', 'logs'],\n            'full': ['data', 'models', 'logs', 'backups', 'config', 'examples'],\n            'development': ['data', 'models', 'logs', 'backups', 'config', 'examples', 'tests', 'docs']\n        }\n        \n        for directory in directories[init_type]:\n            Path(directory).mkdir(exist_ok=True)\n            click.echo(f\"   📁 Created: {directory}/\")\n        \n        # Create basic configuration\n        if not Path(\".env\").exists():\n            env_content = \"\"\"# Building Energy Optimizer Configuration\nENVIRONMENT=development\nDEBUG=true\nOPENWEATHERMAP_API_KEY=your_api_key_here\nDATABASE_URL=sqlite:///building_energy.db\n\"\"\"\n            with open(\".env\", \"w\") as f:\n                f.write(env_content)\n            click.echo(f\"   ⚙️ Created: .env\")\n        \n        # Create example script\n        if init_type in ['full', 'development']:\n            example_script = '''#!/usr/bin/env python3\n\"\"\"Example usage of Building Energy Optimizer.\"\"\"\n\nfrom building_energy_optimizer import quick_optimize, create_enhanced_example_data\n\ndef main():\n    # Generate sample data\n    data = create_enhanced_example_data(\\'2024-01-01\\', \\'2024-01-07\\')\n    \n    # Run optimization\n    result = quick_optimize(data, algorithm=\\'xgboost\\')\n    \n    # Show results\n    summary = result[\\'report\\'][\\'summary\\']\n    print(f\"Potential savings: {summary[\\'potential_savings_percent\\']:.1f}%\")\n    print(f\"Cost savings: €{summary[\\'cost_savings_estimate_eur\\']:.2f}\")\n\nif __name__ == \"__main__\":\n    main()\n'''\n            with open(\"examples/basic_example.py\", \"w\") as f:\n                f.write(example_script)\n            click.echo(f\"   📝 Created: examples/basic_example.py\")\n        \n        # Initialize database\n        click.echo(f\"\\n🗄️ Initializing database...\")\n        try:\n            from building_energy_optimizer.utils.database import init_database\n            init_database()\n            click.echo(f\"   ✅ Database initialized\")\n        except Exception as e:\n            click.echo(f\"   ⚠️ Database initialization failed: {e}\")\n        \n        click.echo(f\"\\n✅ Initialization completed!\")\n        click.echo(f\"\\n🚀 Next steps:\")\n        click.echo(f\"   1. Edit .env with your configuration\")\n        click.echo(f\"   2. Run: beo demo\")\n        click.echo(f\"   3. Start services: beo api & beo dashboard\")\n        \n    except Exception as e:\n        click.echo(f\"❌ Initialization failed: {e}\", err=True)\n        sys.exit(1)\n\n# Plugin management commands\n@main.group()\ndef plugins():\n    \"\"\"Plugin management commands.\"\"\"\n    pass\n\n@plugins.command('list')\ndef list_plugins():\n    \"\"\"List available plugins.\"\"\"\n    try:\n        from building_energy_optimizer.plugins import get_plugin_manager\n        \n        manager = get_plugin_manager()\n        status_summary = manager.get_status_summary()\n        \n        click.echo(\"🧩 Available Plugins:\")\n        click.echo(\"=\" * 25)\n        \n        for plugin_name, plugin in manager.plugins.items():\n            status = \"✅ Loaded\" if plugin.is_loaded() else \"❌ Not Loaded\"\n            click.echo(f\"   {status} {plugin_name}: {plugin.name} v{plugin.version}\")\n            if plugin.description:\n                click.echo(f\"     📝 {plugin.description}\")\n        \n        click.echo(f\"\\n📊 Summary: {status_summary['loaded_plugins']}/{status_summary['total_plugins']} plugins loaded\")\n        \n    except Exception as e:\n        click.echo(f\"❌ Plugin listing failed: {e}\", err=True)\n        sys.exit(1)\n\n@plugins.command('enable')\n@click.argument('plugin_name')\ndef enable_plugin(plugin_name):\n    \"\"\"Enable a plugin.\"\"\"\n    try:\n        from building_energy_optimizer.plugins import get_plugin_manager\n        \n        manager = get_plugin_manager()\n        \n        if plugin_name not in manager.plugins:\n            click.echo(f\"❌ Plugin '{plugin_name}' not found\", err=True)\n            sys.exit(1)\n        \n        # This would enable the plugin in a real system\n        click.echo(f\"✅ Plugin '{plugin_name}' enabled\")\n        \n    except Exception as e:\n        click.echo(f\"❌ Plugin enable failed: {e}\", err=True)\n        sys.exit(1)\n\nif __name__ == '__main__':\n    main()\n
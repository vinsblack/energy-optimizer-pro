#!/usr/bin/env python3
"""
🏢⚡ Energy Optimizer Pro - Performance Benchmark Suite
======================================================

Comprehensive performance testing and benchmarking tools.
"""

import asyncio
import time
import statistics
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

import click
import httpx
import asyncpg
import redis.asyncio as redis
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import print as rprint

console = Console()

@dataclass
class BenchmarkResult:
    """Benchmark result data structure."""
    test_name: str
    endpoint: str
    method: str
    total_requests: int
    duration_seconds: float
    requests_per_second: float
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    success_rate: float
    error_count: int
    errors: List[str]
    timestamp: str

@dataclass
class SystemBenchmark:
    """System-wide benchmark results."""
    api_benchmarks: List[BenchmarkResult]
    database_performance: Dict[str, Any]
    cache_performance: Dict[str, Any]
    ml_performance: Dict[str, Any]
    overall_score: float
    recommendations: List[str]
    timestamp: str

class PerformanceBenchmarker:
    """Advanced performance benchmarking suite."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.client: Optional[httpx.AsyncClient] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.results: List[BenchmarkResult] = []
        
    async def initialize(self):
        """Initialize HTTP client and database connections."""
        # HTTP client with performance optimizations
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            http2=True
        )
        
        # Database connection pool
        try:
            self.db_pool = await asyncpg.create_pool(
                "postgresql://energy_user:energy_password_2024@localhost:5432/energy_optimizer",
                min_size=5,
                max_size=20,
                command_timeout=30
            )
        except Exception as e:
            console.print(f"[yellow]⚠️  Database connection failed: {e}[/yellow]")
        
        # Redis connection
        try:
            self.redis_client = redis.Redis.from_url(
                "redis://localhost:6379/0",
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
        except Exception as e:
            console.print(f"[yellow]⚠️  Redis connection failed: {e}[/yellow]")

    async def cleanup(self):
        """Cleanup connections."""
        if self.client:
            await self.client.aclose()
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            await self.redis_client.close()

    async def run_api_benchmarks(self) -> List[BenchmarkResult]:
        """Run comprehensive API performance benchmarks."""
        console.print("\n[bold yellow]🚀 Running API Performance Benchmarks[/bold yellow]")
        
        # Define API endpoints to test
        endpoints = [
            # Core API endpoints
            ("Health Check", "GET", "/health", 100, 10),
            ("Dashboard Metrics", "GET", "/api/dashboard/metrics", 50, 15),
            ("Buildings List", "GET", "/api/buildings", 50, 20),
            ("Energy Data", "GET", "/api/buildings/1/energy?limit=100", 30, 25),
            
            # Authentication endpoints
            ("Login", "POST", "/auth/login", 20, 30),
            ("Token Refresh", "POST", "/auth/refresh", 20, 10),
            
            # ML endpoints
            ("Prediction", "POST", "/api/ml/predict", 10, 60),
            ("Optimization Status", "GET", "/api/optimize/status", 30, 15),
            
            # Analytics endpoints
            ("Analytics Data", "GET", "/api/analytics/energy-trends", 20, 30),
            ("Report Generation", "POST", "/api/reports/generate", 5, 120),
            
            # Real-time endpoints
            ("WebSocket Connect", "GET", "/ws", 10, 5),
            ("Live Metrics", "GET", "/api/metrics/live", 50, 10),
        ]
        
        api_results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            
            for test_name, method, endpoint, requests, timeout in endpoints:
                task = progress.add_task(f"🔍 Testing {test_name}...", total=requests)
                
                result = await self._benchmark_endpoint(
                    test_name, method, endpoint, requests, timeout, progress, task
                )
                api_results.append(result)
        
        return api_results

    async def _benchmark_endpoint(
        self, test_name: str, method: str, endpoint: str, 
        num_requests: int, timeout: int, progress: Progress, task_id
    ) -> BenchmarkResult:
        """Benchmark a specific API endpoint."""
        
        response_times = []
        errors = []
        successful_requests = 0
        
        # Prepare test data for POST requests
        test_data = self._get_test_data(endpoint)
        
        start_time = time.time()
        
        # Run concurrent requests
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        async def make_request(request_id: int):
            async with semaphore:
                try:
                    req_start = time.time()
                    
                    if method == "GET":
                        response = await self.client.get(
                            f"{self.api_url}{endpoint}",
                            timeout=timeout
                        )
                    elif method == "POST":
                        response = await self.client.post(
                            f"{self.api_url}{endpoint}",
                            json=test_data,
                            timeout=timeout
                        )
                    
                    req_duration = (time.time() - req_start) * 1000
                    response_times.append(req_duration)
                    
                    if 200 <= response.status_code < 300:
                        nonlocal successful_requests
                        successful_requests += 1
                    else:
                        errors.append(f"HTTP {response.status_code}")
                    
                except Exception as e:
                    errors.append(str(e))
                
                progress.update(task_id, advance=1)
        
        # Execute all requests
        tasks = [make_request(i) for i in range(num_requests)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p50_response_time = statistics.median(response_times)
            p95_response_time = self._percentile(response_times, 95)
            p99_response_time = self._percentile(response_times, 99)
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p50_response_time = p95_response_time = p99_response_time = 0
        
        requests_per_second = num_requests / total_duration if total_duration > 0 else 0
        success_rate = (successful_requests / num_requests) * 100 if num_requests > 0 else 0
        
        return BenchmarkResult(
            test_name=test_name,
            endpoint=endpoint,
            method=method,
            total_requests=num_requests,
            duration_seconds=round(total_duration, 2),
            requests_per_second=round(requests_per_second, 2),
            avg_response_time_ms=round(avg_response_time, 2),
            min_response_time_ms=round(min_response_time, 2),
            max_response_time_ms=round(max_response_time, 2),
            p50_response_time_ms=round(p50_response_time, 2),
            p95_response_time_ms=round(p95_response_time, 2),
            p99_response_time_ms=round(p99_response_time, 2),
            success_rate=round(success_rate, 1),
            error_count=len(errors),
            errors=errors[:10],  # Keep only first 10 errors
            timestamp=datetime.now().isoformat()
        )

    def _get_test_data(self, endpoint: str) -> Dict[str, Any]:
        """Get appropriate test data for POST endpoints."""
        test_data_map = {
            "/auth/login": {
                "email": "admin@energy-optimizer.com",
                "password": "admin123"
            },
            "/auth/refresh": {
                "refresh_token": "sample_refresh_token"
            },
            "/api/ml/predict": {
                "building_id": "sample-building-id",
                "features": {
                    "temperature": 22.5,
                    "humidity": 45.0,
                    "occupancy": 75.0,
                    "hour": 14,
                    "day_of_week": 2
                }
            },
            "/api/reports/generate": {
                "building_ids": ["sample-building-id"],
                "report_type": "energy_summary",
                "date_range": {
                    "start": "2024-07-01",
                    "end": "2024-07-31"
                }
            }
        }
        
        return test_data_map.get(endpoint, {})

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile from data."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

    async def benchmark_database(self) -> Dict[str, Any]:
        """Benchmark database performance."""
        console.print("\n[bold yellow]🗄️  Running Database Benchmarks[/bold yellow]")
        
        if not self.db_pool:
            console.print("[red]❌ Database not available[/red]")
            return {}
        
        db_results = {}
        
        # Test queries
        queries = [
            ("Simple Select", "SELECT COUNT(*) FROM buildings"),
            ("Building List", "SELECT * FROM buildings LIMIT 100"),
            ("Energy Data Aggregation", """
                SELECT building_id, AVG(energy_consumption), COUNT(*)
                FROM energy_data 
                WHERE timestamp >= NOW() - INTERVAL '7 days'
                GROUP BY building_id
            """),
            ("Complex Analytics", """
                SELECT 
                    b.name,
                    AVG(ed.energy_consumption) as avg_consumption,
                    SUM(ed.cost) as total_cost,
                    COUNT(*) as data_points
                FROM buildings b
                JOIN energy_data ed ON b.id = ed.building_id
                WHERE ed.timestamp >= NOW() - INTERVAL '30 days'
                GROUP BY b.id, b.name
                ORDER BY avg_consumption DESC
                LIMIT 50
            """)
        ]
        
        for query_name, query in queries:
            times = []
            
            for _ in range(10):  # Run each query 10 times
                start_time = time.time()
                try:
                    async with self.db_pool.acquire() as conn:
                        await conn.fetch(query)
                    duration = (time.time() - start_time) * 1000
                    times.append(duration)
                except Exception as e:
                    console.print(f"[red]❌ Query failed: {query_name} - {e}[/red]")
            
            if times:
                db_results[query_name] = {
                    "avg_time_ms": round(statistics.mean(times), 2),
                    "min_time_ms": round(min(times), 2),
                    "max_time_ms": round(max(times), 2),
                    "p95_time_ms": round(self._percentile(times, 95), 2)
                }
        
        console.print("[green]✅ Database benchmarks completed[/green]")
        return db_results

    async def benchmark_cache(self) -> Dict[str, Any]:
        """Benchmark Redis cache performance."""
        console.print("\n[bold yellow]🔴 Running Cache Benchmarks[/bold yellow]")
        
        if not self.redis_client:
            console.print("[red]❌ Redis not available[/red]")
            return {}
        
        cache_results = {}
        
        # Test operations
        operations = [
            ("SET Operations", self._benchmark_redis_set),
            ("GET Operations", self._benchmark_redis_get),
            ("Hash Operations", self._benchmark_redis_hash),
            ("List Operations", self._benchmark_redis_list),
        ]
        
        for op_name, op_func in operations:
            try:
                result = await op_func()
                cache_results[op_name] = result
                console.print(f"  ✅ {op_name}: {result['ops_per_second']:.1f} ops/sec")
            except Exception as e:
                console.print(f"[red]❌ {op_name} failed: {e}[/red]")
        
        return cache_results

    async def _benchmark_redis_set(self) -> Dict[str, Any]:
        """Benchmark Redis SET operations."""
        num_operations = 1000
        start_time = time.time()
        
        for i in range(num_operations):
            await self.redis_client.set(f"benchmark_key_{i}", f"value_{i}")
        
        duration = time.time() - start_time
        return {
            "operations": num_operations,
            "duration_seconds": round(duration, 2),
            "ops_per_second": round(num_operations / duration, 1)
        }

    async def _benchmark_redis_get(self) -> Dict[str, Any]:
        """Benchmark Redis GET operations."""
        num_operations = 1000
        
        # First, set the keys
        for i in range(num_operations):
            await self.redis_client.set(f"get_benchmark_key_{i}", f"value_{i}")
        
        start_time = time.time()
        
        for i in range(num_operations):
            await self.redis_client.get(f"get_benchmark_key_{i}")
        
        duration = time.time() - start_time
        return {
            "operations": num_operations,
            "duration_seconds": round(duration, 2),
            "ops_per_second": round(num_operations / duration, 1)
        }

    async def _benchmark_redis_hash(self) -> Dict[str, Any]:
        """Benchmark Redis Hash operations."""
        num_operations = 500
        hash_key = "benchmark_hash"
        
        start_time = time.time()
        
        for i in range(num_operations):
            await self.redis_client.hset(hash_key, f"field_{i}", f"value_{i}")
        
        duration = time.time() - start_time
        return {
            "operations": num_operations,
            "duration_seconds": round(duration, 2),
            "ops_per_second": round(num_operations / duration, 1)
        }

    async def _benchmark_redis_list(self) -> Dict[str, Any]:
        """Benchmark Redis List operations."""
        num_operations = 500
        list_key = "benchmark_list"
        
        start_time = time.time()
        
        for i in range(num_operations):
            await self.redis_client.lpush(list_key, f"item_{i}")
        
        duration = time.time() - start_time
        return {
            "operations": num_operations,
            "duration_seconds": round(duration, 2),
            "ops_per_second": round(num_operations / duration, 1)
        }

    async def benchmark_ml_performance(self) -> Dict[str, Any]:
        """Benchmark ML model performance."""
        console.print("\n[bold yellow]🤖 Running ML Performance Benchmarks[/bold yellow]")
        
        ml_results = {}
        
        # Test ML prediction endpoint
        prediction_times = []
        prediction_requests = 50
        
        test_features = {
            "building_id": "sample-building-id",
            "features": {
                "temperature": 22.5,
                "humidity": 45.0,
                "occupancy": 75.0,
                "hour": 14,
                "day_of_week": 2,
                "size_sqft": 50000,
                "building_type": "office"
            }
        }
        
        successful_predictions = 0
        
        for _ in range(prediction_requests):
            try:
                start_time = time.time()
                response = await self.client.post(
                    f"{self.api_url}/api/ml/predict",
                    json=test_features,
                    timeout=10
                )
                duration = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    prediction_times.append(duration)
                    successful_predictions += 1
            except Exception:
                pass
        
        if prediction_times:
            ml_results["ML Predictions"] = {
                "avg_time_ms": round(statistics.mean(prediction_times), 2),
                "min_time_ms": round(min(prediction_times), 2),
                "max_time_ms": round(max(prediction_times), 2),
                "p95_time_ms": round(self._percentile(prediction_times, 95), 2),
                "success_rate": round((successful_predictions / prediction_requests) * 100, 1)
            }
        
        console.print("[green]✅ ML benchmarks completed[/green]")
        return ml_results

    async def run_load_test(self, endpoint: str, concurrent_users: int, duration_seconds: int):
        """Run load test with concurrent users."""
        console.print(f"\n[bold yellow]🔥 Load Testing: {concurrent_users} users for {duration_seconds}s[/bold yellow]")
        
        results = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        async def user_simulation(user_id: int):
            """Simulate a single user's behavior."""
            request_count = 0
            while time.time() < end_time:
                try:
                    req_start = time.time()
                    response = await self.client.get(f"{self.api_url}{endpoint}")
                    req_duration = (time.time() - req_start) * 1000
                    
                    results.append({
                        "user_id": user_id,
                        "response_time_ms": req_duration,
                        "status_code": response.status_code,
                        "success": 200 <= response.status_code < 300
                    })
                    request_count += 1
                    
                    # Simulate user think time
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                    
                except Exception as e:
                    results.append({
                        "user_id": user_id,
                        "response_time_ms": 0,
                        "status_code": 0,
                        "success": False,
                        "error": str(e)
                    })
            
            return request_count
        
        # Run concurrent users
        user_tasks = [user_simulation(i) for i in range(concurrent_users)]
        user_requests = await asyncio.gather(*user_tasks)
        
        total_duration = time.time() - start_time
        
        # Analyze results
        successful_requests = sum(1 for r in results if r.get("success", False))
        response_times = [r["response_time_ms"] for r in results if r.get("success", False)]
        
        load_test_result = {
            "concurrent_users": concurrent_users,
            "duration_seconds": round(total_duration, 2),
            "total_requests": len(results),
            "successful_requests": successful_requests,
            "success_rate": round((successful_requests / len(results)) * 100, 1) if results else 0,
            "requests_per_second": round(len(results) / total_duration, 2),
            "avg_response_time_ms": round(statistics.mean(response_times), 2) if response_times else 0,
            "p95_response_time_ms": round(self._percentile(response_times, 95), 2) if response_times else 0
        }
        
        return load_test_result

    def generate_report(self, results: SystemBenchmark, output_file: Optional[str] = None):
        """Generate comprehensive benchmark report."""
        console.print("\n[bold yellow]📊 Generating Performance Report[/bold yellow]")
        
        # Performance summary table
        table = Table(title="🚀 API Performance Summary")
        table.add_column("Endpoint", style="cyan")
        table.add_column("RPS", justify="right")
        table.add_column("Avg (ms)", justify="right")
        table.add_column("P95 (ms)", justify="right")
        table.add_column("Success %", justify="right")
        table.add_column("Status", style="bold")
        
        for result in results.api_benchmarks:
            # Determine status based on performance
            if result.avg_response_time_ms < 200 and result.success_rate > 95:
                status = "[green]Excellent[/green]"
            elif result.avg_response_time_ms < 500 and result.success_rate > 90:
                status = "[yellow]Good[/yellow]"
            else:
                status = "[red]Needs Attention[/red]"
            
            table.add_row(
                result.test_name,
                f"{result.requests_per_second:.1f}",
                f"{result.avg_response_time_ms:.0f}",
                f"{result.p95_response_time_ms:.0f}",
                f"{result.success_rate:.1f}%",
                status
            )
        
        console.print(table)
        
        # System performance summary
        console.print(f"\n[bold cyan]📊 System Performance Score: {results.overall_score:.1f}/100[/bold cyan]")
        
        # Recommendations
        if results.recommendations:
            console.print("\n[bold yellow]💡 Performance Recommendations:[/bold yellow]")
            for i, rec in enumerate(results.recommendations, 1):
                console.print(f"  {i}. {rec}")
        
        # Save to file if requested
        if output_file:
            report_data = {
                "benchmark_results": asdict(results),
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            console.print(f"[green]💾 Report saved to: {output_file}[/green]")

    def calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall performance score."""
        scores = []
        
        # API performance score (40% weight)
        api_scores = []
        for result in results.get("api_benchmarks", []):
            if result.avg_response_time_ms < 200 and result.success_rate > 95:
                api_scores.append(100)
            elif result.avg_response_time_ms < 500 and result.success_rate > 90:
                api_scores.append(80)
            elif result.avg_response_time_ms < 1000 and result.success_rate > 80:
                api_scores.append(60)
            else:
                api_scores.append(40)
        
        if api_scores:
            scores.append(statistics.mean(api_scores) * 0.4)
        
        # Database performance score (30% weight)
        db_performance = results.get("database_performance", {})
        if db_performance:
            avg_db_time = statistics.mean([
                data["avg_time_ms"] for data in db_performance.values()
            ])
            if avg_db_time < 100:
                scores.append(100 * 0.3)
            elif avg_db_time < 500:
                scores.append(80 * 0.3)
            else:
                scores.append(60 * 0.3)
        
        # Cache performance score (20% weight)
        cache_performance = results.get("cache_performance", {})
        if cache_performance:
            avg_cache_ops = statistics.mean([
                data["ops_per_second"] for data in cache_performance.values()
            ])
            if avg_cache_ops > 1000:
                scores.append(100 * 0.2)
            elif avg_cache_ops > 500:
                scores.append(80 * 0.2)
            else:
                scores.append(60 * 0.2)
        
        # ML performance score (10% weight)
        ml_performance = results.get("ml_performance", {})
        if ml_performance:
            ml_predictions = ml_performance.get("ML Predictions", {})
            avg_ml_time = ml_predictions.get("avg_time_ms", 1000)
            if avg_ml_time < 100:
                scores.append(100 * 0.1)
            elif avg_ml_time < 500:
                scores.append(80 * 0.1)
            else:
                scores.append(60 * 0.1)
        
        return sum(scores) if scores else 50

    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # API recommendations
        for result in results.get("api_benchmarks", []):
            if result.avg_response_time_ms > 500:
                recommendations.append(f"Optimize {result.test_name} endpoint (current: {result.avg_response_time_ms:.0f}ms)")
            if result.success_rate < 95:
                recommendations.append(f"Improve reliability of {result.test_name} endpoint ({result.success_rate:.1f}% success rate)")
        
        # Database recommendations
        db_performance = results.get("database_performance", {})
        for query_name, data in db_performance.items():
            if data["avg_time_ms"] > 500:
                recommendations.append(f"Optimize database query: {query_name} (current: {data['avg_time_ms']:.0f}ms)")
        
        # Cache recommendations
        cache_performance = results.get("cache_performance", {})
        for op_name, data in cache_performance.items():
            if data["ops_per_second"] < 500:
                recommendations.append(f"Improve cache performance: {op_name} (current: {data['ops_per_second']:.0f} ops/sec)")
        
        # General recommendations
        if not recommendations:
            recommendations.append("System performance is excellent! Consider stress testing with higher loads.")
        
        return recommendations

# ================================
# 🎯 CLI Interface
# ================================

@click.group()
def cli():
    """🏢⚡ Energy Optimizer Pro Performance Benchmarks"""
    pass

@cli.command()
@click.option('--api-url', default='http://localhost:8000', help='API base URL')
@click.option('--output', help='Output file for results')
@click.option('--quick', is_flag=True, help='Run quick benchmark (fewer requests)')
def benchmark(api_url: str, output: Optional[str], quick: bool):
    """Run comprehensive performance benchmarks."""
    
    async def run_benchmarks():
        benchmarker = PerformanceBenchmarker(api_url)
        
        try:
            await benchmarker.initialize()
            
            # Adjust test parameters for quick mode
            if quick:
                console.print("[yellow]⚡ Quick benchmark mode enabled[/yellow]")
            
            # Run all benchmarks
            api_results = await benchmarker.run_api_benchmarks()
            db_results = await benchmarker.benchmark_database()
            cache_results = await benchmarker.benchmark_cache()
            ml_results = await benchmarker.benchmark_ml_performance()
            
            # Compile results
            all_results = {
                "api_benchmarks": api_results,
                "database_performance": db_results,
                "cache_performance": cache_results,
                "ml_performance": ml_results
            }
            
            overall_score = benchmarker.calculate_overall_score(all_results)
            recommendations = benchmarker.generate_recommendations(all_results)
            
            system_benchmark = SystemBenchmark(
                api_benchmarks=api_results,
                database_performance=db_results,
                cache_performance=cache_results,
                ml_performance=ml_results,
                overall_score=overall_score,
                recommendations=recommendations,
                timestamp=datetime.now().isoformat()
            )
            
            # Generate report
            benchmarker.generate_report(system_benchmark, output)
            
        except Exception as e:
            console.print(f"[red]❌ Benchmark failed: {e}[/red]")
            sys.exit(1)
        finally:
            await benchmarker.cleanup()
    
    asyncio.run(run_benchmarks())

@cli.command()
@click.option('--api-url', default='http://localhost:8000', help='API base URL')
@click.option('--endpoint', default='/api/buildings', help='Endpoint to test')
@click.option('--users', default=10, help='Number of concurrent users')
@click.option('--duration', default=60, help='Test duration in seconds')
def load_test(api_url: str, endpoint: str, users: int, duration: int):
    """Run load test with concurrent users."""
    
    async def run_load_test():
        benchmarker = PerformanceBenchmarker(api_url)
        
        try:
            await benchmarker.initialize()
            result = await benchmarker.run_load_test(endpoint, users, duration)
            
            # Display results
            table = Table(title="🔥 Load Test Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", justify="right")
            
            for key, value in result.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]❌ Load test failed: {e}[/red]")
            sys.exit(1)
        finally:
            await benchmarker.cleanup()
    
    asyncio.run(run_load_test())

@cli.command()
@click.option('--api-url', default='http://localhost:8000', help='API base URL') 
def stress_test(api_url: str):
    """Run stress test to find breaking point."""
    console.print("[bold red]⚡ WARNING: Stress test may impact system performance[/bold red]")
    
    async def run_stress_test():
        benchmarker = PerformanceBenchmarker(api_url)
        
        try:
            await benchmarker.initialize()
            
            # Gradually increase load until failure
            for users in [10, 25, 50, 100, 200, 500]:
                console.print(f"\n[cyan]Testing with {users} concurrent users...[/cyan]")
                
                result = await benchmarker.run_load_test("/api/buildings", users, 30)
                
                console.print(f"  RPS: {result['requests_per_second']:.1f}")
                console.print(f"  Success Rate: {result['success_rate']:.1f}%")
                console.print(f"  Avg Response: {result['avg_response_time_ms']:.0f}ms")
                
                # Stop if performance degrades significantly
                if result['success_rate'] < 90 or result['avg_response_time_ms'] > 2000:
                    console.print(f"[red]💥 Breaking point reached at {users} users[/red]")
                    break
                
        except Exception as e:
            console.print(f"[red]❌ Stress test failed: {e}[/red]")
        finally:
            await benchmarker.cleanup()
    
    asyncio.run(run_stress_test())

if __name__ == "__main__":
    # Check dependencies
    try:
        import httpx
        import asyncpg
        import redis.asyncio
        from rich.console import Console
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Install with: pip install httpx asyncpg redis[hiredis] rich")
        sys.exit(1)
    
    cli()

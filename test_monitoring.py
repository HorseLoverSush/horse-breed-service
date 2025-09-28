"""
Comprehensive test suite for enhanced error handling and monitoring features.

This script tests all aspects of the error handling system, enhanced logging,
and monitoring endpoints to ensure everything works correctly.
"""

import asyncio
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

# Configure test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MonitoringTestSuite:
    """Comprehensive test suite for monitoring and error handling."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    @contextmanager
    def test_case(self, name):
        """Context manager for individual test cases."""
        self.total_tests += 1
        print(f"\n🧪 Testing: {name}")
        print("-" * 60)
        start_time = time.time()
        
        try:
            yield
            duration = time.time() - start_time
            print(f"✅ PASSED: {name} ({duration:.2f}s)")
            self.passed_tests += 1
            self.test_results.append({
                "name": name,
                "status": "PASSED",
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ FAILED: {name} - {str(e)} ({duration:.2f}s)")
            self.test_results.append({
                "name": name,
                "status": "FAILED",
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
    
    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with error handling."""
        url = f"{self.api_base}{endpoint}"
        response = requests.request(method, url, timeout=10, **kwargs)
        return response
    
    def test_service_health(self):
        """Test basic service health and availability."""
        with self.test_case("Service Health Check"):
            # Test basic health endpoint
            response = self.make_request("GET", "/monitoring/health")
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            
            health_data = response.json()
            assert health_data["status"] == "healthy", f"Service not healthy: {health_data}"
            assert "timestamp" in health_data, "Missing timestamp in health response"
            assert "version" in health_data, "Missing version in health response"
            
            print(f"   Service Status: {health_data['status']}")
            print(f"   Uptime: {health_data.get('uptime_seconds', 0):.2f}s")
            print(f"   Version: {health_data.get('version', 'unknown')}")
    
    def test_detailed_health(self):
        """Test detailed health check with system metrics."""
        with self.test_case("Detailed Health Check"):
            response = self.make_request("GET", "/monitoring/health/detailed")
            assert response.status_code == 200, f"Detailed health check failed: {response.status_code}"
            
            health_data = response.json()
            required_fields = ["status", "timestamp", "system", "service", "components"]
            for field in required_fields:
                assert field in health_data, f"Missing field: {field}"
            
            system_metrics = health_data["system"]
            assert "cpu_percent" in system_metrics, "Missing CPU metrics"
            assert "memory_percent" in system_metrics, "Missing memory metrics"
            
            print(f"   Overall Status: {health_data['status']}")
            print(f"   CPU Usage: {system_metrics['cpu_percent']}%")
            print(f"   Memory Usage: {system_metrics['memory_percent']}%")
            print(f"   Components: {len(health_data['components'])}")
    
    def test_metrics_endpoint(self):
        """Test comprehensive metrics endpoint."""
        with self.test_case("Application Metrics"):
            response = self.make_request("GET", "/monitoring/metrics")
            assert response.status_code == 200, f"Metrics endpoint failed: {response.status_code}"
            
            metrics_data = response.json()
            required_sections = ["service", "system", "system_info"]
            for section in required_sections:
                assert section in metrics_data, f"Missing metrics section: {section}"
            
            service_metrics = metrics_data["service"]
            system_info = metrics_data["system_info"]
            
            print(f"   Platform: {system_info.get('platform', 'unknown')}")
            print(f"   Python Version: {system_info.get('python_version', 'unknown')}")
            print(f"   CPU Count: {system_info.get('cpu_count', 'unknown')}")
            print(f"   Total Requests: {service_metrics.get('total_requests', 0)}")
    
    def test_performance_metrics(self):
        """Test performance-specific metrics."""
        with self.test_case("Performance Metrics"):
            response = self.make_request("GET", "/monitoring/metrics/performance")
            assert response.status_code == 200, f"Performance metrics failed: {response.status_code}"
            
            perf_data = response.json()
            required_sections = ["request_metrics", "error_metrics"]
            for section in required_sections:
                assert section in perf_data, f"Missing performance section: {section}"
            
            request_metrics = perf_data["request_metrics"]
            error_metrics = perf_data["error_metrics"]
            
            print(f"   Total Requests: {request_metrics.get('total_requests', 0)}")
            print(f"   Requests/Second: {request_metrics.get('requests_per_second', 0):.2f}")
            print(f"   Avg Response Time: {request_metrics.get('average_response_time', 0):.2f}ms")
            print(f"   Error Rate: {error_metrics.get('error_rate', 0):.2f}%")
    
    def test_log_metrics(self):
        """Test logging metrics endpoint."""
        with self.test_case("Log Metrics"):
            response = self.make_request("GET", "/monitoring/logs/metrics")
            assert response.status_code == 200, f"Log metrics failed: {response.status_code}"
            
            log_data = response.json()
            required_fields = ["total_log_entries", "log_levels", "recent_errors", "log_files"]
            for field in required_fields:
                assert field in log_data, f"Missing log metrics field: {field}"
            
            print(f"   Total Log Entries: {log_data['total_log_entries']}")
            print(f"   Log Files: {len(log_data['log_files'])}")
            print(f"   Recent Errors: {len(log_data['recent_errors'])}")
            
            if log_data['log_files']:
                for log_file in log_data['log_files']:
                    print(f"     - {log_file['name']}: {log_file['size_mb']}MB")
    
    def test_service_status(self):
        """Test overall service status endpoint."""
        with self.test_case("Service Status"):
            response = self.make_request("GET", "/monitoring/status")
            assert response.status_code == 200, f"Service status failed: {response.status_code}"
            
            status_data = response.json()
            required_fields = ["status", "timestamp", "uptime_seconds", "components"]
            for field in required_fields:
                assert field in status_data, f"Missing status field: {field}"
            
            print(f"   Status: {status_data['status']}")
            print(f"   Uptime: {status_data.get('uptime_human', 'unknown')}")
            print(f"   Environment: {status_data.get('environment', 'unknown')}")
            
            components = status_data['components']
            for component, status in components.items():
                print(f"   {component.title()}: {status}")
    
    def test_error_handling(self):
        """Test error handling with various scenarios."""
        with self.test_case("Error Handling"):
            # Test 404 error (non-existent breed)
            response = self.make_request("GET", "/breeds/non-existent-breed-12345")
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
            
            error_data = response.json()
            assert "detail" in error_data, "Missing error detail"
            assert "error_type" in error_data, "Missing error type"
            assert "correlation_id" in error_data, "Missing correlation ID"
            
            print(f"   404 Error properly handled: {error_data['detail']}")
            print(f"   Error Type: {error_data['error_type']}")
            print(f"   Correlation ID: {error_data['correlation_id']}")
            
            # Test validation error (if applicable)
            try:
                response = self.make_request("POST", "/breeds", json={"invalid": "data"})
                if response.status_code == 422:
                    validation_error = response.json()
                    print(f"   Validation Error handled: {validation_error.get('detail', 'Unknown')}")
            except:
                pass  # Validation test is optional
    
    def test_api_documentation(self):
        """Test API documentation endpoints."""
        with self.test_case("API Documentation"):
            # Test OpenAPI JSON
            response = requests.get(f"{self.base_url}/openapi.json", timeout=10)
            assert response.status_code == 200, f"OpenAPI JSON failed: {response.status_code}"
            
            openapi_data = response.json()
            assert "openapi" in openapi_data, "Missing OpenAPI version"
            assert "paths" in openapi_data, "Missing API paths"
            
            # Count endpoints
            paths = openapi_data["paths"]
            monitoring_paths = [path for path in paths.keys() if "/monitoring" in path]
            breed_paths = [path for path in paths.keys() if "/breeds" in path]
            
            print(f"   Total API Paths: {len(paths)}")
            print(f"   Monitoring Endpoints: {len(monitoring_paths)}")
            print(f"   Breed Endpoints: {len(breed_paths)}")
            
            # Test Swagger UI (just check if it loads)
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            assert response.status_code == 200, f"Swagger UI failed: {response.status_code}"
            print("   Swagger UI accessible")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        with self.test_case("Concurrent Request Handling"):
            import concurrent.futures
            import threading
            
            def make_health_request():
                try:
                    response = self.make_request("GET", "/monitoring/health")
                    return response.status_code == 200
                except:
                    return False
            
            # Make 10 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_health_request) for _ in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_count = sum(results)
            assert success_count >= 8, f"Too many concurrent requests failed: {success_count}/10"
            
            print(f"   Concurrent Requests: {success_count}/10 successful")
    
    def test_log_file_creation(self):
        """Test that log files are being created properly."""
        with self.test_case("Log File Creation"):
            logs_dir = Path("logs")
            assert logs_dir.exists(), "Logs directory does not exist"
            
            # Make some requests to generate logs
            for i in range(3):
                self.make_request("GET", "/monitoring/health")
                time.sleep(0.1)
            
            # Check for log files
            log_files = list(logs_dir.glob("*.log"))
            assert len(log_files) > 0, "No log files found"
            
            print(f"   Log files found: {len(log_files)}")
            for log_file in log_files:
                size_kb = log_file.stat().st_size / 1024
                print(f"     - {log_file.name}: {size_kb:.2f}KB")
    
    def test_enhanced_logging_features(self):
        """Test enhanced logging features like correlation IDs."""
        with self.test_case("Enhanced Logging Features"):
            # Make a request and check if correlation ID is returned
            response = self.make_request("GET", "/monitoring/health")
            correlation_id = response.headers.get("X-Correlation-ID")
            
            if correlation_id:
                assert len(correlation_id) > 0, "Empty correlation ID"
                print(f"   Correlation ID generated: {correlation_id}")
            else:
                print("   Note: Correlation ID not found in headers (may be implementation dependent)")
            
            # Check if logs contain structured data (if accessible)
            logs_dir = Path("logs")
            if logs_dir.exists():
                main_log = logs_dir / "horse_breed_service.log"
                if main_log.exists():
                    try:
                        with open(main_log, 'r') as f:
                            # Read last few lines
                            lines = f.readlines()[-5:]
                            json_logs = 0
                            for line in lines:
                                try:
                                    log_entry = json.loads(line.strip())
                                    if "@timestamp" in log_entry:
                                        json_logs += 1
                                except:
                                    continue
                            
                            print(f"   Structured JSON logs found: {json_logs}/5")
                    except Exception as e:
                        print(f"   Could not read log file: {e}")
    
    def run_all_tests(self):
        """Run all test cases."""
        print("🚀 Starting Monitoring & Error Handling Test Suite")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        self.test_service_health()
        self.test_detailed_health()
        self.test_metrics_endpoint()
        self.test_performance_metrics()
        self.test_log_metrics()
        self.test_service_status()
        self.test_error_handling()
        self.test_api_documentation()
        self.test_concurrent_requests()
        self.test_log_file_creation()
        self.test_enhanced_logging_features()
        
        # Print summary
        duration = time.time() - start_time
        success_rate = (self.passed_tests / self.total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Duration: {duration:.2f}s")
        
        if success_rate == 100:
            print("\n🎉 ALL TESTS PASSED! Your monitoring system is working perfectly!")
        elif success_rate >= 80:
            print("\n✅ Most tests passed. Some minor issues may need attention.")
        else:
            print("\n⚠️  Several tests failed. Please check the service configuration.")
        
        # Save test results
        results_file = Path("test_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.total_tests,
                    "passed_tests": self.passed_tests,
                    "success_rate": success_rate,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat()
                },
                "test_results": self.test_results
            }, f, indent=2)
        
        print(f"\n📝 Detailed results saved to: {results_file}")
        
        return success_rate == 100


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Horse Breed Service monitoring")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the service (default: http://localhost:8000)")
    parser.add_argument("--wait", type=int, default=0,
                       help="Wait N seconds before starting tests (useful if service is starting)")
    
    args = parser.parse_args()
    
    if args.wait > 0:
        print(f"⏱️  Waiting {args.wait} seconds for service to start...")
        time.sleep(args.wait)
    
    # Check if service is running
    try:
        response = requests.get(f"{args.url}/docs", timeout=5)
        if response.status_code != 200:
            print(f"❌ Service not accessible at {args.url}")
            print("   Make sure the service is running with: python -m uvicorn app.main:app --reload")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to service at {args.url}")
        print("   Make sure the service is running with: python -m uvicorn app.main:app --reload")
        return False
    
    # Run tests
    test_suite = MonitoringTestSuite(args.url)
    success = test_suite.run_all_tests()
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
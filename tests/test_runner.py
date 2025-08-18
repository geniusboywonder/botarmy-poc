# tests/test_runner.py
#!/usr/bin/env python3
"""
Comprehensive test runner for BotArmy POC Integration Testing
Executes all integration tests with detailed reporting
"""

import pytest
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Custom test runner with enhanced reporting"""
    
    def __init__(self):
        self.start_time = None
        self.test_results = {
            "summary": {},
            "detailed_results": [],
            "performance_metrics": {},
            "coverage_report": {},
            "timestamp": None
        }
    
    def run_all_tests(self, verbose=True, coverage=True):
        """Run all integration tests with optional coverage"""
        print("🚀 Starting BotArmy POC Integration Test Suite")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Test files to run
        test_files = [
            "tests/test_api.py",
            "tests/test_database.py", 
            "tests/test_integration.py",
            "tests/test_integration_comprehensive.py",
            "tests/test_integration_comprehensive_part2.py",
            "tests/test_integration_comprehensive_part3.py"
        ]
        
        # Build pytest arguments
        args = []
        
        # Add coverage if requested
        if coverage:
            args.extend([
                "--cov=.",
                "--cov-report=html:tests/coverage_html",
                "--cov-report=json:tests/coverage.json",
                "--cov-report=term-missing"
            ])
        
        # Add verbose output
        if verbose:
            args.append("-v")
        
        # Add test files
        args.extend(test_files)
        
        # Add additional options
        args.extend([
            "--tb=short",
            "--junit-xml=tests/test_results.xml",
            "--json-report",
            "--json-report-file=tests/test_report.json"
        ])
        
        print(f"Running pytest with args: {' '.join(args)}")
        print("-" * 60)
        
        # Run tests
        exit_code = pytest.main(args)
        
        # Process results
        self._process_results(exit_code)
        
        return exit_code
    
    def run_specific_category(self, category):
        """Run specific test category"""
        categories = {
            "api": ["tests/test_api.py", "tests/test_integration_comprehensive.py::TestAPIIntegration"],
            "agents": ["tests/test_integration_comprehensive.py::TestAgentWorkflow"],
            "database": ["tests/test_database.py", "tests/test_integration_comprehensive.py::TestDatabaseIntegration"],
            "realtime": ["tests/test_integration_comprehensive_part2.py::TestRealTimeFeatures"],
            "errors": ["tests/test_integration_comprehensive_part2.py::TestErrorHandling"],
            "e2e": ["tests/test_integration_comprehensive_part3.py::TestEndToEnd"],
            "performance": ["tests/test_integration_comprehensive_part3.py::TestEndToEnd::test_performance_under_load"],
            "consistency": ["tests/test_integration_comprehensive_part3.py::TestDataConsistency"]
        }
        
        if category not in categories:
            print(f"❌ Unknown test category: {category}")
            print(f"Available categories: {', '.join(categories.keys())}")
            return 1
        
        print(f"🎯 Running {category.upper()} tests")
        print("=" * 60)
        
        args = ["-v", "--tb=short"] + categories[category]
        return pytest.main(args)
    
    def _process_results(self, exit_code):
        """Process and display test results"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        # Basic results
        if exit_code == 0:
            print("✅ All tests PASSED")
        else:
            print(f"❌ Tests FAILED (exit code: {exit_code})")
        
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        
        # Load detailed results if available
        self._load_detailed_results()
        
        # Generate summary report
        self._generate_summary_report()
    
    def _load_detailed_results(self):
        """Load detailed test results from JSON report"""
        try:
            if os.path.exists("tests/test_report.json"):
                with open("tests/test_report.json", "r") as f:
                    report = json.load(f)
                
                summary = report.get("summary", {})
                print(f"📋 Tests run: {summary.get('total', 0)}")
                print(f"✅ Passed: {summary.get('passed', 0)}")
                print(f"❌ Failed: {summary.get('failed', 0)}")
                print(f"⚠️  Skipped: {summary.get('skipped', 0)}")
                print(f"🚨 Errors: {summary.get('error', 0)}")
                
                if summary.get('failed', 0) > 0:
                    print("\n❌ FAILED TESTS:")
                    for test in report.get("tests", []):
                        if test.get("outcome") == "failed":
                            print(f"   - {test.get('nodeid', 'Unknown')}")
                            if test.get('call', {}).get('longrepr'):
                                error = test['call']['longrepr']
                                if isinstance(error, str) and len(error) > 200:
                                    error = error[:200] + "..."
                                print(f"     Error: {error}")
                
        except Exception as e:
            print(f"⚠️  Could not load detailed results: {e}")
    
    def _generate_summary_report(self):
        """Generate comprehensive summary report"""
        timestamp = datetime.now().isoformat()
        
        report = {
            "timestamp": timestamp,
            "execution_time": time.time() - self.start_time if self.start_time else 0,
            "test_categories": {
                "api_integration": "Tests FastAPI endpoints with database",
                "agent_workflow": "Tests AI agent processing pipeline", 
                "database_integration": "Tests complex database operations",
                "realtime_features": "Tests SSE and background tasks",
                "error_handling": "Tests error recovery and resilience",
                "end_to_end": "Tests complete user workflows",
                "data_consistency": "Tests data integrity across operations"
            },
            "coverage_info": self._get_coverage_info(),
            "performance_benchmarks": {
                "api_response_time": "< 2 seconds average",
                "concurrent_requests": "95%+ success rate under load",
                "database_operations": "< 100ms query time",
                "agent_processing": "< 30 seconds per stage"
            }
        }
        
        # Save report
        os.makedirs("tests/reports", exist_ok=True)
        report_file = f"tests/reports/integration_test_report_{timestamp.replace(':', '-')}.json"
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def _get_coverage_info(self):
        """Get coverage information if available"""
        try:
            if os.path.exists("tests/coverage.json"):
                with open("tests/coverage.json", "r") as f:
                    coverage = json.load(f)
                
                return {
                    "total_coverage": f"{coverage.get('totals', {}).get('percent_covered', 0):.1f}%",
                    "files_covered": len(coverage.get('files', {})),
                    "html_report": "tests/coverage_html/index.html"
                }
        except Exception:
            pass
        
        return {"status": "Coverage report not available"}


def main():
    """Main test runner entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BotArmy POC Integration Test Runner")
    parser.add_argument("--category", "-c", help="Run specific test category", 
                       choices=["api", "agents", "database", "realtime", "errors", "e2e", "performance", "consistency"])
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.category:
        exit_code = runner.run_specific_category(args.category)
    else:
        exit_code = runner.run_all_tests(
            verbose=not args.quiet,
            coverage=not args.no_coverage
        )
    
    if exit_code == 0:
        print("\n🎉 Integration testing completed successfully!")
        print("The BotArmy POC is ready for deployment.")
    else:
        print(f"\n💥 Integration testing failed with exit code {exit_code}")
        print("Please review the test failures above.")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

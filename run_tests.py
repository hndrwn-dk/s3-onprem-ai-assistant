#!/usr/bin/env python3
# run_tests.py - Comprehensive test runner for S3 AI Assistant v2.2.7

import subprocess
import sys
import os
import time
import json
import requests
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestRunner:
    """Comprehensive test runner for S3 AI Assistant"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.start_time = time.time()
        
    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{title:^60}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
        
    def print_test(self, test_name: str, status: str, details: str = ""):
        """Print test result"""
        if status == "PASS":
            print(f"{Colors.GREEN}[PASS]{Colors.END} {test_name}")
            if details:
                print(f"  {Colors.WHITE}{details}{Colors.END}")
            self.passed += 1
        elif status == "FAIL":
            print(f"{Colors.RED}[FAIL]{Colors.END} {test_name}")
            if details:
                print(f"  {Colors.RED}{details}{Colors.END}")
            self.failed += 1
        elif status == "SKIP":
            print(f"{Colors.YELLOW}[SKIP]{Colors.END} {test_name}")
            if details:
                print(f"  {Colors.YELLOW}{details}{Colors.END}")
        else:  # INFO
            print(f"{Colors.BLUE}[INFO]{Colors.END} {test_name}")
            if details:
                print(f"  {Colors.WHITE}{details}{Colors.END}")
    
    def run_command(self, command: str, timeout: int = 30) -> tuple:
        """Run shell command and return (success, output)"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, str(e)
    
    def check_file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        return Path(filepath).exists()
    
    def check_python_syntax(self, filepath: str) -> tuple:
        """Check Python file syntax"""
        success, output = self.run_command(f"python -m py_compile {filepath}")
        return success, output
    
    def run_pytest(self, test_path: str = "tests/") -> tuple:
        """Run pytest"""
        success, output = self.run_command(f"python -m pytest {test_path} -v --tb=short")
        return success, output
    
    def check_api_health(self, url: str = "http://localhost:8000") -> tuple:
        """Check API health endpoint"""
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return True, f"Status: {data.get('status', 'unknown')}, Version: {data.get('version', 'unknown')}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except requests.exceptions.RequestException as e:
            return False, str(e)
    
    def test_environment_setup(self):
        """Test environment and dependencies"""
        self.print_header("ENVIRONMENT SETUP")
        
        # Check Python version
        python_version = sys.version.split()[0]
        if sys.version_info >= (3, 8):
            self.print_test(f"Python Version {python_version}", "PASS", "Python 3.8+ required")
        else:
            self.print_test(f"Python Version {python_version}", "FAIL", "Python 3.8+ required")
        
        # Check required files
        required_files = [
            "api.py", "config.py", "validation.py", "model_cache.py",
            "utils.py", "response_cache.py", "bucket_index.py",
            "requirements.txt", "Dockerfile", "docker-compose.yml"
        ]
        
        for file in required_files:
            if self.check_file_exists(file):
                self.print_test(f"File exists: {file}", "PASS")
            else:
                self.print_test(f"File exists: {file}", "FAIL", f"Required file missing: {file}")
        
        # Check Python syntax
        python_files = [
            "api.py", "config.py", "validation.py", "model_cache.py",
            "utils.py", "response_cache.py", "bucket_index.py"
        ]
        
        for file in python_files:
            if self.check_file_exists(file):
                success, output = self.check_python_syntax(file)
                if success:
                    self.print_test(f"Syntax check: {file}", "PASS")
                else:
                    self.print_test(f"Syntax check: {file}", "FAIL", output)
            else:
                self.print_test(f"Syntax check: {file}", "SKIP", "File not found")
    
    def test_security_features(self):
        """Test security implementations"""
        self.print_header("SECURITY FEATURES")
        
        # Check validation module
        try:
            from validation import InputValidator, ValidationError, safe_query
            self.print_test("Import validation module", "PASS")
            
            # Test dangerous input detection
            try:
                safe_query("../../../etc/passwd")
                self.print_test("Directory traversal detection", "FAIL", "Should reject dangerous input")
            except ValidationError:
                self.print_test("Directory traversal detection", "PASS", "Properly rejects dangerous input")
            
            # Test XSS detection
            try:
                safe_query("<script>alert('xss')</script>")
                self.print_test("XSS detection", "FAIL", "Should reject script tags")
            except ValidationError:
                self.print_test("XSS detection", "PASS", "Properly rejects script tags")
                
        except ImportError as e:
            self.print_test("Import validation module", "FAIL", str(e))
        
        # Check model cache security
        try:
            from model_cache import ModelCache
            
            # Check if dangerous deserialization is disabled
            with open("model_cache.py", "r") as f:
                content = f.read()
                if "allow_dangerous_deserialization=False" in content:
                    self.print_test("Secure deserialization", "PASS", "Dangerous deserialization disabled")
                elif "allow_dangerous_deserialization=True" in content:
                    self.print_test("Secure deserialization", "FAIL", "Dangerous deserialization enabled")
                else:
                    self.print_test("Secure deserialization", "SKIP", "Could not determine setting")
                    
        except ImportError as e:
            self.print_test("Check model cache security", "FAIL", str(e))
    
    def test_configuration_management(self):
        """Test configuration features"""
        self.print_header("CONFIGURATION MANAGEMENT")
        
        try:
            from config import config, AppConfig
            self.print_test("Import config module", "PASS")
            
            # Test environment variable loading
            os.environ["S3AI_TEST_VAR"] = "test_value"
            test_config = AppConfig()
            self.print_test("Configuration object creation", "PASS")
            
            # Test validation
            try:
                from validation import InputValidator
                InputValidator.validate_config_value("test_int", 5, int)
                self.print_test("Configuration validation", "PASS")
            except Exception as e:
                self.print_test("Configuration validation", "FAIL", str(e))
                
        except ImportError as e:
            self.print_test("Import config module", "FAIL", str(e))
    
    def test_api_features(self):
        """Test API implementation"""
        self.print_header("API FEATURES")
        
        try:
            # Import API modules
            from api import app
            self.print_test("Import API module", "PASS")
            
            # Check if security middleware is present
            with open("api.py", "r") as f:
                content = f.read()
                
                security_features = [
                    ("Rate limiting", "limiter.limit"),
                    ("CORS middleware", "CORSMiddleware"),
                    ("Input validation", "safe_query"),
                    ("Error handling", "ValidationError"),
                    ("Trusted hosts", "TrustedHostMiddleware")
                ]
                
                for feature_name, feature_code in security_features:
                    if feature_code in content:
                        self.print_test(f"API security: {feature_name}", "PASS")
                    else:
                        self.print_test(f"API security: {feature_name}", "FAIL", f"Missing: {feature_code}")
                        
        except ImportError as e:
            self.print_test("Import API module", "FAIL", str(e))
    
    def test_docker_setup(self):
        """Test Docker configuration"""
        self.print_header("DOCKER SETUP")
        
        # Check Docker files
        docker_files = ["Dockerfile", "docker-compose.yml", ".dockerignore"]
        for file in docker_files:
            if self.check_file_exists(file):
                self.print_test(f"Docker file: {file}", "PASS")
            else:
                self.print_test(f"Docker file: {file}", "FAIL", f"Missing: {file}")
        
        # Check Docker syntax
        if self.check_file_exists("docker-compose.yml"):
            success, output = self.run_command("docker-compose config", timeout=10)
            if success:
                self.print_test("Docker Compose syntax", "PASS")
            else:
                self.print_test("Docker Compose syntax", "FAIL", output)
        
        # Check if Docker is available
        success, output = self.run_command("docker --version", timeout=5)
        if success:
            self.print_test("Docker availability", "PASS", output.strip())
        else:
            self.print_test("Docker availability", "SKIP", "Docker not available")
    
    def test_unit_tests(self):
        """Run unit tests"""
        self.print_header("UNIT TESTS")
        
        if self.check_file_exists("tests/"):
            success, output = self.run_pytest()
            if success:
                self.print_test("Unit tests", "PASS", "All tests passed")
            else:
                self.print_test("Unit tests", "FAIL", output)
        else:
            self.print_test("Unit tests", "SKIP", "Tests directory not found")
    
    def test_documentation(self):
        """Test documentation completeness"""
        self.print_header("DOCUMENTATION")
        
        doc_files = [
            ("README.md", "Main documentation"),
            ("DEPLOYMENT.md", "Deployment guide"), 
            ("CONTRIBUTING.md", "Contributing guide"),
            ("LICENSE", "License file")
        ]
        
        for file, description in doc_files:
            if self.check_file_exists(file):
                # Check file size (should not be empty)
                size = Path(file).stat().st_size
                if size > 100:  # At least 100 bytes
                    self.print_test(f"Documentation: {description}", "PASS", f"Size: {size} bytes")
                else:
                    self.print_test(f"Documentation: {description}", "FAIL", "File too small or empty")
            else:
                self.print_test(f"Documentation: {description}", "FAIL", f"Missing: {file}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"{Colors.BOLD}{Colors.BLUE}S3 On-Premises AI Assistant - Test Suite v2.2.7{Colors.END}")
        print(f"{Colors.WHITE}Security Enhanced & Production Ready{Colors.END}\n")
        
        # Run all test suites
        self.test_environment_setup()
        self.test_security_features()
        self.test_configuration_management()
        self.test_api_features()
        self.test_docker_setup()
        self.test_unit_tests()
        self.test_documentation()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_time = time.time() - self.start_time
        total_tests = self.passed + self.failed
        
        self.print_header("TEST SUMMARY")
        
        print(f"{Colors.WHITE}Total Tests: {total_tests}{Colors.END}")
        
        if self.passed > 0:
            print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        
        if self.failed > 0:
            print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        
        print(f"{Colors.WHITE}Duration: {total_time:.2f} seconds{Colors.END}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED! Ready for release!{Colors.END}")
            print(f"{Colors.GREEN}Security features implemented{Colors.END}")
            print(f"{Colors.GREEN}Production configuration ready{Colors.END}")
            print(f"{Colors.GREEN}Docker deployment available{Colors.END}")
            print(f"{Colors.GREEN}Comprehensive testing completed{Colors.END}")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}{self.failed} TEST(S) FAILED{Colors.END}")
            print(f"{Colors.YELLOW}Please fix the failing tests before release.{Colors.END}")
            return False

def main():
    """Main function"""
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
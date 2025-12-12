"""
Live System Health Diagnostic Tests

This module contains tests that check the live system health and can be run
against the running Lumen application to diagnose real-time issues.

These tests help identify:
1. API endpoint accessibility
2. Authentication flow issues
3. Photo display pipeline problems
4. Database connectivity in live environment
5. Frontend-backend integration issues

Perfect for debugging the user's current issue: "logged in but can't see photos"
"""

import pytest
import requests
import time
import logging
from unittest.mock import patch

logger = logging.getLogger(__name__)


@pytest.mark.diagnostics
@pytest.mark.live
@pytest.mark.external
class TestLiveSystemHealth:
    """Test live system health and accessibility"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.base_url = "http://100.106.201.33:8080"
        self.frontend_url = "http://100.106.201.33:8000"
        self.timeout = 10
        
    def test_backend_server_accessibility(self):
        """Test if backend server is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            print(f"Backend health check: {response.status_code}")
            
            if response.status_code == 404:
                # Try root endpoint if /health doesn't exist
                response = requests.get(f"{self.base_url}/", timeout=self.timeout)
                print(f"Backend root endpoint: {response.status_code}")
                
            assert response.status_code in [200, 404], f"Backend should be accessible, got {response.status_code}"
            print("✅ Backend server is accessible")
            
        except requests.ConnectionError:
            pytest.fail("❌ Backend server not accessible - check if server is running")
        except Exception as e:
            pytest.fail(f"Backend accessibility test failed: {e}")
    
    def test_frontend_server_accessibility(self):
        """Test if frontend server is running and accessible"""
        try:
            response = requests.get(self.frontend_url, timeout=self.timeout)
            assert response.status_code == 200, f"Frontend should be accessible, got {response.status_code}"
            print("✅ Frontend server is accessible")
            
        except requests.ConnectionError:
            pytest.fail("❌ Frontend server not accessible - check if server is running")
        except Exception as e:
            pytest.fail(f"Frontend accessibility test failed: {e}")
    
    def test_api_documentation_accessible(self):
        """Test if FastAPI docs are accessible"""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=self.timeout)
            if response.status_code == 200:
                print("✅ API documentation accessible at /docs")
            else:
                print(f"⚠️ API docs not accessible: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Could not access API docs: {e}")
    
    def test_photos_recent_endpoint_live(self):
        """Test /photos/recent endpoint on live system"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/photos/recent",
                timeout=self.timeout
            )
            
            print(f"Recent photos endpoint: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    photo_count = len(data.get('photos', []))
                    total_count = data.get('total_count', 0)
                    
                    print("✅ Recent photos endpoint working")
                    print(f"  Photos returned: {photo_count}")
                    print(f"  Total in database: {total_count}")
                    
                    if photo_count == 0:
                        print("⚠️ No photos returned - may indicate database/pipeline issue")
                    else:
                        # Check sample photo structure
                        sample_photo = data['photos'][0]
                        print(f"  Sample photo ID: {sample_photo.get('id', 'Missing')}")
                        print(f"  Sample title: {sample_photo.get('title', 'Missing')}")
                        
                        image_url = sample_photo.get('image_url', '')
                        if 'placeholder' in image_url.lower():
                            print("⚠️ Photos returning placeholder URLs - ID validation/GCS issue")
                        else:
                            print("✅ Photos returning real URLs")
                            
                except Exception as e:
                    print(f"⚠️ Response parsing failed: {e}")
                    print(f"Response content: {response.text[:200]}...")
                    
            elif response.status_code == 500:
                print("❌ Internal server error - likely database connection issue")
                print(f"Response: {response.text[:200]}...")
                
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.RequestException as e:
            pytest.fail(f"Photos endpoint request failed: {e}")
    
    def test_authenticated_endpoint_behavior(self):
        """Test behavior of authenticated endpoints without valid auth"""
        try:
            # Test my-photos endpoint without auth
            response = requests.get(
                f"{self.base_url}/api/v1/photos/my-photos",
                timeout=self.timeout
            )
            
            print(f"My-photos without auth: {response.status_code}")
            assert response.status_code == 401, "Should require authentication"
            
            # Test with fake token  
            response = requests.get(
                f"{self.base_url}/api/v1/photos/my-photos",
                headers={'Authorization': 'Bearer fake-token'},
                timeout=self.timeout
            )
            
            print(f"My-photos with fake token: {response.status_code}")
            assert response.status_code == 401, "Should reject fake token"
            
            print("✅ Authentication middleware working correctly")
            
        except Exception as e:
            pytest.fail(f"Authentication test failed: {e}")
    
    def test_cors_configuration(self):
        """Test CORS configuration for frontend-backend communication"""
        try:
            # Test preflight request
            response = requests.options(
                f"{self.base_url}/api/v1/photos/recent",
                headers={
                    'Origin': self.frontend_url,
                    'Access-Control-Request-Method': 'GET'
                },
                timeout=self.timeout
            )
            
            print(f"CORS preflight: {response.status_code}")
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            print("CORS headers:")
            for header, value in cors_headers.items():
                print(f"  {header}: {value}")
                
            if cors_headers['Access-Control-Allow-Origin']:
                print("✅ CORS configured")
            else:
                print("⚠️ CORS may not be properly configured")
                
        except Exception as e:
            print(f"⚠️ CORS test failed: {e}")


@pytest.mark.diagnostics
@pytest.mark.live
@pytest.mark.performance
class TestLiveSystemPerformance:
    """Test live system performance characteristics"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.base_url = "http://100.106.201.33:8080"
        self.timeout = 30  # Longer timeout for performance tests
        
    def test_api_response_times(self):
        """Test API endpoint response times"""
        endpoints = [
            "/api/v1/photos/recent",
            "/docs",
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    timeout=self.timeout
                )
                response_time = time.time() - start_time
                
                print(f"{endpoint}: {response.status_code} in {response_time:.3f}s")
                
                # Response should be reasonably fast
                if response_time > 10.0:
                    print(f"⚠️ Slow response: {response_time:.3f}s")
                else:
                    print(f"✅ Good response time: {response_time:.3f}s")
                    
            except Exception as e:
                print(f"❌ {endpoint} failed: {e}")
    
    def test_concurrent_requests(self):
        """Test system behavior under concurrent load"""
        import concurrent.futures
        import threading
        
        def make_request():
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/photos/recent?limit=5",
                    timeout=self.timeout
                )
                return response.status_code == 200
            except:
                return False
        
        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        success_count = sum(results)
        print(f"Concurrent requests: {success_count}/5 successful")
        
        if success_count >= 4:
            print("✅ System handles concurrent load well")
        else:
            print("⚠️ System may have concurrency issues")


@pytest.mark.diagnostics
@pytest.mark.live
@pytest.mark.integration
class TestFrontendBackendIntegration:
    """Test frontend-backend integration issues"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.base_url = "http://100.106.201.33:8080"
        self.frontend_url = "http://100.106.201.33:8000"
        
    def test_frontend_loads_correctly(self):
        """Test if frontend loads without errors"""
        try:
            response = requests.get(f"{self.frontend_url}/lumen-app.html")
            
            if response.status_code == 200:
                content = response.text
                
                # Check for critical frontend components
                checks = [
                    ('Firebase config', 'firebaseConfig' in content),
                    ('API base URL', '100.106.201.33:8080' in content),
                    ('Photo display JS', 'photo-display.js' in content),
                    ('App JS', 'app.js' in content),
                ]
                
                print("Frontend loading checks:")
                for check_name, passed in checks:
                    status = "✅" if passed else "⚠️"
                    print(f"  {status} {check_name}: {passed}")
                    
                all_passed = all(check[1] for check in checks)
                if all_passed:
                    print("✅ Frontend loads correctly")
                else:
                    print("⚠️ Frontend may have configuration issues")
                    
            else:
                print(f"❌ Frontend not accessible: {response.status_code}")
                
        except Exception as e:
            pytest.fail(f"Frontend loading test failed: {e}")
    
    def test_javascript_console_simulation(self):
        """Simulate common frontend JavaScript operations"""
        # This would typically be done with selenium, but we'll simulate the API calls
        try:
            # Simulate the calls that frontend would make
            
            # 1. Check recent photos (what home page loads)
            response = requests.get(f"{self.base_url}/api/v1/photos/recent?page=1&limit=20")
            print(f"Frontend simulation - recent photos: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Photos available for frontend: {len(data.get('photos', []))}")
                
                if len(data.get('photos', [])) == 0:
                    print("⚠️ Frontend would show empty gallery - no photos returned")
                else:
                    print("✅ Frontend should display photos")
                    
            # 2. Check CORS preflight (what browser does)
            response = requests.options(
                f"{self.base_url}/api/v1/photos/recent",
                headers={'Origin': self.frontend_url}
            )
            print(f"Frontend simulation - CORS preflight: {response.status_code}")
            
        except Exception as e:
            print(f"⚠️ Frontend simulation failed: {e}")


if __name__ == "__main__":
    # Allow running diagnostics directly with specific markers
    pytest.main([__file__, "-v", "-s", "-m", "live"])
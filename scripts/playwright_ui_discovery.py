#!/usr/bin/env python3
"""
Playwright UI Feature Discovery System
Automatically tests the local Lumen frontend to identify implemented features
and generate missing feature reports for UI specification development
"""

import sys
import os
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import requests

# Add backend path for database models
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    print("ERROR: Playwright not installed")
    print("Install with: pip install playwright")
    print("Then run: playwright install")
    sys.exit(1)


class PlaywrightUIDiscovery:
    """Discovers UI features and functionality using Playwright automation"""
    
    def __init__(self, base_url: str = "http://localhost:8000", backend_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.backend_url = backend_url
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.discovered_features = {
            "pages": [],
            "authentication": {},
            "photo_features": {},
            "user_features": {},
            "navigation": {},
            "forms": [],
            "missing_features": [],
            "errors_found": [],
            "performance": {}
        }
    
    async def setup(self):
        """Initialize Playwright browser and context"""
        print("Initializing Playwright browser...")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True
        )
        
        self.page = await self.context.new_page()
        
        # Set up console logging
        self.page.on("console", lambda msg: self.log_console(msg))
        self.page.on("pageerror", lambda error: self.log_error("JavaScript Error", str(error)))
        
        print("Playwright browser ready")
    
    def log_console(self, msg):
        """Log console messages from the browser"""
        if msg.type == "error":
            self.discovered_features["errors_found"].append({
                "type": "console_error",
                "message": msg.text,
                "timestamp": datetime.now().isoformat()
            })
    
    def log_error(self, error_type: str, message: str):
        """Log errors encountered during testing"""
        self.discovered_features["errors_found"].append({
            "type": error_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_basic_navigation(self):
        """Test basic navigation and page loading"""
        print("Testing basic navigation...")
        
        try:
            # Navigate to homepage
            start_time = time.time()
            response = await self.page.goto(self.base_url, wait_until="networkidle")
            load_time = time.time() - start_time
            
            self.discovered_features["performance"]["homepage_load"] = load_time
            
            if response and response.status == 200:
                self.discovered_features["pages"].append({
                    "url": self.base_url,
                    "title": await self.page.title(),
                    "status": "accessible",
                    "load_time": load_time
                })
            else:
                self.log_error("Navigation", f"Homepage returned status {response.status if response else 'No response'}")
                return False
            
            # Check for basic elements
            await self.discover_page_elements()
            
            return True
            
        except Exception as e:
            self.log_error("Basic Navigation", str(e))
            return False
    
    async def discover_page_elements(self):
        """Discover elements on the current page"""
        try:
            # Look for common UI elements
            elements = {
                "nav_bar": "nav, .navbar, .navigation",
                "login_button": "button[onclick*='login'], .login-btn, #login, [data-login]",
                "signup_button": "button[onclick*='signup'], .signup-btn, #signup, [data-signup]",
                "photo_gallery": ".gallery, .photo-grid, .photos, [data-photos]",
                "upload_button": "input[type='file'], .upload-btn, [data-upload]",
                "user_profile": ".profile, .user-info, [data-profile]",
                "search_input": "input[type='search'], .search-input, [data-search]",
                "forms": "form",
                "modals": ".modal, .popup, .dialog",
                "menus": ".menu, .dropdown"
            }
            
            page_elements = {}
            
            for element_type, selector in elements.items():
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        page_elements[element_type] = {
                            "found": True,
                            "selector": selector,
                            "visible": await element.is_visible(),
                            "text": (await element.inner_text())[:100] if element_type not in ["upload_button"] else "N/A"
                        }
                    else:
                        page_elements[element_type] = {"found": False}
                except Exception as e:
                    page_elements[element_type] = {"found": False, "error": str(e)}
            
            current_url = self.page.url
            if not any(page["url"] == current_url for page in self.discovered_features["pages"]):
                self.discovered_features["pages"][-1]["elements"] = page_elements
            
        except Exception as e:
            self.log_error("Element Discovery", str(e))
    
    async def test_authentication_flows(self):
        """Test authentication-related functionality"""
        print("Testing authentication flows...")
        
        try:
            # Look for login functionality
            login_selectors = [
                "button[onclick*='login']",
                ".login-btn", 
                "#login",
                "[data-login]",
                "button:has-text('Login')",
                "button:has-text('Sign In')"
            ]
            
            login_found = False
            for selector in login_selectors:
                login_element = await self.page.query_selector(selector)
                if login_element and await login_element.is_visible():
                    login_found = True
                    
                    self.discovered_features["authentication"]["login_button"] = {
                        "found": True,
                        "selector": selector,
                        "text": await login_element.inner_text()
                    }
                    
                    # Try clicking login button
                    try:
                        await login_element.click()
                        await self.page.wait_for_timeout(2000)
                        
                        # Check if login modal/form appeared
                        login_form = await self.page.query_selector("form, .login-form, .auth-form")
                        if login_form:
                            self.discovered_features["authentication"]["login_form"] = {
                                "found": True,
                                "has_email_field": bool(await self.page.query_selector("input[type='email'], input[name='email']")),
                                "has_password_field": bool(await self.page.query_selector("input[type='password'], input[name='password']")),
                                "has_submit_button": bool(await self.page.query_selector("button[type='submit'], .submit-btn"))
                            }
                        
                    except Exception as e:
                        self.log_error("Login Click", str(e))
                    
                    break
            
            if not login_found:
                self.discovered_features["authentication"]["login_button"] = {"found": False}
                self.discovered_features["missing_features"].append({
                    "category": "authentication",
                    "feature": "login_button",
                    "priority": "critical",
                    "description": "No login button found on homepage"
                })
            
            # Test signup functionality
            signup_selectors = [
                "button[onclick*='signup']",
                ".signup-btn",
                "#signup", 
                "[data-signup]",
                "button:has-text('Sign Up')",
                "button:has-text('Register')"
            ]
            
            signup_found = False
            for selector in signup_selectors:
                signup_element = await self.page.query_selector(selector)
                if signup_element and await signup_element.is_visible():
                    signup_found = True
                    self.discovered_features["authentication"]["signup_button"] = {
                        "found": True,
                        "selector": selector,
                        "text": await signup_element.inner_text()
                    }
                    break
            
            if not signup_found:
                self.discovered_features["authentication"]["signup_button"] = {"found": False}
                self.discovered_features["missing_features"].append({
                    "category": "authentication",
                    "feature": "signup_button", 
                    "priority": "critical",
                    "description": "No signup button found on homepage"
                })
                
        except Exception as e:
            self.log_error("Authentication Testing", str(e))
    
    async def test_photo_functionality(self):
        """Test photo-related features"""
        print("Testing photo functionality...")
        
        try:
            # Look for photo gallery
            gallery_selectors = [
                ".gallery",
                ".photo-grid",
                ".photos",
                "[data-photos]",
                ".image-container",
                "img[src*='photo'], img[src*='image']"
            ]
            
            gallery_found = False
            for selector in gallery_selectors:
                gallery = await self.page.query_selector(selector)
                if gallery:
                    gallery_found = True
                    
                    # Count photos in gallery
                    photos = await self.page.query_selector_all(f"{selector} img, img")
                    
                    self.discovered_features["photo_features"]["gallery"] = {
                        "found": True,
                        "selector": selector,
                        "photo_count": len(photos),
                        "visible": await gallery.is_visible()
                    }
                    break
            
            if not gallery_found:
                self.discovered_features["photo_features"]["gallery"] = {"found": False}
                self.discovered_features["missing_features"].append({
                    "category": "photos",
                    "feature": "photo_gallery",
                    "priority": "high",
                    "description": "No photo gallery found on homepage"
                })
            
            # Look for upload functionality
            upload_selectors = [
                "input[type='file']",
                ".upload-btn",
                "[data-upload]",
                "button:has-text('Upload')"
            ]
            
            upload_found = False
            for selector in upload_selectors:
                upload_element = await self.page.query_selector(selector)
                if upload_element:
                    upload_found = True
                    self.discovered_features["photo_features"]["upload"] = {
                        "found": True,
                        "selector": selector,
                        "type": "file_input" if selector == "input[type='file']" else "button",
                        "visible": await upload_element.is_visible()
                    }
                    break
            
            if not upload_found:
                self.discovered_features["photo_features"]["upload"] = {"found": False}
                self.discovered_features["missing_features"].append({
                    "category": "photos", 
                    "feature": "photo_upload",
                    "priority": "high",
                    "description": "No photo upload functionality found"
                })
                
        except Exception as e:
            self.log_error("Photo Testing", str(e))
    
    async def test_user_features(self):
        """Test user profile and social features"""
        print("Testing user features...")
        
        try:
            # Look for user profile elements
            profile_selectors = [
                ".profile",
                ".user-info", 
                "[data-profile]",
                ".user-card",
                ".avatar"
            ]
            
            profile_found = False
            for selector in profile_selectors:
                profile_element = await self.page.query_selector(selector)
                if profile_element and await profile_element.is_visible():
                    profile_found = True
                    self.discovered_features["user_features"]["profile"] = {
                        "found": True,
                        "selector": selector,
                        "visible": True
                    }
                    break
            
            if not profile_found:
                self.discovered_features["user_features"]["profile"] = {"found": False}
                self.discovered_features["missing_features"].append({
                    "category": "users",
                    "feature": "user_profile_display",
                    "priority": "medium",
                    "description": "No user profile display found"
                })
            
            # Look for search functionality
            search_selectors = [
                "input[type='search']",
                ".search-input",
                "[data-search]",
                "input[placeholder*='search']"
            ]
            
            search_found = False
            for selector in search_selectors:
                search_element = await self.page.query_selector(selector)
                if search_element:
                    search_found = True
                    self.discovered_features["user_features"]["search"] = {
                        "found": True,
                        "selector": selector,
                        "placeholder": await search_element.get_attribute("placeholder"),
                        "visible": await search_element.is_visible()
                    }
                    break
            
            if not search_found:
                self.discovered_features["user_features"]["search"] = {"found": False}
                self.discovered_features["missing_features"].append({
                    "category": "users",
                    "feature": "user_search",
                    "priority": "medium", 
                    "description": "No search functionality found"
                })
                
        except Exception as e:
            self.log_error("User Features Testing", str(e))
    
    async def test_navigation_menu(self):
        """Test navigation and menu functionality"""
        print("Testing navigation menu...")
        
        try:
            # Look for navigation elements
            nav_selectors = [
                "nav",
                ".navbar",
                ".navigation", 
                ".menu",
                ".nav-menu"
            ]
            
            nav_found = False
            for selector in nav_selectors:
                nav_element = await self.page.query_selector(selector)
                if nav_element and await nav_element.is_visible():
                    nav_found = True
                    
                    # Find navigation links
                    links = await nav_element.query_selector_all("a, button")
                    nav_items = []
                    
                    for link in links[:10]:  # Limit to first 10 links
                        text = await link.inner_text()
                        href = await link.get_attribute("href")
                        nav_items.append({
                            "text": text.strip(),
                            "href": href,
                            "visible": await link.is_visible()
                        })
                    
                    self.discovered_features["navigation"]["menu"] = {
                        "found": True,
                        "selector": selector,
                        "items": nav_items,
                        "item_count": len(nav_items)
                    }
                    break
            
            if not nav_found:
                self.discovered_features["navigation"]["menu"] = {"found": False}
                self.discovered_features["missing_features"].append({
                    "category": "navigation",
                    "feature": "navigation_menu",
                    "priority": "high",
                    "description": "No navigation menu found"
                })
                
        except Exception as e:
            self.log_error("Navigation Testing", str(e))
    
    async def scan_all_forms(self):
        """Scan and catalog all forms on the page"""
        print("Scanning forms...")
        
        try:
            forms = await self.page.query_selector_all("form")
            
            for i, form in enumerate(forms):
                form_data = {
                    "id": await form.get_attribute("id") or f"form_{i}",
                    "action": await form.get_attribute("action"),
                    "method": await form.get_attribute("method") or "GET",
                    "visible": await form.is_visible(),
                    "inputs": []
                }
                
                # Catalog form inputs
                inputs = await form.query_selector_all("input, textarea, select")
                for inp in inputs:
                    input_data = {
                        "type": await inp.get_attribute("type") or "text",
                        "name": await inp.get_attribute("name"),
                        "placeholder": await inp.get_attribute("placeholder"),
                        "required": await inp.get_attribute("required") is not None,
                        "visible": await inp.is_visible()
                    }
                    form_data["inputs"].append(input_data)
                
                self.discovered_features["forms"].append(form_data)
                
        except Exception as e:
            self.log_error("Form Scanning", str(e))
    
    async def check_responsive_design(self):
        """Test responsive design at different viewport sizes"""
        print("Testing responsive design...")
        
        try:
            viewports = [
                {"width": 375, "height": 667, "name": "mobile"},
                {"width": 768, "height": 1024, "name": "tablet"},
                {"width": 1920, "height": 1080, "name": "desktop"}
            ]
            
            responsive_results = {}
            
            for viewport in viewports:
                await self.page.set_viewport_size({
                    "width": viewport["width"],
                    "height": viewport["height"]
                })
                
                await self.page.wait_for_timeout(1000)  # Wait for layout adjustment
                
                # Check if key elements are still visible
                key_elements = [
                    "nav, .navbar",
                    "button, .btn",
                    ".gallery, .photos, img"
                ]
                
                viewport_results = {}
                for selector in key_elements:
                    elements = await self.page.query_selector_all(selector)
                    visible_count = 0
                    for el in elements:
                        if await el.is_visible():
                            visible_count += 1
                    
                    viewport_results[selector] = {
                        "total": len(elements),
                        "visible": visible_count
                    }
                
                responsive_results[viewport["name"]] = viewport_results
            
            self.discovered_features["navigation"]["responsive"] = responsive_results
            
            # Reset to desktop viewport
            await self.page.set_viewport_size({"width": 1280, "height": 720})
            
        except Exception as e:
            self.log_error("Responsive Testing", str(e))
    
    async def run_full_discovery(self):
        """Run complete UI feature discovery"""
        print("Starting comprehensive UI feature discovery...")
        print(f"Target: {self.base_url}")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            await self.setup()
            
            # Run discovery tests
            if await self.test_basic_navigation():
                await self.test_authentication_flows()
                await self.test_photo_functionality()
                await self.test_user_features()
                await self.test_navigation_menu()
                await self.scan_all_forms()
                await self.check_responsive_design()
            else:
                print("CRITICAL: Basic navigation failed, skipping other tests")
                return False
            
            total_time = time.time() - start_time
            self.discovered_features["performance"]["total_discovery_time"] = total_time
            
            print(f"Discovery completed in {total_time:.2f} seconds")
            return True
            
        except Exception as e:
            self.log_error("Full Discovery", str(e))
            return False
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
    
    def generate_feature_report(self) -> Dict[str, Any]:
        """Generate comprehensive feature discovery report"""
        
        # Categorize missing features by priority
        critical_missing = [f for f in self.discovered_features["missing_features"] if f.get("priority") == "critical"]
        high_missing = [f for f in self.discovered_features["missing_features"] if f.get("priority") == "high"]
        medium_missing = [f for f in self.discovered_features["missing_features"] if f.get("priority") == "medium"]
        
        # Count implemented features
        implemented_count = 0
        total_expected = 0
        
        feature_categories = ["authentication", "photo_features", "user_features", "navigation"]
        for category in feature_categories:
            if category in self.discovered_features:
                for feature, data in self.discovered_features[category].items():
                    total_expected += 1
                    if isinstance(data, dict) and data.get("found"):
                        implemented_count += 1
        
        implementation_percentage = (implemented_count / total_expected * 100) if total_expected > 0 else 0
        
        report = {
            "discovery_summary": {
                "timestamp": datetime.now().isoformat(),
                "target_url": self.base_url,
                "implementation_percentage": round(implementation_percentage, 1),
                "features_implemented": implemented_count,
                "features_expected": total_expected,
                "pages_tested": len(self.discovered_features["pages"]),
                "forms_found": len(self.discovered_features["forms"]),
                "errors_found": len(self.discovered_features["errors_found"])
            },
            "missing_features_by_priority": {
                "critical": critical_missing,
                "high": high_missing, 
                "medium": medium_missing
            },
            "detailed_findings": self.discovered_features,
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on discoveries"""
        recommendations = []
        
        # Authentication recommendations
        if not self.discovered_features.get("authentication", {}).get("login_button", {}).get("found"):
            recommendations.append("CRITICAL: Implement user authentication system with login/signup buttons")
        
        # Photo functionality recommendations  
        if not self.discovered_features.get("photo_features", {}).get("gallery", {}).get("found"):
            recommendations.append("HIGH: Create photo gallery display on homepage")
        
        if not self.discovered_features.get("photo_features", {}).get("upload", {}).get("found"):
            recommendations.append("HIGH: Add photo upload functionality")
        
        # Navigation recommendations
        if not self.discovered_features.get("navigation", {}).get("menu", {}).get("found"):
            recommendations.append("HIGH: Implement navigation menu system")
        
        # User experience recommendations
        if not self.discovered_features.get("user_features", {}).get("search", {}).get("found"):
            recommendations.append("MEDIUM: Add search functionality for photos/users")
        
        # Performance recommendations
        load_time = self.discovered_features.get("performance", {}).get("homepage_load", 0)
        if load_time > 3:
            recommendations.append(f"MEDIUM: Optimize homepage load time (currently {load_time:.2f}s)")
        
        # Error-based recommendations
        if self.discovered_features["errors_found"]:
            recommendations.append("MEDIUM: Fix JavaScript console errors for better user experience")
        
        return recommendations


def check_prerequisites() -> bool:
    """Check if required services are running"""
    services = {
        "Frontend": "http://localhost:8000",
        "Backend": "http://localhost:8080/health"
    }
    
    print("Checking prerequisites...")
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {service} is running")
            else:
                print(f"✗ {service} returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException:
            print(f"✗ {service} is not accessible at {url}")
            return False
    
    return True


def save_report(report: Dict[str, Any], filepath: str):
    """Save discovery report to file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to: {filepath}")


def print_summary(report: Dict[str, Any]):
    """Print summary of discovery results"""
    summary = report["discovery_summary"]
    missing = report["missing_features_by_priority"]
    
    print("\n" + "=" * 60)
    print("UI FEATURE DISCOVERY SUMMARY")
    print("=" * 60)
    print(f"Implementation Progress: {summary['implementation_percentage']}%")
    print(f"Features Found: {summary['features_implemented']}/{summary['features_expected']}")
    print(f"Pages Tested: {summary['pages_tested']}")
    print(f"Forms Found: {summary['forms_found']}")
    print(f"Errors Found: {summary['errors_found']}")
    
    print(f"\nMISSING FEATURES:")
    print(f"  Critical: {len(missing['critical'])}")
    print(f"  High: {len(missing['high'])}")
    print(f"  Medium: {len(missing['medium'])}")
    
    if missing['critical']:
        print(f"\nCRITICAL ISSUES:")
        for feature in missing['critical']:
            print(f"  • {feature['description']}")
    
    print(f"\nTOP RECOMMENDATIONS:")
    for rec in report["recommendations"][:5]:
        print(f"  • {rec}")
    
    print("\nFor detailed analysis, check the generated JSON report.")


async def main():
    """Main discovery function"""
    print("Playwright UI Feature Discovery System")
    print("=" * 50)
    
    if not check_prerequisites():
        print("CRITICAL: Required services not running")
        print("Start frontend: python3 -m http.server 8000")
        print("Start backend: python -m uvicorn app.main:app --reload --port 8080")
        return False
    
    # Create report directory
    report_dir = Path(__file__).parent.parent / "test-reports" / f"ui_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    report_path = report_dir / "feature_discovery.json"
    
    discovery = PlaywrightUIDiscovery()
    
    try:
        success = await discovery.run_full_discovery()
        
        if success:
            report = discovery.generate_feature_report()
            save_report(report, str(report_path))
            print_summary(report)
            
            print(f"\nUI Discovery completed successfully!")
            print(f"Detailed report: {report_path}")
            
            return True
        else:
            print("Discovery failed - check logs for details")
            return False
            
    except KeyboardInterrupt:
        print("\nDiscovery interrupted by user")
        return False
    except Exception as e:
        print(f"Discovery failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
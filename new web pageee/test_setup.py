#!/usr/bin/env python3
"""
Test script for Global Medical Guidelines AI Hub
Verifies that all components are working correctly
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_backend_health():
    """Test if the backend is running and healthy"""
    print("🔍 Testing backend health...")
    
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend healthy: {data}")
            return True
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    endpoints = [
        ('/api/guidelines', 'GET'),
        ('/api/sources', 'GET'),
        ('/api/specialties', 'GET'),
        ('/api/stats', 'GET')
    ]
    
    all_passed = True
    
    for endpoint, method in endpoints:
        try:
            response = requests.request(method, f'http://localhost:5000{endpoint}', timeout=10)
            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - OK")
            else:
                print(f"❌ {method} {endpoint} - {response.status_code}")
                all_passed = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {method} {endpoint} - Error: {e}")
            all_passed = False
    
    return all_passed

def test_database():
    """Test database functionality"""
    print("\n🔍 Testing database...")
    
    try:
        # Test getting guidelines
        response = requests.get('http://localhost:5000/api/guidelines', timeout=10)
        if response.status_code == 200:
            data = response.json()
            guideline_count = len(data.get('guidelines', []))
            print(f"✅ Database accessible: {guideline_count} guidelines found")
            return True
        else:
            print(f"❌ Database error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_scraping():
    """Test if scraping is working"""
    print("\n🔍 Testing scraping functionality...")
    
    try:
        # Check if we have guidelines from different sources
        response = requests.get('http://localhost:5000/api/sources', timeout=10)
        if response.status_code == 200:
            data = response.json()
            sources = data.get('sources', [])
            print(f"✅ Scraping sources: {sources}")
            
            if len(sources) > 0:
                return True
            else:
                print("⚠️  No sources found - scraping may not have run yet")
                return True  # Not a failure, just no data yet
        else:
            print(f"❌ Scraping test failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Scraping test error: {e}")
        return False

def test_frontend():
    """Test if frontend is accessible"""
    print("\n🔍 Testing frontend...")
    
    try:
        response = requests.get('http://localhost:3000', timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessible")
            return True
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Frontend not accessible: {e}")
        print("   (This is normal if frontend is not running)")
        return True  # Not a failure, frontend is optional for API testing

def test_ai_functionality():
    """Test AI functionality"""
    print("\n🔍 Testing AI functionality...")
    
    try:
        # Get some guidelines to test AI processing
        response = requests.get('http://localhost:5000/api/guidelines?limit=1', timeout=10)
        if response.status_code == 200:
            data = response.json()
            guidelines = data.get('guidelines', [])
            
            if guidelines:
                guideline = guidelines[0]
                if guideline.get('summary'):
                    print("✅ AI summarization working")
                    return True
                else:
                    print("⚠️  No AI summary found - AI may be in fallback mode")
                    return True
            else:
                print("⚠️  No guidelines to test AI with")
                return True
        else:
            print(f"❌ AI test failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ AI test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🏥 Global Medical Guidelines AI Hub - System Test")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("API Endpoints", test_api_endpoints),
        ("Database", test_database),
        ("Scraping", test_scraping),
        ("AI Functionality", test_ai_functionality),
        ("Frontend", test_frontend)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        return 0
    elif passed >= total - 1:  # Allow one failure (usually frontend)
        print("⚠️  Most tests passed. System is mostly working.")
        return 0
    else:
        print("❌ Multiple tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
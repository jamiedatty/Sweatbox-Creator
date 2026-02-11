#!/usr/bin/env python3
"""
Test script to verify web map functionality works correctly.
"""

import sys
import os
# Set test environment to use dummy map widget
os.environ['PYTEST_CURRENT_TEST'] = '1'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_web_map_imports():
    """Test that web map dependencies are available"""
    print("Testing web map imports...")

    try:
        from flask import Flask
        print("✓ Flask available")
    except ImportError:
        print("✗ Flask not available")
        return False

    try:
        import folium
        print("✓ Folium available")
    except ImportError:
        print("✗ Folium not available")
        return False

    try:
        import tkinterweb
        print("✓ tkinterweb available")
    except ImportError:
        print("✗ tkinterweb not available")
        return False

    return True

def test_sweatbox_map_web_features():
    """Test that SweatboxMapViewer has web map features"""
    print("\nTesting SweatboxMapViewer web features...")

    try:
        from modules.ui.viewers.sweatbox_map import WEB_MAP_AVAILABLE, TKINTERWEB_AVAILABLE
        print(f"✓ WEB_MAP_AVAILABLE: {WEB_MAP_AVAILABLE}")
        print(f"✓ TKINTERWEB_AVAILABLE: {TKINTERWEB_AVAILABLE}")

        if not WEB_MAP_AVAILABLE:
            print("✗ Web map not available - Flask/Folium missing")
            return False

        if not TKINTERWEB_AVAILABLE:
            print("✗ tkinterweb not available - embedded web view disabled")
            return False

        return True
    except ImportError as e:
        print(f"✗ Could not import SweatboxMapViewer: {e}")
        return False

def test_web_map_generation():
    """Test that web map HTML generation works"""
    print("\nTesting web map HTML generation...")

    try:
        from modules.ui.viewers.sweatbox_map import SweatboxMapViewer

        # Create a minimal viewer for testing
        class MockParent:
            def __init__(self):
                self.master = None
                self.tk = None
                self._last_child_ids = {}

        parent = MockParent()
        viewer = SweatboxMapViewer(parent)

        # Test HTML generation
        html = viewer.generate_web_map_html()
        if html and len(html) > 100:
            print("✓ Web map HTML generated successfully")
            print(f"  HTML length: {len(html)} characters")
            return True
        else:
            print("✗ Web map HTML generation failed")
            return False

    except Exception as e:
        print(f"✗ Error testing web map generation: {e}")
        return False

if __name__ == "__main__":
    print("Running web map tests...\n")

    tests_passed = 0
    total_tests = 3

    if test_web_map_imports():
        tests_passed += 1

    if test_sweatbox_map_web_features():
        tests_passed += 1

    if test_web_map_generation():
        tests_passed += 1

    print(f"\nResults: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("✓ All web map tests passed!")
    else:
        print("✗ Some web map tests failed.")

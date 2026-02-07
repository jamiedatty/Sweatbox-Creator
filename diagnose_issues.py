import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=== DIAGNOSTIC CHECK ===")

# Check tkintermapview
try:
    from tkintermapview import TkinterMapView
    print("✓ tkintermapview is installed")
except ImportError:
    print("✗ tkintermapview is NOT installed")
    print("  Run: pip install tkintermapview")

# Check SCT parser
try:
    from modules.parsers.sct_parser_simple import SCTParser
    print("✓ SCTParser module is available")
    
    # Test parsing
    test_file = "test.sct"
    if os.path.exists(test_file):
        parser = SCTParser(test_file)
        data = parser.parse()
        print(f"✓ Test SCT file parsed: {len(data.get('airports', []))} airports")
        print(f"  Airports: {[a.get('icao', 'N/A') for a in data.get('airports', [])]}")
        print(f"  Fixes: {len(data.get('fixes', []))}")
        print(f"  ARTCC HIGH: {len(data.get('ARTCC_HIGH', []))}")
        print(f"  ARTCC LOW: {len(data.get('ARTCC_LOW', []))}")
    else:
        print(f"  Note: Test file {test_file} not found")
        
except Exception as e:
    print(f"✗ SCTParser error: {e}")

# Check map viewer
try:
    from modules.ui.viewers.sweatbox_map import SweatboxMapViewer
    print("✓ SweatboxMapViewer module is available")
except Exception as e:
    print(f"✗ SweatboxMapViewer error: {e}")

print("\n=== RECOMMENDED ACTIONS ===")
print("1. Run: pip install --upgrade tkintermapview")
print("2. Create test.sct file with sample data")
print("3. Run test_sct_and_map.py to verify")
print("4. Check console for debug output")
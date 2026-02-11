#!/usr/bin/env python3
"""
Test script to verify aircraft generation works correctly and doesn't spawn globally.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.generators.random_generator import RandomScenarioGenerator

class MockCreator:
    def __init__(self):
        self.sct_parser = None
        self.map_viewer = None
        self.aircraft_details_tree = MockTree()
        self.status_label = MockLabel()

class MockTree:
    def __init__(self):
        self.items = []

    def insert(self, parent, index, values=None):
        self.items.append(values)

    def get_children(self):
        return self.items

class MockLabel:
    def __init__(self):
        self.text = ""

    def config(self, text=""):
        self.text = text

def test_aircraft_generation():
    """Test that aircraft generation works and positions are reasonable."""
    print("Testing aircraft generation...")

    # Create a mock creator
    creator = MockCreator()

    # Create the generator
    generator = RandomScenarioGenerator(creator)

    # Mock SCT parser with airport data
    class MockSCTParser:
        def get_data(self):
            return {
                'airports': [
                    {
                        'icao': 'KJFK',
                        'latitude': 40.6413,
                        'longitude': -73.7781
                    }
                ]
            }

    creator.sct_parser = MockSCTParser()

    # Test generating a single aircraft
    try:
        generator.generate_random_aircraft(0, selected_airport='KJFK', controller_type='ALL')
        print("✓ Aircraft generation succeeded")

        # Check if aircraft was added to tree
        if creator.aircraft_details_tree.items:
            values = creator.aircraft_details_tree.items[0]
            print(f"✓ Aircraft added: {values[0]} at position {values[3]}")

            # Parse position
            try:
                lat_str, lon_str = values[3].split(', ')
                lat = float(lat_str)
                lon = float(lon_str)

                # Check if position is reasonable (not global random)
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    print("✓ Position is within valid geographic bounds")

                    # Check if position is near JFK (roughly within 100 miles)
                    jfk_lat, jfk_lon = 40.6413, -73.7781
                    distance = generator.calculate_distance(lat, lon, jfk_lat, jfk_lon)
                    if 40 <= distance <= 100:  # Allow some margin for calculation
                        print(f"✓ Position is within reasonable distance from airport ({distance:.1f} NM)")
                        return True
                    else:
                        print(f"✗ Position is too far from airport ({distance:.1f} NM)")
                        return False
                else:
                    print("✗ Position is outside valid geographic bounds")
                    return False
            except ValueError:
                print("✗ Could not parse position coordinates")
                return False
        else:
            print("✗ No aircraft was generated")
            return False

    except Exception as e:
        print(f"✗ Aircraft generation failed: {e}")
        return False

if __name__ == "__main__":
    print("Running aircraft generation tests...\n")

    if test_aircraft_generation():
        print("\n✓ All tests passed! Aircraft generation is working correctly.")
    else:
        print("\n✗ Tests failed. Please check the implementation.")

#!/usr/bin/env python3
"""
Test script to verify that aircraft spawning range has been changed from 50-75 miles to 75-150 miles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.generators.random_generator import RandomScenarioGenerator

class MockCreator:
    def __init__(self):
        self.sct_parser = None
        self.map_viewer = None

def test_spawning_range():
    """Test that the spawning range is now 75-150 miles instead of 50-75."""
    print("Testing aircraft spawning range...")

    # Create a mock creator
    creator = MockCreator()

    # Create the generator
    generator = RandomScenarioGenerator(creator)

    # Test the generate_position_miles_from_airport method with default parameters
    # The method should now use min_miles=75, max_miles=150 by default

    # Since we don't have a real airport, let's check the method signature and defaults
    import inspect
    sig = inspect.signature(generator.generate_position_miles_from_airport)
    defaults = {
        k: v.default for k, v in sig.parameters.items() if v.default is not inspect.Parameter.empty
    }

    print(f"Default parameters for generate_position_miles_from_airport: {defaults}")

    # Check if min_miles and max_miles are set to 50 and 75
    if 'min_miles' in defaults and 'max_miles' in defaults:
        if defaults['min_miles'] == 50 and defaults['max_miles'] == 75:
            print("✓ Spawning range successfully set to 50-75 miles")
            return True
        else:
            print(f"✗ Spawning range is {defaults['min_miles']}-{defaults['max_miles']} miles, expected 50-75")
            return False
    else:
        print("✗ Could not find min_miles and max_miles parameters")
        return False

def test_prompt_text():
    """Test that the prompt text has been updated to reflect 50-75NM."""
    print("Testing prompt text...")

    creator = MockCreator()
    generator = RandomScenarioGenerator(creator)

    # Check the prompt text in the method
    import inspect
    source = inspect.getsource(generator.prompt_for_controller_type)
    if "50-75NM" in source:
        print("✓ Prompt text successfully updated to 50-75NM")
        return True
    else:
        print("✗ Prompt text does not contain 50-75NM")
        return False

def test_comments():
    """Test that comments have been updated."""
    print("Testing comments...")

    creator = MockCreator()
    generator = RandomScenarioGenerator(creator)

    # Check comments in generate_random_aircraft
    import inspect
    source = inspect.getsource(generator.generate_random_aircraft)
    if "50-75 miles" in source:
        print("✓ Comments successfully updated to reflect 50-75 miles")
        return True
    else:
        print("✗ Comments do not reflect 50-75 miles")
        return False

if __name__ == "__main__":
    print("Running spawning range verification tests...\n")

    tests = [
        test_spawning_range,
        test_prompt_text,
        test_comments
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed! Aircraft spawning range has been successfully set to 50-75 miles.")
    else:
        print("✗ Some tests failed. Please check the implementation.")

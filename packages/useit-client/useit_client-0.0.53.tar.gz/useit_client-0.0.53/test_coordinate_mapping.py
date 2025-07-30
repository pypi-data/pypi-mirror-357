#!/usr/bin/env python3
"""
Test script to verify coordinate mapping between animation and actual clicks 
in WebRDP environment.

Run this script to test if the animation position matches the actual click position.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from computer_use_ootb_internal.computer_use_demo.tools.computer import ComputerTool

def test_webrdp_coordinates():
    """Test coordinate mapping in WebRDP environment"""
    print("=== WebRDP Coordinate Mapping Test ===")
    
    # Create computer tool instance
    computer = ComputerTool(selected_screen=0, is_scaling=False)
    
    # Test points within the 1920x1080 WebRDP area
    test_points = [
        (100, 100),    # Top-left area
        (960, 540),    # Center
        (1800, 980),   # Bottom-right area  
        (500, 300),    # Random point 1
        (1200, 700),   # Random point 2
    ]
    
    print(f"WebRDP working area: {computer.width}x{computer.height}")
    print(f"Screen bbox: {computer.bbox}")
    
    success_count = 0
    total_tests = len(test_points)
    
    for i, (x, y) in enumerate(test_points):
        print(f"\n--- Test {i+1}/{total_tests}: Point ({x}, {y}) ---")
        
        try:
            # Test the coordinate mapping
            success = computer.test_coordinate_mapping(x, y)
            if success:
                success_count += 1
                print(f"✓ Test {i+1} PASSED")
            else:
                print(f"✗ Test {i+1} FAILED")
                
        except Exception as e:
            print(f"✗ Test {i+1} ERROR: {e}")
        
        # Wait a bit between tests
        import time
        time.sleep(1)
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {success_count}/{total_tests}")
    print(f"Success rate: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print("✓ All tests passed! Coordinate mapping is working correctly.")
    else:
        print("✗ Some tests failed. There may be coordinate mapping issues.")
        print("\nTroubleshooting tips:")
        print("1. Check if Windows display scaling is affecting coordinates")
        print("2. Verify WebRDP resolution settings")
        print("3. Ensure pyautogui is using the correct coordinate system")
    
    return success_count == total_tests

if __name__ == "__main__":
    test_webrdp_coordinates() 
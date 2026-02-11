#!/usr/bin/env python3
"""
macOS Compatibility Module for Sweatbox Creator
Provides utilities to ensure consistent color rendering across macOS versions
"""

import sys
import platform

def is_macos():
    """Check if running on macOS"""
    return platform.system() == 'Darwin'

def get_macos_version():
    """Get macOS version tuple (major, minor)"""
    if not is_macos():
        return None
    version = platform.mac_ver()[0]
    try:
        parts = version.split('.')
        return (int(parts[0]), int(parts[1]))
    except:
        return (10, 0)

def setup_macos_colors():
    """
    Apply color fixes specific to macOS.
    Returns a dictionary of compatible colors.
    """
    if not is_macos():
        return None
    
    # macOS-compatible color palette
    return {
        # Background colors
        'background': '#F5F5F7',
        'surface': '#FFFFFF',
        'surface_alternate': '#F0F0F2',
        
        # Primary colors
        'primary': '#007AFF',
        'primary_dark': '#0056B3',
        'primary_light': '#5AC8FA',
        
        # Status colors
        'success': '#34C759',
        'success_dark': '#248A3D',
        'warning': '#FF9500',
        'danger': '#FF3B30',
        'info': '#00C7BE',
        
        # Text colors
        'text': '#1D1D1F',
        'text_secondary': '#86868B',
        'text_hint': '#AEAEB2',
        
        # UI element colors
        'border': '#D2D2D7',
        'divider': '#E5E5EA',
        'shadow': '#00000020',
        
        # Gradient colors
        'gradient_start': '#007AFF',
        'gradient_end': '#5AC8FA',
        
        # Special colors
        'accent': '#007AFF',
        'highlight': '#34C759',
        
        # Status bar colors
        'status_background': '#2C2C2E',
        'status_text': '#FFFFFF',
        'status_indicator': '#30D158',
        
        # Card colors
        'card_background': '#FFFFFF',
        'card_border': '#D2D2D7',
        
        # White
        'white': '#FFFFFF',
    }

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def adjust_brightness(hex_color, factor):
    """Adjust the brightness of a hex color"""
    rgb = hex_to_rgb(hex_color)
    adjusted = tuple(min(255, max(0, int(c * factor))) for c in rgb)
    return rgb_to_hex(adjusted)

def get_contrasting_color(hex_color):
    """Get contrasting text color (black or white) for a background"""
    rgb = hex_to_rgb(hex_color)
    luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
    return '#000000' if luminance > 0.5 else '#FFFFFF'

if __name__ == "__main__":
    print(f"Running on macOS: {is_macos()}")
    print(f"macOS version: {get_macos_version()}")
    colors = setup_macos_colors()
    if colors:
        print(f"Loaded {len(colors)} macOS colors")

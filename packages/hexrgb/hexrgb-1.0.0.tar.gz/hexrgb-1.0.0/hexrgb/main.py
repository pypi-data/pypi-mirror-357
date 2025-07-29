#!/usr/bin/env python3
# hexrgb/main.py — CLI tool to convert HEX to RGB (standalone)

import argparse
import re
import sys

# Constants
HEX_REGEX = r"^[0-9A-Fa-f]{6}$"
INVALID_HEX_FORMAT = (
    "Error: Invalid HEX format.\n"
    "Expected: 6-digit HEX value (e.g., #FFAABB or FFAABB).\n"
    "Note: Only characters 0-9 and A-F are allowed."
)
MISSING_HEX_VALUE = "Error: You must provide a HEX value using --hex-to-rgb."
VERSION = (
    "hexrgb v1.0.0\n"
    "Author : Mallik Mohammad Musaddiq\n"
    "GitHub : https://github.com/mallikmusaddiq1/hexrgb\n"
    "Email  : mallikmusaddiq1@gmail.com"
)

# Conversion logic
def hex_to_rgb(hex_color):
    """Convert a HEX color string to an (R, G, B) tuple."""
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)

# Main CLI handler
def main():
    parser = argparse.ArgumentParser(
        prog="hexrgb",
        description="Convert HEX color code to RGB format (e.g., #FFAA33 → 255,170,51)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True
    )

    parser.add_argument(
        "--hex-to-rgb",
        metavar="HEX",
        help="HEX color code to convert (e.g., #FFAA33 or FFAA33)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=VERSION,
        help="Show version and author info"
    )

    args = parser.parse_args()

    if not args.hex_to_rgb:
        print(MISSING_HEX_VALUE)
        sys.exit(1)

    hex_color = args.hex_to_rgb.strip().lstrip("#")

    if not re.fullmatch(HEX_REGEX, hex_color):
        print(INVALID_HEX_FORMAT)
        sys.exit(1)

    rgb = hex_to_rgb(hex_color)
    print(f"RGB: {rgb[0]},{rgb[1]},{rgb[2]}")

if __name__ == "__main__":
    main()
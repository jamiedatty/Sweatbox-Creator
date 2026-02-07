import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.parsers.sct_parser_simple import SCTParser

# Test with your SCT file
parser = SCTParser("test.sct")  # Replace with actual file
data = parser.parse()

# Check boundary structure
if 'ARTCC_HIGH' in data and data['ARTCC_HIGH']:
    print(f"Found {len(data['ARTCC_HIGH'])} ARTCC HIGH boundaries")
    sample = data['ARTCC_HIGH'][0]
    print(f"Sample boundary: {sample.get('name')}")
    if 'segments' in sample and sample['segments']:
        sample_seg = sample['segments'][0]
        print(f"Sample segment start: {sample_seg.get('start')}")
        print(f"Sample segment end: {sample_seg.get('end')}")

if 'airports' in data:
    print(f"\nFound {len(data['airports'])} airports")
    if data['airports']:
        sample_airport = data['airports'][0]
        print(f"Sample airport: {sample_airport}")
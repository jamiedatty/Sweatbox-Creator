import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from modules.parsers.sct_parser_simple import SCTParser

p=SCTParser('test_sample.sct')
data=p.parse()
print('Airports', len(data.get('airports',[])))
print('Fixes', len(data.get('fixes',[])))
print('Runways', len(data.get('runways',[])))
print('VOR', len(data.get('VOR',[])))

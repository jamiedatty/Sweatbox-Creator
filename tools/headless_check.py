import os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
# Force dummy map widget
os.environ['PYTEST_CURRENT_TEST']='1'
from modules.parsers.sct_parser_simple import SCTParser
from modules.ui.viewers.sweatbox_map import SweatboxMapViewer
p = SCTParser('test_sample.sct')
data = p.parse()
print('AIRPORTS:')
for a in data.get('airports',[]):
    print(a)

# Instantiate dummy map viewer and load data
import tkinter as tk
root = tk.Tk()
root.withdraw()
viewer = SweatboxMapViewer(root, None, p, None)
viewer.debug = True
viewer.load_data()
print('Markers:', len(viewer.map_markers))

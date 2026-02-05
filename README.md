Sweatbox File Viewer/Creator

A Python tkinter-based GUI application for viewing and analyzing EuroScope Sector Files (.ese) and Sector Files (.sct).

## Features

### File Loading
- Load ESE (EuroScope Sector) files
- Load SCT (Sector) files for additional data
- Optional SCT file loading for airspace information

### Views
1. **Map View** (Interactive):
   - Real map display using OpenStreetMap
   - Controller positions with color coding
   - Airports, VORs, NDBs, and fixes
   - Airspace classes (A-G) with adjustable transparency
   - Airways (high and low)
   - Interactive tooltips and popups
   - Zoom and pan functionality
   - Multiple base map layers

2. **Aircraft View**:
   - SIDs/STARs display grouped by airport
   - Procedure counts and names
   - Placeholder for future aircraft management features

3. **Controllers View**:
   - Filterable table of controller positions
   - Search by callsign, name, frequency, or type
   - Color-coded by position type
   - Export to CSV functionality
   - Double-click for detailed view

## Installation

1. Install Python 3.7 or higher
2. Install required packages:
```bash
pip install -r requirements.txt
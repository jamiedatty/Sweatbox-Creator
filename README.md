# ESE File Viewer Application

A Python tkinter-based GUI application for viewing and analyzing .ese (EuroScope Sector File) files.

## Features

### Home Page
- **Create**: Load and analyze an ESE file
- **Import**: Future feature (currently shows "Not available yet" message)

### Create Page Features
After loading an ESE file, you can access:

1. **Map View**: 
   - Visual representation of controller positions
   - Color-coded by position type (Tower/Ground, Approach, Center, ATIS)
   - Interactive tooltips showing position details
   - Coordinate grid overlay

2. **Aircraft View**:
   - Displays SIDs/STARs grouped by airport
   - Shows procedure counts and names
   - Future: Will include flight plan management

3. **Controllers View**:
   - Searchable table of all controller positions
   - Filter by position type (TWR, GND, APP, CTR, ATIS, DEL)
   - Statistics summary

4. **Master Pseudo-controller Entry**:
   - Text field for entering master pseudo-controller information

## File Structure

```
main.py                 - Application entry point
home_page.py           - Home page with Create/Import buttons
create_page.py         - Main viewing page with navigation
ese_parser.py          - ESE file parser
map_viewer.py          - Map visualization component
aircraft_viewer.py     - Aircraft/SIDs/STARs viewer
controller_viewer.py   - Controller positions table viewer
```

## Installation & Running

### Requirements
- Python 3.x
- tkinter (usually comes with Python)

### Run the Application
```bash
python main.py
```

## Usage

1. Launch the application
2. Click "Create" on the home page
3. Select an ESE file when prompted
4. Navigate between Map, Aircraft, and Controllers views using the top menu buttons
5. Use filters and interact with the data as needed

## ESE File Format

The application parses standard EuroScope Sector Files (.ese) which contain:
- `[POSITIONS]` - Controller positions with frequencies and coordinates
- `[SIDSSTARS]` - Standard Instrument Departures and Arrivals
- `[AIRSPACE]` - Airspace definitions
- `[RADAR]` - Radar coverage areas
- `[FREETEXT]` - Additional text annotations

## Color Coding (Map View)

- **Red**: Tower/Ground/Delivery positions
- **Orange**: Approach/Departure positions
- **Blue**: Center positions
- **Grey**: ATIS and other positions

## Future Enhancements

- Full panning and zooming on the map
- Import functionality
- Export capabilities
- More detailed aircraft information
- Route visualization
- Real-time position tracking
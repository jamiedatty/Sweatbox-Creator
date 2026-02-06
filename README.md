# Sweatbox Creator

A comprehensive application for creating VATSIM sweatbox training scenarios with ESE, SCT, and RWY file support.

## Features

- **File Processing**: Parses ESE (controller schedules), SCT (sector/airport data), and RWY (runway) files
- **Interactive Mapping**: Real-time geographic display with zoom/pan controls
- **Multi-Airport Management**: Control multiple airports with automatic ICAO extraction
- **Aircraft Generation**: Manual, automatic at entry fixes, and random realistic generation
- **Controller Management**: Import positions from ESE files, manage frequencies
- **Runway Visualization**: Extended runway centerlines (10 miles both directions)
- **Entry Fix Detection**: Automatically identifies fixes within 100NM radius
- **Three-Panel Interface**: Controls, interactive map, detailed lists
- **Export System**: Generates standard sweatbox format files
- **Drag & Drop Aircraft**: Move aircraft directly on the map with mouse

## Installation

1. Install Python 3.8 or higher
2. Extract this project
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
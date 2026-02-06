import os
from datetime import datetime

class SweatboxExporter:
    def __init__(self, creator):
        self.creator = creator
    
    def export(self, file_path):
        """Export sweatbox file"""
        content = self.generate_sweatbox_content()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Exported to {file_path}"
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def generate_sweatbox_content(self):
        """Generate sweatbox file content"""
        lines = []
        
        # Header comment
        lines.append("; Sweatbox File")
        lines.append(f"; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"; Master Controller: {self.creator.master_controller}")
        lines.append("")
        
        # Master controller
        lines.append(f"PSEUDOPILOT:{self.creator.master_controller}")
        lines.append("")
        
        # Airport altitude
        lines.append("AIRPORT_ALT:5558.0")
        lines.append("")
        
        # ILS definitions from RWY file
        if hasattr(self.creator, 'rwy_parser') and self.creator.rwy_parser and hasattr(self.creator.rwy_parser, 'ils_data'):
            lines.append("; ILS Definitions")
            for ils in self.creator.rwy_parser.ils_data:
                glideslope_lat, glideslope_lon = ils['glideslope']
                localizer_lat, localizer_lon = ils['localizer']
                lines.append(f"{ils['name']}:{glideslope_lat}:{glideslope_lon}:{localizer_lat}:{localizer_lon}")
            lines.append("")
        
        # Controllers
        lines.append("; Controllers")
        simulated_controllers = self.creator.get_simulated_controllers()
        
        for controller in simulated_controllers:
            lines.append(f"PSEUDOPILOT:{self.creator.master_controller}")
            lines.append(f"CONTROLLER:{controller['callsign']}:{controller['frequency']}")
        
        if simulated_controllers:
            lines.append("")
        
        # Aircraft
        lines.append("; Aircraft")
        aircraft_count = 0
        
        for item in self.creator.aircraft_details_tree.get_children():
            values = self.creator.aircraft_details_tree.item(item, 'values')
            if values and len(values) >= 5:
                aircraft_count += 1
                callsign, ac_type, altitude, position, route = values[:5]
                
                # Parse position
                try:
                    if ',' in position:
                        lat_str, lon_str = position.split(',')
                        lat = float(lat_str.strip())
                        lon = float(lon_str.strip())
                    else:
                        lat, lon = -26.145, 28.234  # Default FAOR
                except:
                    lat, lon = -26.145, 28.234  # Default FAOR
                
                # Clean altitude
                alt_clean = altitude.replace('ft', '').strip()
                
                # Get speed and heading if available
                speed = "250"
                heading = "000"
                if len(values) >= 7:
                    speed = values[5] if values[5] else "250"
                    heading = values[6] if values[6] else "000"
                
                # Generate aircraft entry in sweatbox format
                lines.append(f"PSEUDOPILOT:{self.creator.master_controller}")
                lines.append(f"@N:{callsign}:{aircraft_count:04d}:1:{lat}:{lon}:{alt_clean}:0:0:0")
                lines.append(f"$FP{callsign}:*A:I:{ac_type}:420:::{alt_clean}:::00:00:0:0::")
                
                # Add route with speed/heading if specified
                if speed != "250" or heading != "000":
                    route_line = f"$ROUTE:{route}"
                    lines.append(route_line)
                else:
                    lines.append(f"$ROUTE:{route}")
                
                lines.append(f"INITIALPSEUDOPILOT:{self.creator.master_controller}")
                lines.append("")
        
        return '\n'.join(lines)
    
    def generate_euroscope_comment(self, aircraft_data):
        """Generate EuroScope comment format for aircraft"""
        # EuroScope comment format: ;callsign:field1:field2:...
        # Example: ;SAA123:ALT:FL350:SPD:480:HDG:270
        callsign = aircraft_data.get('callsign', '')
        altitude = aircraft_data.get('altitude', '').replace('ft', '')
        speed = aircraft_data.get('speed', '250')
        heading = aircraft_data.get('heading', '000')
        
        comment = f";{callsign}:ALT:{altitude}:SPD:{speed}:HDG:{heading}"
        
        # Add route if available
        route = aircraft_data.get('route', '')
        if route:
            comment += f":ROUTE:{route}"
        
        return comment
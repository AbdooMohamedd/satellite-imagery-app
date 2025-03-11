import datetime
from geopy.distance import geodesic
from datetime import datetime as dt, timedelta
import re
import numpy as np
import os
from shapely.geometry import Polygon, Point, box, LineString
import math

def convert_coordinates(lat, lon):
    # Convert latitude and longitude to a different coordinate system if needed
    return (lat, lon)

def calculate_distance(coord1, coord2):
    # Calculate the distance between two geographical coordinates
    return geodesic(coord1, coord2).kilometers

def find_gaza_coordinates_file():
    """Find the Gaza Coordinates.txt file in various locations"""
    possible_locations = [
        "Gaza Coordinates.txt",
        os.path.join(os.getcwd(), "Gaza Coordinates.txt"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Gaza Coordinates.txt"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Gaza Coordinates.txt"),
        "d:\\collage\\Gaza Before and After\\Gaza Coordinates.txt",
        "d:\\collage\\Gaza Before and After\\satellite-imagery-app\\Gaza Coordinates.txt"
    ]
    
    for loc in possible_locations:
        if os.path.isfile(loc):
            print(f"Found Gaza Coordinates at: {loc}")
            return loc
    
    print("WARNING: Could not find Gaza Coordinates.txt file!")
    return "Gaza Coordinates.txt"  # Return default, which will likely fail

def load_gaza_borders(file_path):
    """
    Reads the Gaza Coordinates file and returns the border points as lists.
    """
    # Make sure the file exists
    if not os.path.isfile(file_path):
        # Try relative path from the current file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, "Gaza Coordinates.txt")
        print(f"Looking for Gaza Coordinates at: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Parse all border coordinates
    north_matches = re.findall(r"north_border\s*=\\s*\[(.*?)\]", content, re.DOTALL)
    south_matches = re.findall(r"south_border\s*=\s*\[(.*?)\]", content, re.DOTALL)
    east_matches = re.findall(r"east_border\s*=\s*\[(.*?)\]", content, re.DOTALL)
    west_matches = re.findall(r"west_border\s*=\s*\[(.*?)\]", content, re.DOTALL)
    
    borders = {
        'north': [],
        'south': [],
        'east': [],
        'west': []
    }
    
    # Extract north border coordinates
    if north_matches:
        matches = re.findall(r"\(\s*([\d\.]+)\s*,\s*([\d\.]+)\s*\)", north_matches[0])
        borders['north'] = [(float(m[0]), float(m[1])) for m in matches]
    
    # Extract south border coordinates
    if south_matches:
        matches = re.findall(r"\(\s*([\d\.]+)\s*,\s*([\d\.]+)\s*\)", south_matches[0])
        borders['south'] = [(float(m[0]), float(m[1])) for m in matches]
    
    # Extract east border coordinates
    if east_matches:
        matches = re.findall(r"\(\s*([\d\.]+)\s*,\s*([\d\.]+)\s*\)", east_matches[0])
        borders['east'] = [(float(m[0]), float(m[1])) for m in matches]
    
    # Extract west border coordinates
    if west_matches:
        matches = re.findall(r"\(\s*([\d\.]+)\s*,\s*([\d\.]+)\s*\)", west_matches[0])
        borders['west'] = [(float(m[0]), float(m[1])) for m in matches]
    
    print(f"Loaded border points - North: {len(borders['north'])}, South: {len(borders['south'])}, East: {len(borders['east'])}, West: {len(borders['west'])}")
    return borders

def create_gaza_polygon(borders):
    """
    Create a polygon from the border coordinates.
    Handles connecting the borders correctly.
    """
    # Combine all points to form a complete polygon
    points = []
    
    # For shapely, we need to create a closed loop in the right order
    
    # Start with west border (south to north)
    if borders['west']:
        print(f"Adding {len(borders['west'])} west border points")
        points.extend(borders['west'])
    
    # North border (west to east)
    if borders['north']:
        print(f"Adding {len(borders['north'])} north border points")
        points.extend(borders['north'])
    
    # East border (north to south)
    if borders['east']:
        print(f"Adding {len(borders['east'])} east border points (reversed)")
        # Use list() to create a copy before reversing
        points.extend(list(reversed(borders['east'])))
    
    # South border (east to west) to close the loop
    if borders['south']:
        print(f"Adding {len(borders['south'])} south border points (reversed)")
        # Use list() to create a copy before reversing
        points.extend(list(reversed(borders['south'])))
    
    # If we have points, create a polygon
    if points:
        try:
            # Debug first and last few points
            print(f"Created polygon with {len(points)} total points")
            for i, point in enumerate(points[:3]):
                print(f"First points {i}: {point}")
            for i, point in enumerate(points[-3:]):
                print(f"Last points {i}: {point}")
            
            # Make sure the polygon is closed (first point = last point)
            if points[0] != points[-1]:
                print("Closing polygon by adding first point at the end")
                points.append(points[0])
                
            # Convert points to (lon, lat) format for Shapely
            shapely_points = [(lon, lat) for lat, lon in points]
            
            polygon = Polygon(shapely_points)
            
            if not polygon.is_valid:
                print("Warning: Created invalid polygon. Using simplified version.")
                polygon = polygon.buffer(0)  # This tries to fix self-intersections
                
            return polygon
        except Exception as e:
            print(f"Error creating polygon: {e}")
            return None
    return None

def get_gaza_bounds():
    """Get the bounding box of Gaza from the coordinates file."""
    try:
        file_path = find_gaza_coordinates_file()
        borders = load_gaza_borders(file_path)
        
        # Combine all points to find min/max
        all_points = borders['north'] + borders['south'] + borders['east'] + borders['west']
        
        # Find min/max lat/lon
        lats = [p[0] for p in all_points]
        lons = [p[1] for p in all_points]
        
        bounds = {
            "min_lat": min(lats),
            "max_lat": max(lats),
            "min_lon": min(lons),
            "max_lon": max(lons)
        }
        
        print(f"Gaza bounds: lat {bounds['min_lat']} to {bounds['max_lat']}, lon {bounds['min_lon']} to {bounds['max_lon']}")
        return bounds
    except Exception as e:
        print(f"Error getting Gaza bounds: {e}")
        # Fallback to hardcoded bounds if there's an error
        return {
            "min_lat": 31.23,
            "max_lat": 31.60,
            "min_lon": 34.20,
            "max_lon": 34.56
        }

def divide_gaza_into_sections(num_sections=150):
    """
    Simple and reliable function to divide Gaza into exactly num_sections parts.
    """
    # Get the bounds of Gaza
    bounds = get_gaza_bounds()
    
    # Calculate dimensions based on aspect ratio
    lat_span = bounds["max_lat"] - bounds["min_lat"]
    lon_span = bounds["max_lon"] - bounds["min_lon"]
    
    # Calculate a grid that gives us exactly the requested number of sections
    # Using aspect ratio to determine rows vs columns
    aspect = lon_span / lat_span
    
    # Start with a square-ish grid
    rows = int(math.sqrt(num_sections / aspect))
    if rows < 1:
        rows = 1
        
    cols = int(num_sections / rows)
    if cols < 1:
        cols = 1
    
    # Adjust to get closer to target
    while rows * cols < num_sections:
        cols += 1
    
    # Final adjustment to match exactly
    if rows * cols > num_sections:
        # Remove excess sections from the end
        excess = (rows * cols) - num_sections
        cols = cols - (excess // rows) - (1 if excess % rows > 0 else 0)
        
        # If we removed too many columns, add one back and handle the difference
        if rows * cols < num_sections:
            cols += 1
    
    print(f"Creating grid with {rows} rows and {cols} columns (total: {rows*cols} sections)")
    
    sections = []
    section_index = 0
    
    # Create grid sections
    for i in range(rows):
        for j in range(cols):
            if section_index >= num_sections:
                break
                
            # Calculate bounds for this grid cell
            min_lat = bounds["min_lat"] + (i / rows) * lat_span
            max_lat = bounds["min_lat"] + ((i + 1) / rows) * lat_span
            min_lon = bounds["min_lon"] + (j / cols) * lon_span
            max_lon = bounds["min_lon"] + ((j + 1) / cols) * lon_span
            
            # Center coordinates
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2
            
            sections.append({
                "id": f"section_{section_index}",
                "bounds": {
                    "min_lat": min_lat,
                    "max_lat": max_lat,
                    "min_lon": max_lon,
                    "max_lon": max_lon
                },
                "center": {
                    "lat": center_lat,
                    "lon": center_lon
                }
            })
            
            section_index += 1
            if section_index >= num_sections:
                break
    
    print(f"Created {len(sections)} sections within Gaza borders")
    return sections

# Keep the existing functions for backward compatibility
def load_gaza_bounds(file_path):
    """Legacy function that returns the outer bounds of Gaza"""
    return get_gaza_bounds()

def divide_region_into_sections(min_lat, max_lat, min_lon, max_lon, num_sections_lat, num_sections_lon):
    """
    Divide the Gaza region into sections, with eastern sections shifted more eastward.
    Section_10 is specifically moved further east.
    """
    print(f"Dividing into {num_sections_lat}x{num_sections_lon} sections")
    
    # Calculate the size of each section
    lat_step = (max_lat - min_lat) / num_sections_lat
    lon_step = (max_lon - min_lon) / num_sections_lon
    
    # Import settings for eastern shift
    from src.config import settings
    eastern_shift = settings.EASTERN_COLUMN_SHIFT if hasattr(settings, 'EASTERN_COLUMN_SHIFT') else 0.0
    
    print(f"Using eastern shift of {eastern_shift} degrees for eastern columns")
    
    sections = []
    section_index = 0
    
    # Create sections from south to north, then west to east
    for i in range(num_sections_lat):
        for j in range(num_sections_lon):
            section_min_lat = min_lat + i * lat_step
            section_max_lat = min_lat + (i + 1) * lat_step
            
            # Apply eastward shift for the eastern column (j=1)
            if j == 1:
                # Special case for section_10 (i=1, j=1)
                if i == 1 and j == 1:  # This condition identifies section_10
                    # Give section_10 a much more significant eastward push (3.0x the normal shift)
                    current_shift = eastern_shift * 3.0
                    print(f"INCREASED eastward shift for section_10: {current_shift} degrees")
                elif i == 0 and j == 1:  # This would be section_1 (just south of section_10)
                    # Also shift the section below section_10 a bit more
                    current_shift = eastern_shift * 1.5
                    print(f"Moderate eastward shift for section_1: {current_shift} degrees")
                else:
                    current_shift = eastern_shift
                
                # Apply the shift to the longitude boundaries
                section_min_lon = min_lon + j * lon_step + current_shift
                section_max_lon = min_lon + (j + 1) * lon_step + current_shift
            else:
                section_min_lon = min_lon + j * lon_step
                section_max_lon = min_lon + (j + 1) * lon_step
            
            # Calculate center coordinates
            center_lat = (section_min_lat + section_max_lat) / 2
            center_lon = (section_min_lon + section_max_lon) / 2
            
            # Create the section
            section_id = f"section_{section_index}"
            
            # For debugging, print the coordinates of section_10
            if section_index == 10:
                print(f"Section 10 coordinates: lat {section_min_lat:.6f}-{section_max_lat:.6f}, lon {section_min_lon:.6f}-{section_max_lon:.6f}")
            
            sections.append({
                "id": section_id,
                "bounds": {
                    "min_lat": section_min_lat,
                    "max_lat": section_max_lat,
                    "min_lon": section_min_lon,
                    "max_lon": section_max_lon
                },
                "center": {
                    "lat": center_lat,
                    "lon": center_lon
                }
            })
            section_index += 1
    
    return sections

def generate_weekly_dates(start_date_str, end_date_str="current"):
    """
    Generate weekly dates between start_date and end_date.
    If end_date is "current", use the current date.
    """
    print(f"Generating dates from {start_date_str} to {end_date_str}")
    
    start_date = dt.strptime(start_date_str, "%Y-%m-%d")
    
    if end_date_str == "current":
        end_date = dt.now()
    else:
        end_date = dt.strptime(end_date_str, "%Y-%m-%d")
    
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(weeks=1)
    
    return dates
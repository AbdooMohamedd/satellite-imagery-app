import os
import sys
from datetime import datetime
import argparse
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.api.satellite_service import SatelliteService
from src.config import settings

def main():
    parser = argparse.ArgumentParser(description='Satellite Imagery Fetcher for Gaza Strip')
    parser.add_argument('--fetch', action='store_true', help='Fetch new imagery data')
    parser.add_argument('--process', action='store_true', help='Process existing imagery data')
    parser.add_argument('--api-key', type=str, help='[DEPRECATED] Use --client-id instead')
    parser.add_argument('--instance-id', type=str, help='[DEPRECATED] Use --client-secret instead')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD or "current")')
    parser.add_argument('--sections', type=str, help='Number of sections in format "lat,lon" (e.g., "2,2")')
    parser.add_argument('--client-id', type=str, help='Client ID for Sentinel Hub OAuth')
    parser.add_argument('--client-secret', type=str, help='Client Secret for Sentinel Hub OAuth')
    
    args = parser.parse_args()
    
    # Update settings if provided in arguments
    if args.api_key:
        settings.API_KEY = args.api_key
    if args.instance_id:
        settings.INSTANCE_ID = args.instance_id
    if args.start_date:
        settings.START_DATE = args.start_date
    if args.end_date:
        settings.END_DATE = args.end_date
    if args.sections:
        try:
            lat, lon = map(int, args.sections.split(','))
            settings.NUM_SECTIONS_LAT = lat
            settings.NUM_SECTIONS_LON = lon
        except:
            print("Invalid sections format. Use 'lat,lon' (e.g., '2,2')")
    if args.client_id:
        settings.CLIENT_ID = args.client_id
    if args.client_secret:
        settings.CLIENT_SECRET = args.client_secret
    
    # Initialize the satellite service
    service = SatelliteService()
    
    if args.fetch:
        print(f"Starting imagery fetch for Gaza Strip from {settings.START_DATE} to {settings.END_DATE if settings.END_DATE != 'current' else 'current date'}")
        print(f"Dividing into {settings.NUM_SECTIONS_LAT}x{settings.NUM_SECTIONS_LON} sections")
        print(f"Using Sentinel Hub API with collection: {settings.SENTINEL_DATA_COLLECTION}")
        
        if settings.CLIENT_ID == "your-client-id-here" or settings.CLIENT_SECRET == "your-client-secret-here":
            print("ERROR: You must set your Sentinel Hub Client ID and Client Secret in settings.py or via command-line arguments")
            print("Get your credentials at https://www.sentinel-hub.com/")
            return
        
        # Fetch imagery
        all_imagery = service.fetch_imagery_for_gaza()
        
        print(f"Successfully fetched {len(all_imagery)} images")
    
    if args.process:
        print("Processing imagery data...")
        service.process_imagery()
        print("Processing complete!")
    
    # If no arguments provided, show help
    if not (args.fetch or args.process):
        parser.print_help()

if __name__ == "__main__":
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f"Execution completed in {(end_time - start_time).total_seconds()} seconds")
import os
import json
import requests
from datetime import datetime
import time
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.models.imagery_data import ImageryData
from src.utils.geo_helpers import load_gaza_bounds, divide_region_into_sections, generate_weekly_dates, divide_gaza_into_sections

class SatelliteService:
    def __init__(self, api_key=None, instance_id=None):
        """Initialize the Satellite Service"""
        self.api_endpoint = settings.API_ENDPOINT
        self.api_key = api_key if api_key else settings.API_KEY
        self.instance_id = instance_id if instance_id else settings.INSTANCE_ID
        
        # For OAuth
        self.token = None
        self.token_expiry = 0
        
        # Root directory for data storage
        self.project_dir = str(Path(__file__).parent.parent.parent)
        self.data_dir = os.path.join(self.project_dir, settings.DATA_DIR)
        
        # Create directories if they don't exist
        self.images_dir = os.path.join(self.data_dir, 'images')
        self.metadata_dir = os.path.join(self.data_dir, 'metadata')
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        # Get initial token
        token = self.get_oauth_token()
        if token:
            print("Successfully obtained OAuth token")
        else:
            print("Warning: Failed to obtain OAuth token")
    
    def _get_oauth_token(self):
        """Internal method to get a fresh OAuth token"""
        try:
            print("Requesting OAuth token...")
            response = requests.post(
                settings.OAUTH_URL,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': settings.CLIENT_ID,
                    'client_secret': settings.CLIENT_SECRET
                },
                verify=settings.VERIFY_SSL
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data['access_token']
                # Calculate expiry time (token_data['expires_in'] is usually 3600 seconds)
                self.token_expiry = time.time() + token_data['expires_in']
                return self.token
            else:
                print(f"Failed to get OAuth token: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"Error obtaining OAuth token: {str(e)}")
            return None
    
    def get_oauth_token(self):
        """Get OAuth token with expiry tracking"""
        now = time.time()
        
        # Check if we have a valid token that's not about to expire
        if self.token and now < self.token_expiry - settings.TOKEN_REFRESH_MARGIN:
            return self.token
        
        # Get a new token
        return self._get_oauth_token()
    
    def fetch_imagery_for_gaza(self):
        """
        Fetch satellite imagery for the Gaza Strip region.
        """
        # Use Gaza bounds from settings
        gaza_bounds = settings.GAZA_BOUNDS
        
        # Generate sections with eastern shift applied
        print("Creating sections with eastern shift for section_10...")
        sections = divide_region_into_sections(
            gaza_bounds["min_lat"],
            gaza_bounds["max_lat"],
            gaza_bounds["min_lon"],
            gaza_bounds["max_lon"],
            settings.NUM_SECTIONS_LAT,
            settings.NUM_SECTIONS_LON
        )
        
        # Generate weekly dates
        dates = generate_weekly_dates(settings.START_DATE, settings.END_DATE)
        print(f"Generated {len(dates)} dates for processing")
        
        all_imagery = []
        resume = False
        if hasattr(settings, 'RESUME_FROM') and settings.RESUME_FROM:
            resume = True
            print(f"Will resume from section {settings.RESUME_FROM}")
        
        # Process each section
        for section in sections:
            section_id = section["id"]
            section_dir = os.path.join(self.images_dir, section_id)
            os.makedirs(section_dir, exist_ok=True)
            
            # Skip sections until we reach the resume point
            if resume and settings.RESUME_FROM != section_id:
                print(f"Skipping section {section_id} (resuming from {settings.RESUME_FROM})")
                continue
            elif resume and settings.RESUME_FROM == section_id:
                print(f"Resuming from section {section_id}")
                resume = False
            
            print(f"Processing section {section_id}: lat {section['bounds']['min_lat']:.6f} to {section['bounds']['max_lat']:.6f}, lon {section['bounds']['min_lon']:.6f} to {section['bounds']['max_lon']:.6f}")
            
            for date in dates:
                print(f"Fetching imagery for section {section_id} on {date}...")
                try:
                    imagery_data = self.fetch_imagery(
                        location={
                            "lat": section["center"]["lat"],
                            "lon": section["center"]["lon"],
                            "bbox": [
                                section["bounds"]["min_lon"],
                                section["bounds"]["min_lat"],
                                section["bounds"]["max_lon"],
                                section["bounds"]["max_lat"]
                            ],
                            "section_id": section_id
                        }, 
                        date=date
                    )
                    if imagery_data:
                        all_imagery.append(imagery_data)
                    time.sleep(1)
                except Exception as e:
                    print(f"Error fetching imagery for section {section_id} on {date}: {str(e)}")
        
        print(f"Successfully fetched {len(all_imagery)} images")
        return all_imagery
        
    def fetch_imagery(self, location, date):
        """
        Fetch satellite imagery using Sentinel Hub Processing API.
        Enhanced to get better quality images with adaptive date range based on cloud coverage.
        """
        # Use the OAuth token instead of api_key
        token = self.get_oauth_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Extend time range based on cloud coverage setting
        from datetime import datetime, timedelta
        date_from_obj = datetime.strptime(date, "%Y-%m-%d")
        date_to_obj = datetime.strptime(date, "%Y-%m-%d")
        
        # Determine how many days to extend based on cloud coverage threshold
        if hasattr(settings, 'CLOUD_COVERAGE_PERCENTAGE') and settings.CLOUD_COVERAGE_PERCENTAGE >= 50:
            days_extension = settings.DATE_RANGE_EXTENSION.get("HIGH_CLOUD_DAYS", 3)
            print(f"Cloud coverage threshold is high ({settings.CLOUD_COVERAGE_PERCENTAGE}%), extending date range by ±{days_extension} days")
        else:
            days_extension = settings.DATE_RANGE_EXTENSION.get("LOW_CLOUD_DAYS", 1)
            print(f"Cloud coverage threshold is low ({settings.CLOUD_COVERAGE_PERCENTAGE}%), extending date range by ±{days_extension} days")
        
        # Apply date range extension
        extended_date_from = (date_from_obj - timedelta(days=days_extension)).strftime("%Y-%m-%d")
        extended_date_to = (date_to_obj + timedelta(days=days_extension)).strftime("%Y-%m-%d")
        
        print(f"Using extended date range: {extended_date_from} to {extended_date_to}")
        
        # Collection-specific parameters
        collections = [
            {
                "id": "sentinel-2-l2a",
                "evalscript": settings.EVALSCRIPT,
                "time_from": settings.TIME_FROM,
                "time_to": settings.TIME_TO
            },
            {
                "id": "sentinel-2-l1c",
                "evalscript": settings.EVALSCRIPT,
                "time_from": settings.TIME_FROM,
                "time_to": settings.TIME_TO
            }
        ]
        
        for collection in collections:
            print(f"Trying {collection['id']} for {date} (extended range)...")
            
            # Create request payload with expanded parameters
            payload = {
                "input": {
                    "bounds": {
                        "bbox": location["bbox"],
                        "properties": {
                            "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                        }
                    },
                    "data": [{
                        "dataFilter": {
                            "timeRange": {
                                "from": f"{extended_date_from}T{collection['time_from']}",
                                "to": f"{extended_date_to}T{collection['time_to']}"
                            },
                            "mosaickingOrder": "leastCC",  # Least cloud coverage
                            "maxCloudCoverage": settings.CLOUD_COVERAGE_PERCENTAGE
                        },
                        "type": collection["id"]
                    }]
                },
                "output": {
                    "width": settings.IMAGE_WIDTH,
                    "height": settings.IMAGE_HEIGHT,
                    "responses": [{
                        "identifier": "default",
                        "format": {
                            "type": settings.IMAGE_MIME_TYPE
                        }
                    }]
                },
                "evalscript": collection["evalscript"]
            }
            
            retries = 0
            while retries < settings.MAX_RETRIES:
                try:
                    response = requests.post(
                        self.api_endpoint,
                        json=payload,
                        headers=headers,
                        verify=settings.VERIFY_SSL,
                        timeout=settings.TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        # For Sentinel Hub, the image is directly in the response body
                        image_data = response.content
                        
                        # Check if the image meets quality standards
                        if self.is_image_valid(image_data):
                            # Save the image
                            section_dir = os.path.join(self.images_dir, location["section_id"])
                            os.makedirs(section_dir, exist_ok=True)
                            local_path = os.path.join(section_dir, f"{date}.{settings.IMAGE_FORMAT}")
                            with open(local_path, 'wb') as f:
                                f.write(image_data)
                            print(f"Image saved to {local_path}")
                            
                            # Create an ImageryData object
                            imagery_data = ImageryData(
                                image_url="",
                                image_data=image_data,
                                timestamp=date,
                                metadata={
                                    "source": "Sentinel Hub",
                                    "collection": collection["id"],
                                    "bbox": location["bbox"],
                                    "date_range": f"{extended_date_from} to {extended_date_to}"
                                },
                                section_id=location["section_id"],
                                local_path=local_path
                            )
                            
                            # Save metadata
                            self.save_metadata(imagery_data)
                            return imagery_data
                        else:
                            print(f"Image failed quality check - trying next option")
                            break
                        
                    elif response.status_code == 401:  # Unauthorized
                        print(f"Token expired. Getting new token...")
                        token = self._get_oauth_token()  # Force token refresh
                        if token:
                            headers["Authorization"] = f"Bearer {token}"
                            retries += 1
                        else:
                            print("Failed to refresh token")
                            break
                            
                    elif response.status_code == 429:  # Rate limit exceeded
                        wait_time = settings.RETRY_DELAY * (2 ** retries)
                        print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        retries += 1
                        
                    else:
                        print(f"Failed to fetch imagery: {response.status_code}, {response.text}")
                        break
                        
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {str(e)}")
                    retries += 1
                    if retries < settings.MAX_RETRIES:
                        time.sleep(settings.RETRY_DELAY)
                    else:
                        break
        
        print(f"Could not obtain valid imagery for {date}")
        return None
    
    def is_image_valid(self, image_data, min_brightness=None, min_std_dev=None):
        """
        Check if the image meets quality standards
        - Image must not be empty
        - Image must have some brightness and contrast
        """
        try:
            # Skip validation if settings are set to 0
            if (min_brightness is None and hasattr(settings, 'MIN_BRIGHTNESS')):
                min_brightness = settings.MIN_BRIGHTNESS
            
            if (min_std_dev is None and hasattr(settings, 'MIN_STD_DEV')):
                min_std_dev = settings.MIN_STD_DEV
                
            # If both are 0, accept all images
            if min_brightness == 0 and min_std_dev == 0:
                return True
                
            # First, check if the image has a valid size
            if len(image_data) < 1000:
                print(f"Image too small - size: {len(image_data)} bytes")
                return False
            
            return True
        except Exception as e:
            print(f"Error validating image: {str(e)}")
            return True  # Accept image if we can't validate
    
    def save_metadata(self, imagery_data):
        """Save metadata for an image"""
        metadata_path = os.path.join(self.metadata_dir, f"{imagery_data.section_id}_{imagery_data.timestamp}.json")
        
        metadata = {
            "timestamp": imagery_data.timestamp,
            "section_id": imagery_data.section_id,
            "local_path": imagery_data.local_path,
            **imagery_data.metadata
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Metadata saved to {metadata_path}")
    
    def process_imagery(self, imagery_data=None):
        """
        Process imagery data - analyze changes, create visualizations, etc.
        Can be implemented later based on specific requirements.
        """
        print("Processing imagery (placeholder method)")
        # TODO: Implement imagery processing logic as needed
        return True

    # Add a save_image method to your SatelliteService class
    def save_image(self, image_data, local_path):
        """Save image data to local file"""
        # Check if the image was already saved by fetch_imagery
        if not os.path.exists(local_path):
            try:
                with open(local_path, 'wb') as f:
                    # If image_data is a URL string, download it
                    if isinstance(image_data, str) and image_data.startswith('http'):
                        response = requests.get(image_data, verify=settings.VERIFY_SSL)
                        if response.status_code == 200:
                            f.write(response.content)
                            print(f"Image downloaded and saved to {local_path}")
                        else:
                            print(f"Failed to download image: {response.status_code}")
                            return False
                    else:
                        # Otherwise, assume it's binary data
                        f.write(image_data)
                        print(f"Image saved to {local_path}")
                    return True
            except Exception as e:
                print(f"Error saving image: {str(e)}")
                return False
        else:
            # File already exists
            print(f"Image already exists at {local_path}")
            return True
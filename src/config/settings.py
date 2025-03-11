# API configuration for Sentinel Hub
CLIENT_ID = "get it from https://apps.sentinel-hub.com/dashboard/#/account/settings"
CLIENT_SECRET = "get it from https://apps.sentinel-hub.com/dashboard/#/account/settings"
API_ENDPOINT = "https://services.sentinel-hub.com/api/v1/process"
API_KEY = CLIENT_SECRET
INSTANCE_ID = CLIENT_ID
OAUTH_URL = "https://services.sentinel-hub.com/oauth/token"

# Authentication settings
TOKEN_REFRESH_MARGIN = 300
VERIFY_SSL = False

# Resume settings - set to None to start fresh or specify a section to resume from
RESUME_FROM = None 

# Sentinel Hub specific settings
SENTINEL_DATA_COLLECTION = "sentinel-2-l2a"

# Time period settings
START_DATE = "2023-01-01"
END_DATE = "current"  

# Division settings - using section_0 as reference and moving northward
NUM_SECTIONS = 20  

# Use 10 vertical sections (northward) and 2 horizontal (east-west)
NUM_SECTIONS_LAT = 10  # Vertical divisions (south to north)
NUM_SECTIONS_LON = 2   # Horizontal divisions (west to east)

# Reference coordinates based on section_0
REFERENCE_SECTION = {
    "min_lat": 31.235845,  
    "min_lon": 34.219500,  
}

# Gaza Strip full boundaries (from Gaza Coordinates.txt)
GAZA_BOUNDS = {
    "min_lat": 31.235845,    # Southernmost point
    "max_lat": 31.594361,    # Northernmost point 
    "min_lon": 34.219500,    # Westernmost point
    "max_lon": 34.558917     # Easternmost point
}

# Eastern shift - pushes eastern sections (including section_10) further east
EASTERN_COLUMN_SHIFT = 0.15  

# Image settings
IMAGE_WIDTH = 2028  
IMAGE_HEIGHT = 1024  
IMAGE_FORMAT = "png"  
IMAGE_MIME_TYPE = f"image/{IMAGE_FORMAT}"

# View angle setting for direct overhead view
VIEW_ANGLE = "NADIR"

VIEW_PARAMS = {
    "viewAngle": VIEW_ANGLE
}

# Storage settings
DATA_DIR = "../data"

# Sentinel Hub specific settings
CLOUD_COVERAGE_PERCENTAGE = 50  

# Date range extension settings based on cloud coverage
# When cloud coverage threshold is high (>= 50%), extend search to these many days before/after
DATE_RANGE_EXTENSION = {
    "HIGH_CLOUD_DAYS": 3,  
    "LOW_CLOUD_DAYS": 1     
}

# Time of day settings - optimal lighting hours
TIME_FROM = "08:00:00Z"
TIME_TO = "17:00:00Z"

# Enhanced EVALSCRIPT for better image quality
EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: ["B04", "B03", "B02", "B08"],
      units: "REFLECTANCE"
    }],
    output: {
      bands: 3,
      sampleType: "AUTO"
    }
  };
}

function evaluatePixel(sample) {
  // Balanced natural color rendering with moderate contrast enhancement
  
  // Reduced gain for less brightness (was 6.5, now 3.0)
  let gain = 3.0;
  
  // Adjusted gamma for more balanced tone (was 0.6, now 0.8)
  let gamma = 0.8;
  
  // Calculate RGB values with gain and gamma correction
  let r = Math.pow(Math.min(sample.B04 * gain, 1), gamma);
  let g = Math.pow(Math.min(sample.B03 * gain, 1), gamma);
  let b = Math.pow(Math.min(sample.B02 * gain, 1), gamma);
  
  // Reduced NIR contribution (was 0.2, now 0.1)
  if (sample.B08) {
    // Mix in NIR to moderately enhance vegetation areas
    r = Math.min(r + sample.B08 * 0.1, 1.0);
    g = Math.min(g + sample.B08 * 0.05, 1.0);
  }

  return [r, g, b];
}
"""

# Image validation settings
MIN_BRIGHTNESS = 0 
MIN_STD_DEV = 0     

# Request settings
TIMEOUT = 180
RETRY_DELAY = 5
MAX_RETRIES = 10
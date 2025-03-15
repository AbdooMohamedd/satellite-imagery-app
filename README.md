# Satellite Imagery Application for Gaza Strip

This repository documents the impact of the ongoing war on the Gaza Strip through satellite imagery analysis. The application fetches and processes satellite images from January 2023 to the present, providing a structured approach for monitoring changes over time.

![Description of GIF](geza_before_after.gif)
# ❌ THIS IS NOT SELF-DEFENSE, THIS IS GENOCIDE ❌

## Features

- **Satellite Image Retrieval**: Fetches high-resolution satellite images from Sentinel-2 (L2A & L1C) and Landsat-8 (L1C) via the Sentinel Hub Processing API and the Planet.com API.
- **Configurable Grid Division**: Segments the Gaza Strip into smaller sections (default 2x2 grid) for enhanced detail.
- **Automated Weekly Snapshots**: Retrieves imagery at weekly intervals for consistent historical comparison.
- **Local Data Storage**: Organizes downloaded images in structured directories along with associated metadata.
- **Image Visualization**: Supports before/after and timeline visualizations to track developments over time.

## Project Structure

```
satellite-imagery-app
├── src
│   ├── main.py               # Application entry point
│   ├── api
│   │   └── satellite_service.py  # Handles API requests for imagery
│   ├── models
│   │   └── imagery_data.py   # Data models for storing imagery information
│   ├── utils
│   │   └── geo_helpers.py    # Utilities for geographic calculations
│   └── config
│       └── settings.py       # Configuration for API keys and parameters
├── tests
│   └── test_satellite_service.py # Unit tests for API requests
├── data
│   ├── images/               # Directory for stored images (categorized by region)
│   └── metadata/             # JSON metadata for fetched images
├── requirements.txt          # Dependencies
└── README.md                 # Documentation
```

## Installation

### 1. Clone the Repository

```sh
git clone https://github.com/AbdooMohamedd/satellite-imagery-app.git
cd satellite-imagery-app
```

### 2. Set Up a Virtual Environment (Recommended)

```sh
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Configure API Credentials

To use Sentinel Hub, visit [Sentinel Hub Dashboard](https://apps.sentinel-hub.com/dashboard/#/account/settings), create a new OAuth client, and retrieve your `CLIENT_ID` and `CLIENT_SECRET`. Add these credentials to `src/config/settings.py`.

## Usage

### Fetching Satellite Imagery

```sh
python src/main.py --fetch
```

This command:

- Retrieves weekly imagery from January 2023 to the present.
- Segments the Gaza Strip into grid sections.
- Saves images in `data/images/` and metadata in `data/metadata/`.

### Processing and Visualization

```sh
python src/main.py --process
```

Creates visual comparisons such as before/after overlays or time-lapse sequences.

### Combining Fetching and Processing

```sh
python src/main.py --fetch --process
```

### Additional Command-Line Options

- `--api-key YOUR_API_KEY` - Provide Sentinel Hub API key.
- `--planet-api-key YOUR_PLANET_API_KEY` - Provide Planet.com API key.
- `--instance-id YOUR_INSTANCE_ID` - Sentinel Hub instance ID.
- `--start-date YYYY-MM-DD` - Set a custom start date.
- `--end-date YYYY-MM-DD` - Define an end date.
- `--sections "lat,lon"` - Adjust the grid division (e.g., "2,2").

## How It Works

1. **Image Acquisition**: The script authenticates with Sentinel Hub and Planet.com, retrieves imagery based on configured parameters, and stores the results.
2. **Storage & Metadata**: Images are saved in organized directories, while metadata (bounding boxes, timestamps, source) is logged for analysis.
3. **Processing & Visualization**: (Optional) Users can generate before/after comparisons or time-lapse animations for visual impact.

## Troubleshooting

- **Dark or Black Images**: Try adjusting the time window in `settings.py`.
- **Rate Limits**: Ensure API subscription permits required usage. The script includes automatic retry mechanisms.

## Contributing

Contributions are welcome! Please submit issues or pull requests for improvements.

## License

This project is licensed under the Apache 2.0 License.


# Satellite Imagery Application for Gaza Strip

This application fetches and processes satellite imagery for the Gaza Strip region from January 2023 to the current date. It divides the region into a configurable grid (by default, a 2×2 grid) and retrieves weekly snapshots for each section. The images are stored locally and can be used for further analysis or visualization.

## Features

- **Fetch Satellite Imagery**: Retrieves daytime images from satellite providers (Sentinel-2 L2A, Sentinel-2 L1C, and Landsat-8 L1C) via the Sentinel Hub Processing API and the Planet.com API.
- **Configurable Grid Division**: Divides the Gaza Strip into sections (default is 2 lat × 2 lon sections) for detailed coverage.
- **Weekly Time Intervals**: Automatically generates weekly dates from January 2023 until the current date.
- **Local Data Storage**: Saves fetched images in section-specific directories and stores corresponding metadata.
- **Optional Visualization**: Create timeline or before/after visualizations of the fetched imagery.

## Project Structure

```
satellite-imagery-app
├── src
│   ├── main.py               # Application entry point
│   ├── api
│   │   └── satellite_service.py  # APIs for fetching and processing satellite imagery
│   ├── models
│   │   └── imagery_data.py   # Data structure for imagery and metadata
│   ├── utils
│   │   └── geo_helpers.py    # Utility functions (date generation, region division, etc.)
│   └── config
│       └── settings.py       # Configuration for API keys, endpoints, and processing parameters
├── tests
│   └── test_satellite_service.py # Unit tests for the API service
├── data
│   ├── images/               # Directory for saved images (organized by section)
│   └── metadata/             # JSON files containing metadata for each fetched image
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Installation

1. **Clone the Repository**

   ```sh
   git clone <repository-url>
   cd satellite-imagery-app
   ```

2. **Set Up a Virtual Environment (Recommended)**

   ```sh
   python -m venv myenv
   ```

   Activate the virtual environment:

   - **Windows:**
     ```sh
     myenv\Scripts\activate
     ```
   - **Unix/MacOS:**
     ```sh
     source myenv/bin/activate
     ```

3. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Configure API Credentials**  
   Edit the `src/config/settings.py` file to update your Sentinel Hub API credentials and your Planet.com API key. You can obtain a Planet API key from [Planet.com](https://www.planet.com/account/#/user-settings).

## Usage

The application provides two primary functionalities: fetching imagery and (optionally) processing/visualizing it.

### Fetching Satellite Imagery

To fetch and save satellite imagery locally, run:

```sh
python src/main.py --fetch
```

This command will:

- Generate weekly dates from January 2023 until the current date.
- Divide the Gaza Strip into a grid (default 2×2).
- For each section and date, attempt to retrieve daylight imagery (using a specified daytime window).
- Save the images in `data/images/<section_id>/` and store metadata in `data/metadata/`.

### Processing and Visualization (Optional)

If you wish to create visualizations (e.g., timelines or before/after comparisons) from the fetched data, run:

```sh
python src/main.py --process
```

You can also combine functionalities:

```sh
python src/main.py --fetch --process
```

### Command-Line Options

The application supports several command-line arguments:

- `--fetch`  
  Fetches new imagery data.
- `--process`  
  Processes the saved imagery (e.g., create visualizations).

- `--api-key YOUR_API_KEY`  
  Supply your Sentinel Hub API key.

- `--planet-api-key YOUR_PLANET_API_KEY`  
  Supply your Planet.com API key.

- `--instance-id YOUR_INSTANCE_ID`  
  Supply your Sentinel Hub instance ID.

- `--start-date YYYY-MM-DD`  
  Override the default start date.

- `--end-date YYYY-MM-DD` or `"current"`  
  Specify the end date.

- `--sections "lat,lon"`  
  Set the number of sections for grid division (e.g., `"2,2"` for a 2×2 grid).

## How It Works

1. **API Interaction:**  
   The application obtains an OAuth token from Sentinel Hub and submits image requests for each section and weekly date. It also utilizes the Planet.com API to fetch additional high-resolution imagery. It uses a defined daytime window (e.g., 10:00–13:00 UTC) to fetch imagery. Multiple satellite collections are supported, falling back if a collection returns insufficient data.

2. **Data Storage:**  
   Fetched images are stored under `data/images/` in section-specific subdirectories. Associated metadata (including source, collection used, bounding box, and time information) is saved under `data/metadata/`.

3. **Image Processing:**  
   (Optionally) Once images are fetched, processing steps can generate visualization timelines or comparative imagery (before/after) for deeper analysis.

## Troubleshooting

- **Dark/Black Images:**  
  If images are too dark or entirely black, consider:

  - Adjusting the daytime time window in the settings.
  - Tweaking the EVALSCRIPT parameters (gain, gamma) in `src/config/settings.py`.
  - Verifying that your API credentials are correct and that the subscription has proper access to the needed datasets.

- **Rate Limiting:**  
  The application implements exponential backoff when encountering rate limit errors. Ensure that your API subscription is adequate for your usage.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions to improve the application, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

# To fetch imagery

```sh
python src/main.py --fetch
```

# To process existing imagery

```sh
python src/main.py --process
```

# To both fetch and process

```sh
python src/main.py --fetch --process
```

# To specify credentials via command line

```sh
python src/main.py --fetch --api-key YOUR_KEY --instance-id YOUR_INSTANCE_ID --planet-api-key YOUR_PLANET_API_KEY
```

## Quick Start Guide

### Prerequisites

1. Install Python 3.8 or higher
2. Install Chrome browser if you don't have it already

### Setup

1. Clone or download this repository to your computer

2. Create a virtual environment and install dependencies:

**Windows**:
```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

**Mac**:
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

3. Modify the `.env` file in the root directory with your API keys (ask Mateo if needed):
```bash
SERPAPI_KEY=your_serp_api_key
FACEBOOK_TOKEN=your_facebook_token
```

### Running the Tool

1. Open terminal/command prompt in the project folder
2. Activate the virtual environment (if not already activated)
3. Run the main project script:
```bash
python src/main.py
```

The script will process the data according to the defined steps and generate output files in the corresponding folders.

## Configuration for Manual Testing in `config.py`

The `config.py` file includes options for performing "manual testing" without relying on the complete input files. This is useful for quickly testing the script with a subset of data.

  # Specific settings for manual testing
    USE_MANUAL_POSTCODES = True  # Set to False to load from file
    MANUAL_POSTCODES = ["AL1", "AL10"]  # Manual postal codes for testing

    USE_MANUAL_CATEGORY = True  # Set to False to load from file or use SPECIFIC_CATEGORY
    MANUAL_CATEGORIES = ["Pest control services"]  # Manual categories for testing 

### How the Configuration Works

- **`USE_MANUAL_POSTCODES`**: If set to `True`, the script will use the postal codes defined in `MANUAL_POSTCODES` instead of loading postal codes from the `postcodes.txt` file. Change this variable to `False` to use the real input file.

- **`MANUAL_POSTCODES`**: A list of postal codes to test the script quickly. You can add or change the values in this list to test different postal codes.

- **`USE_MANUAL_CATEGORY`**: If set to `True`, the script will use the categories defined in `MANUAL_CATEGORIES` instead of loading categories from `categories.txt`. Change this variable to `False` to load all categories from the file.

- **`MANUAL_CATEGORIES`**: A list of categories for quick testing. You can adjust or add categories as needed for testing.

> **Note**: For full execution (without manual testing), make sure `USE_MANUAL_POSTCODES` and `USE_MANUAL_CATEGORY` are set to `False`. This will allow the script to use the complete input files in `data/input`.
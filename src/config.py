from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Specific settings for manual testing
USE_MANUAL_POSTCODES = True  # Set to False to load from file
MANUAL_POSTCODES = ["AL1", "AL10"]  # Manual postcodes for testing

USE_MANUAL_CATEGORY = True  # Set to False to load from file or use SPECIFIC_CATEGORY
MANUAL_CATEGORIES = ["Accounting firm","Accounting school","Accounting Software Company"]

# API Configuration
# SerpAPI
API_KEY = os.getenv('SERPAPI_KEY')
# Facebook token
ACCESS_TOKEN = os.getenv('FACEBOOK_TOKEN')



#######

COUNTRY = " England, United Kingdom"

DATE_90_DAYS_AGO = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
DATE_30_DAYS_AGO = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

# Base directories for organized output
BASE_DIR = "data"
INPUT_DIR = os.path.join(BASE_DIR, "input")
REFERENCE_DIR = os.path.join(BASE_DIR, "reference")
STEPS_DIR = os.path.join(BASE_DIR, "steps")
FINAL_DIR = os.path.join(BASE_DIR, "final")

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(REFERENCE_DIR, exist_ok=True)
os.makedirs(STEPS_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

# Date Configuration
DATE_FORMAT = "%Y%m%d"
TODAY_DATE = datetime.now().strftime(DATE_FORMAT)

# Input Files
POSTCODES_FILE_PATH = os.path.join(INPUT_DIR, "postcodes.txt")
CATEGORIES_FILE_PATH = os.path.join(INPUT_DIR, "categories.txt")

# Function to load postcodes based on the manual setting
def load_postcodes():
    if USE_MANUAL_POSTCODES:
        return MANUAL_POSTCODES
    else:
        with open(POSTCODES_FILE_PATH, 'r') as file:
            return [line.strip() for line in file if line.strip()]

# Function to load categories based on the manual setting
def load_categories():
    if USE_MANUAL_CATEGORY:
        return MANUAL_CATEGORIES
    else:
        with open(CATEGORIES_FILE_PATH, 'r') as file:
            return [line.strip() for line in file if line.strip()]

# Load final lists of postcodes and categories
POSTCODES = load_postcodes()
CATEGORIES = load_categories()

# Reference files paths
COUNTY_REF_PATH = os.path.join(REFERENCE_DIR, "postcodes by county.xlsx")
REGION_REF_PATH = os.path.join(REFERENCE_DIR, "Postcode districts.xlsx")

# Filename helper functions
def get_step_filename(step_number, description):
    # Create a subdirectory in 'steps' for today's date
    dated_step_dir = os.path.join(STEPS_DIR, TODAY_DATE)
    os.makedirs(dated_step_dir, exist_ok=True)  # Ensure the directory exists
    
    # Save the step file in the date-specific directory
    return os.path.join(dated_step_dir, f"STEP_{step_number}_{description}_{TODAY_DATE}.csv")

def get_final_output_filename():
    return os.path.join(FINAL_DIR, f"FINAL_OUTPUT_{TODAY_DATE}.csv")

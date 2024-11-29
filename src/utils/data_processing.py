#utils/data_processing.py

import re
import pandas as pd

def extract_root_domain(url):
    try:
        return re.sub(r'^(https?://)?(www\.)?', '', url).split('/')[0]
    except TypeError:
        return 'No URL found'

def filter_by_postcode(row):
    postcode = row['Postcode']
    location = str(row['Location'])
    pattern = r'\b' + re.escape(postcode) + r'\b'
    return re.search(pattern, location) is not None

def extract_postcode(location):
    match = re.search(r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s\d[A-Z]{2}\b', location)
    if match:
        return match.group(0)
    return None

from urllib.parse import urlparse

def get_root_domain(url):
    """Extracts the root domain from a URL."""
    try:
        if isinstance(url, str):
            return urlparse(url).netloc
        else:
            return 'No URL found'
    except Exception as e:
        print(f"Error parsing URL: {e}")
        return 'Error'

def process_branch_data(df):
    """Process branch data to add 'Root Domain' and 'Number of Branches'."""
    # Check if 'Number_of_branches' column exists; if not, initialize it
    if 'Number_of_branches' not in df.columns:
        df.loc[:, 'Number_of_branches'] = 1

    # Ensure the 'URL' column exists before proceeding
    if 'URL' in df.columns:
        # Extract root domain from the 'URL' column
        df.loc[:, 'Root Domain'] = df['URL'].apply(get_root_domain).str.replace("www.", "", regex=False)
    else:
        print("Column 'URL' not found in DataFrame. Cannot extract root domains.")
        df.loc[:, 'Root Domain'] = 'No URL found'  # Fallback in case URL column doesn't exist

    # Fill NaN values for 'Number_of_branches'
    df.loc[:, 'Number_of_branches'] = df['Number_of_branches'].fillna(1)

    # Sort the DataFrame
    df.sort_values(by=['Postcode', 'Company Name', 'Location'], ascending=[True, True, True], inplace=True)

    # Group by 'Company Name' to sum branches
    df.loc[:, 'sum_branches'] = df.groupby('Company Name')['Number_of_branches'].transform('sum')

    # Drop duplicate company names, keeping the first occurrence
    df.drop_duplicates(subset='Company Name', keep='first', inplace=True)

    # Update 'Number_of_branches' with the total number of branches
    df.loc[:, 'Number_of_branches'] = df['sum_branches']

    # Drop the temporary column 'sum_branches'
    df.drop(columns='sum_branches', inplace=True)

    return df
#steps/load_data.py

import os
import pandas as pd
from tqdm import tqdm
from utils.file_operations import save_to_csv
from utils.google_maps import search_google_maps, get_serpapi_location
import config

def load_or_create_combined_data():
    combined_data_path = config.get_step_filename(0, "initial_combined_data")

    if os.path.exists(combined_data_path):
        print("Loaded existing combined data from STEP 0")
        return pd.read_csv(combined_data_path)

    print("Creating new initial combined data from postcodes and categories")
    df_combined = pd.DataFrame(columns=['Postcode', 'Location', 'Company Name', 'Phone', 'URL', 'Category'])
    for post_code in tqdm(config.POSTCODES, desc='Processing Postcodes', unit='postcode'):
        for category in tqdm(config.CATEGORIES, desc='Processing Categories', leave=False):
            coordinates = get_serpapi_location(f"{post_code}, {config.COUNTRY}")
            if coordinates:
                search_data = search_google_maps(post_code, coordinates, category, config.API_KEY)
                temp_df = pd.DataFrame(search_data, columns=['Postcode', 'Location', 'Company Name', 'Phone', 'URL'])
                temp_df['Category'] = category
                df_combined = pd.concat([df_combined, temp_df], ignore_index=True)

    save_to_csv(df_combined, combined_data_path)
    return df_combined

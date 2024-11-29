# steps/process_steps.py

import os
import pandas as pd
from steps.save_and_resume import apply_step
from processors.google_ads import process_google_ads
from processors.facebook_ads import add_facebook_ads_data
from processors.legal_names import process_legal_names
from processors.postcode_processing import add_county_region_columns
from utils.data_processing import filter_by_postcode, process_branch_data
from processors.email_extraction import add_email_data
import config

def apply_all_steps(df_combined, starting_step=0):
    steps = [
        (1, "filtered_postcodes", lambda df: df[df.apply(filter_by_postcode, axis=1)]),
        (2, "county_region_added", add_county_region_columns),
        (3, "branch_data_processed", process_branch_data),
        (4, "email_data_added", add_email_data),
        (5, "google_ads_30d", lambda df: process_google_ads(df, days=30)),
        (6, "google_ads_90d", lambda df: process_google_ads(df, days=90)),
        (7, "legal_names_processed", process_legal_names),
        (8, "facebook_ads_data_added", add_facebook_ads_data),
    ]

    for step_number, description, function in steps:
        # Verificar si el archivo del paso ya existe
        step_filename = config.get_step_filename(step_number, description)
        if step_number > starting_step:
            if os.path.exists(step_filename):
                print(f"STEP {step_number} already completed, loading existing data...")
                df_combined = pd.read_csv(step_filename)
            else:
                df_combined = apply_step(df_combined, step_number, description, function)

    return df_combined

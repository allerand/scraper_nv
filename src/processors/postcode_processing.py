#processors/postcode_processing.py

import pandas as pd
import config

# Load county and region reference data
county_ref = pd.read_excel(config.COUNTY_REF_PATH, header=1).drop(0)
region_ref = pd.read_excel(config.REGION_REF_PATH)
region_ref.set_index('Postcode', inplace=True)

# Function to find county by postcode
def find_county(postcode, ref_df):
    for idx, row in ref_df.iterrows():
        postcode_list = row['Postcode areas in County'].split(', ')
        if postcode in postcode_list:
            return row['County']
    return None

# Function to add County, Town/Area, and Region columns
def add_county_region_columns(df_combined):
    df = df_combined.copy()
    
    if 'County' not in df.columns:
        df.loc[:, 'County'] = pd.NA
    if 'Town/Area' not in df.columns:
        df.loc[:, 'Town/Area'] = pd.NA
    if 'Region' not in df.columns:
        df.loc[:, 'Region'] = pd.NA

    mask_county = df['County'].isna()
    df.loc[mask_county, 'County'] = df.loc[mask_county, 'Postcode'].apply(lambda x: find_county(x, county_ref))

    mask_town_area = df['Town/Area'].isna()
    mask_region = df['Region'].isna()
    
    df.loc[mask_town_area, 'Town/Area'] = df.loc[mask_town_area, 'Postcode'].map(region_ref['Town/Area'])
    df.loc[mask_region, 'Region'] = df.loc[mask_region, 'Postcode'].map(region_ref['Region'])
    
    return df
